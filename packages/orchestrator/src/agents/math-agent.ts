import fs from "node:fs/promises";
import path from "node:path";
import { logAgent } from "../logger.js";
import { coreMathDir, dirExists, fileExists } from "../paths.js";
import { runCommandOrThrow } from "../spawn.js";
import type {
  AgentContext,
  AgentDefinition,
  AgentResult,
  PathsArtifact,
  SurfaceArtifact,
} from "../types.js";

function hasPythonPackage(mathDir: string): boolean {
  return (
    fileExists(path.join(mathDir, "pyproject.toml")) ||
    fileExists(path.join(mathDir, "setup.py")) ||
    dirExists(path.join(mathDir, "trading_model_math")) ||
    dirExists(path.join(mathDir, "src", "trading_model_math"))
  );
}

async function readSurface(surfacePath: string): Promise<SurfaceArtifact | null> {
  try {
    const raw = await fs.readFile(surfacePath, "utf8");
    return JSON.parse(raw) as SurfaceArtifact;
  } catch {
    return null;
  }
}

/** Normalize nested market-data surface or flat summary. */
export function surfaceParams(surface: SurfaceArtifact | null): {
  symbol: string;
  s0: number;
  iv30: number;
  iv60: number;
  iv90: number;
  slope: number;
} {
  const nested = surface?.surface;
  return {
    symbol: (surface?.symbol || nested?.ticker || "QQQ").toUpperCase(),
    s0: surface?.spot ?? nested?.stockpx ?? 100,
    iv30: surface?.iv30 ?? nested?.iv30 ?? 0.2,
    iv60: surface?.iv60 ?? nested?.iv60 ?? 0.21,
    iv90: surface?.iv90 ?? nested?.iv90 ?? 0.22,
    slope: surface?.slope ?? nested?.slope ?? -1.5,
  };
}

/** Placeholder path bundle matching core-math schema when Python is unavailable. */
function placeholderPaths(symbol: string, surface: SurfaceArtifact | null): PathsArtifact {
  const p = surfaceParams(surface);
  const nSteps = 64;
  const dt = 1 / 252;
  const S0 = p.s0;
  const v0 = p.iv30 ** 2;
  const S: number[] = [S0];
  const v: number[] = [v0];
  const times: number[] = [0];

  let spot = S0;
  let variance = v0;
  for (let i = 1; i <= nSteps; i++) {
    const shock = Math.sin(i * 0.37) * 0.01;
    const volShock = Math.cos(i * 0.21) * 0.002;
    variance = Math.max(
      1e-6,
      variance + 2.0 * (0.04 - variance) * dt + 0.3 * Math.sqrt(Math.max(variance, 0)) * volShock,
    );
    spot = spot * Math.exp(-0.5 * variance * dt + Math.sqrt(variance * dt) * shock * 10);
    S.push(spot);
    v.push(variance);
    times.push(i * dt);
  }

  return {
    model: "heston-placeholder",
    symbol: symbol.toUpperCase(),
    params: { v0, kappa: 2, theta: 0.04, xi: 0.3, rho: -0.7 },
    times,
    paths: [{ S, v }],
    nPaths: 1,
    nSteps,
    dt,
    spot: S,
    variance: v,
    mock: true,
    warning:
      "Python trading_model_math package missing — wrote placeholder paths. Install packages/core-math for real SDEs.",
  };
}

async function runMathAgent(ctx: AgentContext): Promise<AgentResult> {
  const started = Date.now();
  const outPath = path.join(ctx.artifactsDir, "paths.json");
  const surfacePath =
    ctx.outputs.surface ?? path.join(ctx.artifactsDir, "surface.json");
  const mathDir = coreMathDir(ctx.repoRoot);

  try {
    const useCli = !ctx.mock && hasPythonPackage(mathDir);
    const surface = await readSurface(surfacePath);
    const p = surfaceParams(surface);

    if (useCli) {
      logAgent(
        "math-agent",
        "info",
        `Running python3 -m trading_model_math simulate-heston → ${outPath}`,
      );
      const pythonPath = [
        mathDir,
        path.join(mathDir, "src"),
        process.env.PYTHONPATH ?? "",
      ]
        .filter(Boolean)
        .join(path.delimiter);

      try {
        // Optional calibrate → feed s0/v0 from surface IVs
        let v0 = p.iv30 ** 2;
        let theta = p.iv90 ** 2;
        try {
          const cal = await runCommandOrThrow(
            "python3",
            [
              "-m",
              "trading_model_math",
              "calibrate",
              "--iv30",
              String(p.iv30),
              "--iv60",
              String(p.iv60),
              "--iv90",
              String(p.iv90),
              "--slope",
              String(p.slope),
              "--s0",
              String(p.s0),
            ],
            { cwd: mathDir, env: { PYTHONPATH: pythonPath } },
          );
          const calibrated = JSON.parse(cal.stdout) as {
            heston?: { v0?: number; theta?: number };
          };
          if (calibrated.heston?.v0 != null) v0 = calibrated.heston.v0;
          if (calibrated.heston?.theta != null) theta = calibrated.heston.theta;
        } catch {
          logAgent("math-agent", "warn", "calibrate step skipped; using IV² defaults");
        }

        await runCommandOrThrow(
          "python3",
          [
            "-m",
            "trading_model_math",
            "simulate-heston",
            "--symbol",
            ctx.symbol,
            "--s0",
            String(p.s0),
            "--v0",
            String(v0),
            "--theta",
            String(theta),
            "--rho",
            "-0.7",
            "--n-steps",
            "64",
            "--n-paths",
            "4",
            "--seed",
            "42",
            "--out",
            outPath,
          ],
          { cwd: mathDir, env: { PYTHONPATH: pythonPath } },
        );
        logAgent("math-agent", "ok", `Wrote ${outPath}`);
        return {
          agent: "math-agent",
          ok: true,
          outputs: { paths: outPath },
          durationMs: Date.now() - started,
        };
      } catch (cliErr) {
        const msg = cliErr instanceof Error ? cliErr.message : String(cliErr);
        logAgent(
          "math-agent",
          "warn",
          `Python CLI failed (${msg.split("\n")[0]}); falling back to placeholder paths`,
        );
      }
    } else if (!ctx.mock) {
      logAgent(
        "math-agent",
        "warn",
        `core-math package missing or incomplete at ${mathDir}; generating placeholder paths`,
      );
    } else {
      logAgent("math-agent", "info", "Mock mode — generating placeholder paths");
    }

    const paths = placeholderPaths(ctx.symbol, surface);
    await fs.writeFile(outPath, JSON.stringify(paths, null, 2) + "\n", "utf8");
    logAgent("math-agent", "ok", `Wrote placeholder ${outPath}`);
    return {
      agent: "math-agent",
      ok: true,
      outputs: { paths: outPath },
      warning: paths.warning,
      durationMs: Date.now() - started,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    logAgent("math-agent", "error", message);
    return {
      agent: "math-agent",
      ok: false,
      outputs: {},
      error: message,
      durationMs: Date.now() - started,
    };
  }
}

export const mathAgent: AgentDefinition = {
  name: "math-agent",
  description: "Simulate Heston / rough Bergomi paths → artifacts/paths.json",
  run: runMathAgent,
};
