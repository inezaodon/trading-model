import type { AgentName } from "./types.js";

const COLORS = {
  reset: "\x1b[0m",
  dim: "\x1b[2m",
  cyan: "\x1b[36m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  red: "\x1b[31m",
  teal: "\x1b[38;5;37m",
} as const;

function stamp(): string {
  return new Date().toISOString().slice(11, 23);
}

export function logAgent(
  agent: AgentName,
  level: "info" | "ok" | "warn" | "error",
  message: string,
): void {
  const color =
    level === "ok"
      ? COLORS.green
      : level === "warn"
        ? COLORS.yellow
        : level === "error"
          ? COLORS.red
          : COLORS.teal;
  const tag = `[${agent}]`.padEnd(18);
  console.log(
    `${COLORS.dim}${stamp()}${COLORS.reset} ${color}${tag}${COLORS.reset} ${message}`,
  );
}

export function logPipeline(message: string): void {
  console.log(
    `${COLORS.dim}${stamp()}${COLORS.reset} ${COLORS.cyan}[orchestrator]${COLORS.reset} ${message}`,
  );
}
