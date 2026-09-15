import { FULL_PIPELINE, builtinAgents } from "./agents/index.js";
import { logAgent, logPipeline } from "./logger.js";
import { ensureArtifactsDir, findRepoRoot } from "./paths.js";
import { AgentRegistry, createDefaultRegistry } from "./registry.js";
import type {
  AgentContext,
  AgentDefinition,
  AgentResult,
  PipelineArgs,
} from "./types.js";

export interface RunPipelineOptions {
  task?: string;
  symbol?: string;
  mock?: boolean;
  artifactsDir?: string;
  repoRoot?: string;
  /** Override which agents to run (by name). Defaults from task. */
  agentNames?: string[];
  registry?: AgentRegistry;
  /** Stop on first agent failure (default true). */
  stopOnError?: boolean;
}

export interface PipelineRunResult {
  ok: boolean;
  args: PipelineArgs;
  results: AgentResult[];
  outputs: Record<string, string>;
}

function taskToAgents(task: string): string[] {
  switch (task) {
    case "full-pipeline":
    case "demo":
      return [...FULL_PIPELINE];
    case "market":
      return ["market-agent"];
    case "math":
      return ["market-agent", "math-agent"];
    case "strategy":
      return ["market-agent", "math-agent", "strategy-agent"];
    case "report":
      return ["report-agent"];
    default:
      throw new Error(
        `Unknown task "${task}". Use: full-pipeline | market | math | strategy | report`,
      );
  }
}

export function createOrchestratorRegistry(
  extra: AgentDefinition[] = [],
): AgentRegistry {
  return createDefaultRegistry([...builtinAgents, ...extra]);
}

/**
 * Run a sequential multi-agent pipeline with labeled logs.
 */
export async function runPipeline(
  options: RunPipelineOptions = {},
): Promise<PipelineRunResult> {
  const task = options.task ?? "full-pipeline";
  const symbol = (options.symbol ?? "QQQ").toUpperCase();
  const mock = options.mock ?? false;
  const repoRoot = options.repoRoot ?? findRepoRoot();
  const artifactsDir = ensureArtifactsDir(repoRoot, options.artifactsDir);
  const stopOnError = options.stopOnError ?? true;
  const registry = options.registry ?? createOrchestratorRegistry();
  const agentNames = options.agentNames ?? taskToAgents(task);

  const args: PipelineArgs = {
    task,
    symbol,
    mock,
    artifactsDir,
    repoRoot,
  };

  logPipeline(
    `task=${task} symbol=${symbol} mock=${mock} artifacts=${artifactsDir}`,
  );
  logPipeline(`pipeline: ${agentNames.join(" → ")}`);

  const agents = registry.resolvePipeline(agentNames);
  const results: AgentResult[] = [];
  const outputs: Record<string, string> = {};

  for (const agent of agents) {
    logAgent(agent.name, "info", `start — ${agent.description}`);

    const ctx: AgentContext = {
      ...args,
      outputs: {
        ...outputs,
        // report-agent can read prior results
        __agentResults: JSON.stringify(results),
      },
    };

    let result: AgentResult;
    try {
      result = await agent.run(ctx);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      result = {
        agent: agent.name,
        ok: false,
        outputs: {},
        error: message,
        durationMs: 0,
      };
      logAgent(agent.name, "error", `uncaught: ${message}`);
    }

    results.push(result);
    Object.assign(outputs, result.outputs);
    // Don't leak internal meta into public outputs map for later agents
    delete outputs.__agentResults;

    if (result.warning) {
      logAgent(agent.name, "warn", result.warning);
    }

    if (!result.ok) {
      logAgent(agent.name, "error", `failed in ${result.durationMs}ms`);
      if (stopOnError) {
        logPipeline("stopping pipeline after failure");
        break;
      }
    } else {
      logAgent(agent.name, "ok", `done in ${result.durationMs}ms`);
    }
  }

  const ok = results.length === agents.length && results.every((r) => r.ok);
  logPipeline(ok ? "pipeline complete" : "pipeline finished with errors");

  return { ok, args, results, outputs };
}
