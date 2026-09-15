import type { AgentDefinition, AgentName } from "./types.js";

/**
 * Simple agent registry — register by name, look up, list for pipeline composition.
 */
export class AgentRegistry {
  private readonly agents = new Map<AgentName, AgentDefinition>();

  register(agent: AgentDefinition): this {
    if (this.agents.has(agent.name)) {
      throw new Error(`Agent already registered: ${agent.name}`);
    }
    this.agents.set(agent.name, agent);
    return this;
  }

  get(name: AgentName): AgentDefinition | undefined {
    return this.agents.get(name);
  }

  require(name: AgentName): AgentDefinition {
    const agent = this.agents.get(name);
    if (!agent) {
      throw new Error(`Unknown agent: ${name}. Registered: ${this.names().join(", ") || "(none)"}`);
    }
    return agent;
  }

  has(name: AgentName): boolean {
    return this.agents.has(name);
  }

  names(): AgentName[] {
    return [...this.agents.keys()];
  }

  list(): AgentDefinition[] {
    return [...this.agents.values()];
  }

  /** Resolve an ordered pipeline; throws if any name is missing. */
  resolvePipeline(names: AgentName[]): AgentDefinition[] {
    return names.map((n) => this.require(n));
  }

  clear(): void {
    this.agents.clear();
  }

  get size(): number {
    return this.agents.size;
  }
}

export function createDefaultRegistry(
  agents: AgentDefinition[],
): AgentRegistry {
  const registry = new AgentRegistry();
  for (const agent of agents) {
    registry.register(agent);
  }
  return registry;
}
