import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  AgentRegistry,
  createDefaultRegistry,
  createOrchestratorRegistry,
  builtinAgents,
  FULL_PIPELINE,
} from "../src/index.js";
import type { AgentDefinition, AgentResult } from "../src/types.js";

function stubAgent(name: string): AgentDefinition {
  return {
    name,
    description: `stub ${name}`,
    run: async (): Promise<AgentResult> => ({
      agent: name,
      ok: true,
      outputs: {},
      durationMs: 1,
    }),
  };
}

describe("AgentRegistry", () => {
  it("registers and retrieves agents by name", () => {
    const registry = new AgentRegistry();
    registry.register(stubAgent("alpha"));
    registry.register(stubAgent("beta"));

    assert.equal(registry.size, 2);
    assert.equal(registry.has("alpha"), true);
    assert.equal(registry.get("alpha")?.name, "alpha");
    assert.deepEqual(registry.names(), ["alpha", "beta"]);
  });

  it("rejects duplicate registration", () => {
    const registry = new AgentRegistry();
    registry.register(stubAgent("dup"));
    assert.throws(() => registry.register(stubAgent("dup")), /already registered/);
  });

  it("require throws for unknown agents", () => {
    const registry = createDefaultRegistry([stubAgent("only")]);
    assert.throws(() => registry.require("missing"), /Unknown agent/);
  });

  it("resolvePipeline returns agents in order", () => {
    const registry = createDefaultRegistry([
      stubAgent("a"),
      stubAgent("b"),
      stubAgent("c"),
    ]);
    const pipeline = registry.resolvePipeline(["c", "a"]);
    assert.deepEqual(
      pipeline.map((a) => a.name),
      ["c", "a"],
    );
  });

  it("ships builtin agents matching full-pipeline", () => {
    const registry = createOrchestratorRegistry();
    assert.ok(registry.size >= 4);
    for (const name of FULL_PIPELINE) {
      assert.ok(registry.has(name), `missing ${name}`);
    }
    assert.equal(builtinAgents.length, 4);
    const resolved = registry.resolvePipeline(FULL_PIPELINE);
    assert.equal(resolved.length, 4);
    assert.equal(resolved[0]?.name, "market-agent");
    assert.equal(resolved[3]?.name, "report-agent");
  });

  it("allows extending the registry with a custom agent", () => {
    const registry = createOrchestratorRegistry([stubAgent("risk-agent")]);
    assert.ok(registry.has("risk-agent"));
    assert.ok(registry.has("market-agent"));
  });
});
