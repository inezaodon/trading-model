export type {
  AgentContext,
  AgentDefinition,
  AgentName,
  AgentResult,
  BacktestArtifact,
  PathsArtifact,
  PipelineArgs,
  ReportArtifact,
  SurfaceArtifact,
} from "./types.js";

export { AgentRegistry, createDefaultRegistry } from "./registry.js";
export {
  createOrchestratorRegistry,
  runPipeline,
  type PipelineRunResult,
  type RunPipelineOptions,
} from "./runner.js";
export {
  builtinAgents,
  FULL_PIPELINE,
  marketAgent,
  mathAgent,
  strategyAgent,
  reportAgent,
} from "./agents/index.js";
export {
  findRepoRoot,
  ensureArtifactsDir,
  marketDataCli,
  strategiesCli,
  coreMathDir,
} from "./paths.js";
export { parseArgs, printHelp, type CliFlags } from "./args.js";
