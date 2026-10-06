# Node packages status

Checked on branch `eng/03-node-side` (from `forked-sprint-hack`, trading-model import b130f0d).
Environment: Node v25.9.0, npm 11.12.1, macOS, system Python 3.9.6 (repo declares node >=20).

## Results

| Step | Result |
|------|--------|
| `npm ci` | OK. 11 packages added, 0 vulnerabilities |
| `npm run build` (market-data, strategies, orchestrator via `tsc`; dashboard via copy-static) | OK, no errors |
| market-data tests | 11 pass, 0 fail |
| strategies tests | 11 pass, 0 fail |
| orchestrator tests | 8 pass, 0 fail |
| dashboard tests | 2 pass, 0 fail |
| `npm run demo` (orchestrator pipeline) | Completes ("pipeline complete"), but in mock mode: the math agent and the strategy agent write placeholders because the Python `trading_model_math` package and the strategies CLI are not found |

Total Node tests: 32 pass, 0 fail.

## Issues found

1. Root `npm test` only ran 3 of the 4 Node packages (dashboard was skipped). It then ran `python3 -m pytest` in `packages/core-math`, which fails here with `No module named pytest`. Fix: split into `test:node` (all 4 packages), `test:py`, and `test` (runs both). `trading/package.json` only.
2. `npm run demo` does not exercise real Python math or strategies output unless `packages/core-math` is pip-installed. Not a Node bug.
3. Not verified: Node 20 (only 25 tested), live NASDAQ Data Link / ORATS calls (tests use mocks), `demo:umbrella` and `smoke:api` scripts.

## Recommendation

Include the Node packages in the v1 import, but do not containerize them (matches the plan's default). They build and pass their tests with zero runtime dependencies, so they cost nothing to keep. Keep the API image Python-only. Add a `trading-agents` compose service (profile `agents`) later, once the Python math package is installed in that image, so the orchestrator produces real output rather than placeholders. Run `npm run test:node` in CI if Node is available.
