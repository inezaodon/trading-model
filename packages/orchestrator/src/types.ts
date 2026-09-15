/**
 * Shared types aligned with artifact contracts across packages.
 */

export type AgentName =
  | "market-agent"
  | "math-agent"
  | "strategy-agent"
  | "report-agent"
  | string;

export interface PipelineArgs {
  task: string;
  symbol: string;
  mock: boolean;
  artifactsDir: string;
  repoRoot: string;
}

export interface AgentResult {
  agent: AgentName;
  ok: boolean;
  outputs: Record<string, string>;
  message?: string;
  warning?: string;
  error?: string;
  durationMs: number;
}

export interface AgentContext extends PipelineArgs {
  /** Paths written by earlier agents in this run. */
  outputs: Record<string, string>;
}

export interface AgentDefinition {
  name: AgentName;
  description: string;
  run: (ctx: AgentContext) => Promise<AgentResult>;
}

/** Flat fields used by strategies; also embed ORATS row for market-data compatibility. */
export interface SurfaceArtifact {
  source?: "mock" | "nasdaq-data-link" | string;
  fetchedAt?: string;
  symbol: string;
  spot?: number;
  asOf?: string;
  mock?: boolean;
  iv30: number;
  iv60?: number;
  iv90?: number;
  slope?: number;
  deriv?: number;
  forwardVariance?: number[];
  surface?: {
    ticker: string;
    date: string;
    stockpx: number;
    iv30: number;
    iv60: number;
    iv90: number;
    slope: number;
    deriv: number;
  };
  reconstruction?: {
    formula: string;
    note: string;
  };
}

/** core-math / strategies PathBundle shape. */
export interface PathsArtifact {
  model: string;
  symbol: string;
  params?: Record<string, number>;
  times: number[];
  paths: Array<{ S: number[]; v: number[] }>;
  mock?: boolean;
  warning?: string;
  /** Legacy flat series (dashboard / placeholders). */
  spot?: number[];
  variance?: number[];
  nPaths?: number;
  nSteps?: number;
  dt?: number;
}

export interface BacktestArtifact {
  symbol: string;
  strategy: string;
  /** Total PnL (strategies package) or step series (legacy placeholder). */
  pnl: number | number[];
  equityCurve?: Array<{ t: number; equity: number }>;
  metrics?: {
    totalReturn: number;
    sharpe: number;
    maxDrawdown: number;
  };
  cumulativePnl?: number;
  sharpe?: number;
  maxDrawdown?: number;
  mock?: boolean;
  warning?: string;
}

export interface ReportArtifact {
  generatedAt: string;
  symbol: string;
  task: string;
  mock: boolean;
  agents: AgentResult[];
  surfacePath?: string;
  pathsPath?: string;
  backtestPath?: string;
  summary: {
    spot?: number;
    iv30?: number;
    pathCount?: number;
    finalSpot?: number;
    terminalVariance?: number;
    cumulativePnl?: number;
    sharpe?: number;
  };
}
