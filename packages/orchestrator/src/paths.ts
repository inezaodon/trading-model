import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Walk upward from a start directory until package.json with name "trading-model" is found.
 */
export function findRepoRoot(startDir: string = process.cwd()): string {
  let dir = path.resolve(startDir);
  for (;;) {
    const pkgPath = path.join(dir, "package.json");
    if (fs.existsSync(pkgPath)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf8")) as {
          name?: string;
          workspaces?: unknown;
        };
        if (pkg.name === "trading-model" || Array.isArray(pkg.workspaces)) {
          return dir;
        }
      } catch {
        /* continue */
      }
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }

  // Fallback: packages/orchestrator/dist -> ../../..
  const fromDist = path.resolve(__dirname, "../../..");
  if (fs.existsSync(path.join(fromDist, "package.json"))) {
    return fromDist;
  }
  return process.cwd();
}

export function ensureArtifactsDir(repoRoot: string, artifactsDir?: string): string {
  const dir = artifactsDir
    ? path.isAbsolute(artifactsDir)
      ? artifactsDir
      : path.join(repoRoot, artifactsDir)
    : path.join(repoRoot, "artifacts");
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

export function marketDataCli(repoRoot: string): string {
  return path.join(repoRoot, "packages/market-data/dist/cli.js");
}

export function strategiesCli(repoRoot: string): string {
  return path.join(repoRoot, "packages/strategies/dist/cli.js");
}

export function coreMathDir(repoRoot: string): string {
  return path.join(repoRoot, "packages/core-math");
}

export function fileExists(p: string): boolean {
  try {
    return fs.existsSync(p) && fs.statSync(p).isFile();
  } catch {
    return false;
  }
}

export function dirExists(p: string): boolean {
  try {
    return fs.existsSync(p) && fs.statSync(p).isDirectory();
  } catch {
    return false;
  }
}
