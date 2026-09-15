"""Truncated path signatures (Chen series / iterated integrals).

For a path X: [0,T] → R^d the signature is

    S(X)_{0,T} = (1, ∫ dX, ∫∫ dX⊗dX, …)

Truncation at level L yields a finite feature map used in signature volatility
models and ML regime hooks (Cuchiero et al., Friz et al.).

This module implements a discrete Chen–Stratonovich-style signature via
iterated trapezoidal / left-point products on increments — suitable for
light level-2/3 feature extraction on (log-S, variance) paths.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _path_increments(path: np.ndarray) -> np.ndarray:
    """path shape (T, d) → increments (T-1, d)."""
    path = np.asarray(path, dtype=float)
    if path.ndim == 1:
        path = path.reshape(-1, 1)
    if path.shape[0] < 2:
        raise ValueError("path must have at least two time points")
    return np.diff(path, axis=0)


def truncated_signature(
    path: np.ndarray,
    level: int = 2,
    include_time: bool = False,
) -> np.ndarray:
    """Compute a truncated signature feature vector (flattened).

    Parameters
    ----------
    path :
        Array of shape ``(T,)`` or ``(T, d)``.
    level :
        Truncation depth (1, 2, or 3 recommended).
    include_time :
        If True, prepend a normalized time coordinate so the path is in R^{d+1}.

    Returns
    -------
    np.ndarray
        Flat vector ``[level-1 terms | level-2 | … | level-L]`` (no leading 1).
        Level-1 is the total increment; higher levels are iterated products of
        increments (discrete Chen identity / left-point approximation).
    """
    if level < 1 or level > 5:
        raise ValueError("level must be in 1..5 for this light implementation")

    path = np.asarray(path, dtype=float)
    if path.ndim == 1:
        path = path.reshape(-1, 1)
    if include_time:
        t = np.linspace(0.0, 1.0, path.shape[0]).reshape(-1, 1)
        path = np.concatenate([t, path], axis=1)

    dx = _path_increments(path)  # (n, d)
    d = dx.shape[1]

    features: list[np.ndarray] = []

    # Level 1: ∫ dX ≈ Σ ΔX
    level1 = dx.sum(axis=0)
    features.append(level1)

    if level >= 2:
        # Level 2: ∫∫ dX_i ⊗ dX_j ≈ Σ_{s<t} ΔX_s^i ΔX_t^j + ½ Σ_t ΔX_t^i ΔX_t^j
        # Efficient running-prefix form:
        prefix = np.zeros(d, dtype=float)
        level2 = np.zeros((d, d), dtype=float)
        for inc in dx:
            # cross terms with past + half diagonal (Stratonovich-ish)
            level2 += np.outer(prefix, inc)
            level2 += 0.5 * np.outer(inc, inc)
            prefix += inc
        features.append(level2.ravel())

    if level >= 3:
        # Level 3 via iterated prefix tensors (O(n d^3))
        # S^3_{ijk} ≈ Σ (prefix2_{ij} + ½ prefix_i ΔX_j + …) — use Horner-style
        # discrete Chen: maintain signature up to level 2 and multiply by exp(ΔX).
        # For light features we use:
        #   Σ_{r≤s≤t} ΔX_r ⊗ ΔX_s ⊗ ΔX_t  with diagonal 1/6 corrections omitted
        #   for speed (still informative for ML hooks).
        prefix = np.zeros(d, dtype=float)
        prefix2 = np.zeros((d, d), dtype=float)
        level3 = np.zeros((d, d, d), dtype=float)
        for inc in dx:
            # level3 += prefix2 ⊗ inc + prefix ⊗ (½ inc⊗inc) + (1/6) inc⊗inc⊗inc
            level3 += np.einsum("ij,k->ijk", prefix2, inc)
            level3 += 0.5 * np.einsum("i,j,k->ijk", prefix, inc, inc)
            level3 += (1.0 / 6.0) * np.einsum("i,j,k->ijk", inc, inc, inc)
            # update lower signatures
            prefix2 += np.outer(prefix, inc) + 0.5 * np.outer(inc, inc)
            prefix += inc
        features.append(level3.ravel())

    if level >= 4:
        # Higher levels: recursive free-algebra multiplication by exp(ΔX) truncated
        sig = _signature_via_chen(dx, level)
        return sig

    return np.concatenate(features, axis=0)


def _signature_via_chen(dx: np.ndarray, level: int) -> np.ndarray:
    """Chen recursive signature truncated at ``level`` (flattened, no unit)."""
    d = dx.shape[1]
    # Represent truncated signature as list of tensors by depth
    # S = [S1, S2, ..., Slevel]
    dims = [d**k for k in range(1, level + 1)]
    S = [np.zeros(dim, dtype=float) for dim in dims]

    for inc in dx:
        # Compute Δ = exp(inc) truncated: depth-k = inc^{\otimes k} / k!
        delta: list[np.ndarray] = []
        tensor = inc.copy()
        fact = 1.0
        for k in range(1, level + 1):
            if k > 1:
                fact *= k
                tensor = np.kron(tensor, inc)
            delta.append(tensor / fact)

        # Chen product: S_new = S ⊗ Δ  (truncated)
        # New depth-m component = Σ_{i+j=m} S_i ⊗ Δ_j  (+ Δ_m)
        new_S = [np.zeros_like(s) for s in S]
        for m in range(1, level + 1):
            acc = delta[m - 1].copy()
            for i in range(1, m):
                j = m - i
                acc = acc + np.kron(S[i - 1], delta[j - 1])
            new_S[m - 1] = acc
        S = new_S

    return np.concatenate(S, axis=0)


def signature_features_from_sv_path(
    s: np.ndarray,
    v: np.ndarray | None = None,
    level: int = 2,
    use_log_s: bool = True,
) -> np.ndarray:
    """Build signature features from a single spot (and optional variance) path.

    Parameters
    ----------
    s :
        Spot path shape ``(T,)``.
    v :
        Optional variance path ``(T,)``; stacked as second channel.
    """
    s = np.asarray(s, dtype=float).ravel()
    channel = np.log(s) if use_log_s else s
    if v is None:
        path = channel.reshape(-1, 1)
    else:
        v = np.asarray(v, dtype=float).ravel()
        if v.shape != channel.shape:
            raise ValueError("s and v must have the same length")
        path = np.column_stack([channel, v])
    return truncated_signature(path, level=level, include_time=True)


def batch_signature_features(
    paths_s: np.ndarray,
    paths_v: np.ndarray | None = None,
    level: int = 2,
) -> np.ndarray:
    """Compute signature features for a batch of paths.

    Parameters
    ----------
    paths_s :
        Shape ``(n_paths, T)``.
    paths_v :
        Optional shape ``(n_paths, T)``.

    Returns
    -------
    np.ndarray
        Shape ``(n_paths, feature_dim)``.
    """
    paths_s = np.asarray(paths_s, dtype=float)
    n = paths_s.shape[0]
    feats = []
    for i in range(n):
        v_i = None if paths_v is None else paths_v[i]
        feats.append(signature_features_from_sv_path(paths_s[i], v_i, level=level))
    return np.vstack(feats)


def signature_feature_dict(
    s: np.ndarray,
    v: np.ndarray | None = None,
    level: int = 2,
) -> dict[str, Any]:
    """JSON-serializable signature payload for CLI / artifacts."""
    feat = signature_features_from_sv_path(s, v, level=level)
    return {
        "level": level,
        "dim": int(feat.size),
        "features": feat.tolist(),
    }
