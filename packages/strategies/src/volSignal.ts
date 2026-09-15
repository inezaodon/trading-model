import { mean } from "./math.js";
import type { PathBundle, SurfaceSummary, VolSignalResult } from "./types.js";

export interface VolSignalOptions {
  /** Relative edge threshold before emitting a non-zero direction. Default 0.05 (5%). */
  threshold?: number;
}

/**
 * Compare model / realized variance on simulated paths vs market iv30².
 *
 * edge > 0 → model richer than market → short-vol bias
 * edge < 0 → model cheaper than market → long-vol bias
 */
export function volatilitySignal(
  paths: PathBundle,
  surface: SurfaceSummary,
  options: VolSignalOptions = {},
): VolSignalResult {
  const threshold = options.threshold ?? 0.05;
  const marketIv = surface.iv30;
  const marketImpliedVariance = marketIv * marketIv;

  const allV: number[] = [];
  const realizedPieces: number[] = [];

  for (const path of paths.paths) {
    for (const v of path.v) allV.push(v);

    const S = path.S;
    const times = paths.times;
    if (S.length < 2) continue;

    let qv = 0;
    for (let i = 1; i < S.length; i++) {
      const prev = S[i - 1]!;
      const curr = S[i]!;
      if (prev > 0 && curr > 0) {
        const r = Math.log(curr / prev);
        qv += r * r;
      }
    }
    const T = times[times.length - 1]! - times[0]!;
    // Annualize quadratic variation
    realizedPieces.push(T > 1e-12 ? qv / T : qv);
  }

  const modelVariance = mean(allV);
  const realizedVariance = mean(realizedPieces);
  const modelRef = 0.5 * (modelVariance + realizedVariance);

  const denom = Math.max(marketImpliedVariance, 1e-12);
  const edge = (modelRef - marketImpliedVariance) / denom;

  let direction: -1 | 0 | 1 = 0;
  if (edge > threshold) direction = -1; // short vol
  else if (edge < -threshold) direction = 1; // long vol

  return {
    marketImpliedVariance,
    modelVariance,
    realizedVariance,
    edge,
    direction,
  };
}
