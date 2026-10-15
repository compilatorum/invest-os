# ICM Lab Adaptation — Kairos / InvestmentOS

**Role in the application:** risk-policy and decision-specification layer behind Value Curator. Do not pitch InvestmentOS/Kairos as a separate startup for this application.

## Narrowed thesis
Translate market and execution conditions into explicit, testable policies that determine whether a proposed on-chain action may proceed. For the ICM Lab MVP, prioritize financial variables: data freshness, price deviation, quote validity, slippage, exposure limits, and human approval thresholds.

## What to retain from Kairos
- Structured risk dimensions and decision pipeline.
- Scenario analysis and explicit assumptions.
- Simulation-first engineering and measurable acceptance criteria.
- Auditability of decisions and separation between signal, model, policy, and action.

## What to defer
- Eight-capital scoring as a customer-facing feature.
- Broad regenerative-economy narratives.
- Investment recommendations, portfolio performance claims, tokenization or governance features unrelated to the first validated use case.

## Proposed policy object
A policy should identify: data source; maximum data age; allowed deviation/confidence; quote validity; maximum slippage; exposure cap; required approval; fail-closed behavior; and a decision log. These are product requirements, not a claim that every item is already implemented.

## Evaluation
Build reproducible tests for:
1. Fresh data and acceptable quote → action may proceed.
2. Stale data → block.
3. Excessive deviation or slippage → block.
4. Missing quote or policy → block.
5. Insufficient authority → block.
6. Explicit human override, where allowed → record approver and reason.

## Evidence boundary
InvestmentOS currently documents Kairos as an eight-dimension capital framework and a proposed simulation/decision pipeline. Clearly distinguish documented concepts from working software. Link to the implementation only after confirming which components run end-to-end.

## ICM Lab fit
Supports the program's asset-management/infrastructure thesis as a policy engine for safer automated treasury workflows. It does not, by itself, establish Pix/SPB integration, registered-receivable tokenization, FIDC infrastructure, or production readiness.
