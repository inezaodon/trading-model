import { marketAgent } from "./market-agent.js";
import { mathAgent } from "./math-agent.js";
import { reportAgent } from "./report-agent.js";
import { strategyAgent } from "./strategy-agent.js";
import type { AgentDefinition } from "../types.js";

export { marketAgent } from "./market-agent.js";
export { mathAgent } from "./math-agent.js";
export { strategyAgent } from "./strategy-agent.js";
export { reportAgent } from "./report-agent.js";

/** Built-in agents shipped with the orchestrator. */
export const builtinAgents: AgentDefinition[] = [
  marketAgent,
  mathAgent,
  strategyAgent,
  reportAgent,
];

/** Default sequential pipeline for `full-pipeline`. */
export const FULL_PIPELINE: string[] = [
  "market-agent",
  "math-agent",
  "strategy-agent",
  "report-agent",
];
