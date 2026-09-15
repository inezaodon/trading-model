"""Simple symmetric random walk and Donsker scaling to Brownian motion.

Let \\(\\xi_i\\) be i.i.d. with \\(P(\\xi=\\pm 1)=1/2\\). The simple random walk is

    S_k = \\xi_1 + \\cdots + \\xi_k,\\quad S_0 = 0.

Donsker's theorem: the linearly interpolated, scaled process

    X^{(n)}_t = n^{-1/2} S_{\\lfloor n t \\rfloor}

converges in law (in C[0,1] with the uniform topology) to a standard Wiener
process as \\(n \\to \\infty\\). This module builds discrete walks and their
scaled continuous-time embeddings for visualization of the BM limit.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def simulate_simple_random_walk(
    n_steps: int = 1000,
    n_paths: int = 1,
    p: float = 0.5,
    seed: int | None = None,
) -> dict[str, Any]:
    """Simulate a 1D simple random walk on the integers.

    Parameters
    ----------
    n_steps :
        Number of steps (path length ``n_steps + 1`` including origin).
    n_paths :
        Independent walks.
    p :
        Probability of a +1 step (``1-p`` for −1). Default 0.5 (symmetric).
    seed :
        RNG seed.

    Returns
    -------
    dict
        ``steps`` (0..n_steps), ``S`` (n_paths, n_steps+1), ``params``.
    """
    if n_steps < 1 or n_paths < 1:
        raise ValueError("n_steps and n_paths must be >= 1")
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1]")

    rng = np.random.default_rng(seed)
    steps = np.arange(n_steps + 1)
    u = rng.random((n_paths, n_steps))
    xi = np.where(u < p, 1.0, -1.0)
    s = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(xi, axis=1)], axis=1)
    return {
        "steps": steps,
        "S": s,
        "kind": "simple_random_walk",
        "params": {"n_steps": n_steps, "n_paths": n_paths, "p": p, "seed": seed},
    }


def random_walk_to_bm_limit(
    n_steps: int = 1000,
    n_paths: int = 1,
    t: float = 1.0,
    p: float = 0.5,
    seed: int | None = None,
) -> dict[str, Any]:
    """Embed a simple random walk as a scaled process converging to BM.

    Uses the Donsker scaling

        X_t = S_{⌊n u⌋} / √n ,   u = t / T

    on the grid ``u_k = k/n``, mapped to physical time ``times = u * t``.

    For the symmetric walk (p=0.5), Var(ξ)=1 so the limit is standard Wiener.
    For biased walks the drift is visible; callers should prefer p=0.5 for the
    classical BM limit demo.
    """
    walk = simulate_simple_random_walk(
        n_steps=n_steps, n_paths=n_paths, p=p, seed=seed
    )
    s = walk["S"]
    # Physical time grid: k/n * t for k = 0..n
    times = (np.arange(n_steps + 1, dtype=float) / n_steps) * t
    # Scale by √(step count) so time-1 variance → 1 for p=0.5
    x = s / np.sqrt(n_steps)
    return {
        "times": times,
        "X": x,
        "S": s,
        "kind": "random_walk_bm_limit",
        "dim": 1,
        "params": {
            "n_steps": n_steps,
            "n_paths": n_paths,
            "t": t,
            "p": p,
            "seed": seed,
            "scaling": "S_k / sqrt(n)",
        },
    }


def simulate_random_walk_2d(
    n_steps: int = 1000,
    n_paths: int = 1,
    seed: int | None = None,
) -> dict[str, Any]:
    """2D lattice random walk: each step is one of (±1,0) or (0,±1) equally.

    Useful for planar trajectory demos before continuous BM.
    """
    if n_steps < 1 or n_paths < 1:
        raise ValueError("n_steps and n_paths must be >= 1")

    rng = np.random.default_rng(seed)
    # directions: E, W, N, S
    dirs = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]])
    choice = rng.integers(0, 4, size=(n_paths, n_steps))
    increments = dirs[choice]  # (n_paths, n_steps, 2)
    path = np.concatenate(
        [np.zeros((n_paths, 1, 2)), np.cumsum(increments, axis=1)],
        axis=1,
    )
    steps = np.arange(n_steps + 1)
    return {
        "steps": steps,
        "X": path[:, :, 0],
        "Y": path[:, :, 1],
        "kind": "simple_random_walk_2d",
        "dim": 2,
        "params": {"n_steps": n_steps, "n_paths": n_paths, "seed": seed},
    }
