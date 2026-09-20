# ProcureAI Eval Baseline Report

Generated: 2026-09-20 05:33 UTC
Golden set: `30` invoices (5 per fraud type: NORMAL, DUPLICATE, SPLIT_PO, PRICE_DRIFT, GHOST, CALC_DISCREPANCY)
Responder: **canned mock (rule-based test double, zero credentials)**
Judge: **mock** (`JUDGE_MODE`)

## Headline metrics

- Verdict accuracy: **100.0%** (30/30)
- Mean findings recall: **0.983**

## By fraud type

| fraud type | n | verdict accuracy | mean findings recall |
|---|---|---|---|
| NORMAL | 5 | 100.0% | 1.000 |
| DUPLICATE | 5 | 100.0% | 1.000 |
| SPLIT_PO | 5 | 100.0% | 1.000 |
| PRICE_DRIFT | 5 | 100.0% | 1.000 |
| GHOST | 5 | 100.0% | 1.000 |
| CALC_DISCREPANCY | 5 | 100.0% | 0.900 |

## Per-invoice results

| invoice | fraud type | expected | got | verdict match | findings recall | notes |
|---|---|---|---|---|---|---|
| INV-3001 | NORMAL | APPROVE | APPROVE | yes | 1.00 | verdict match (APPROVE). 3/3 findings recalled |
| INV-3002 | NORMAL | APPROVE | APPROVE | yes | 1.00 | verdict match (APPROVE). 3/3 findings recalled |
| INV-3003 | NORMAL | APPROVE | APPROVE | yes | 1.00 | verdict match (APPROVE). 3/3 findings recalled |
| INV-3004 | NORMAL | APPROVE | APPROVE | yes | 1.00 | verdict match (APPROVE). 3/3 findings recalled |
| INV-3005 | NORMAL | APPROVE | APPROVE | yes | 1.00 | verdict match (APPROVE). 3/3 findings recalled |
| INV-3006 | DUPLICATE | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3007 | DUPLICATE | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3008 | DUPLICATE | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3009 | DUPLICATE | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3010 | DUPLICATE | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3011 | SPLIT_PO | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3012 | SPLIT_PO | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3013 | SPLIT_PO | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3014 | SPLIT_PO | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3015 | SPLIT_PO | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3016 | PRICE_DRIFT | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3017 | PRICE_DRIFT | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3018 | PRICE_DRIFT | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3019 | PRICE_DRIFT | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3020 | PRICE_DRIFT | FLAG | FLAG | yes | 1.00 | verdict match (FLAG). 2/2 findings recalled |
| INV-3021 | GHOST | REJECT | REJECT | yes | 1.00 | verdict match (REJECT). 2/2 findings recalled |
| INV-3022 | GHOST | REJECT | REJECT | yes | 1.00 | verdict match (REJECT). 2/2 findings recalled |
| INV-3023 | GHOST | REJECT | REJECT | yes | 1.00 | verdict match (REJECT). 2/2 findings recalled |
| INV-3024 | GHOST | REJECT | REJECT | yes | 1.00 | verdict match (REJECT). 2/2 findings recalled |
| INV-3025 | GHOST | REJECT | REJECT | yes | 1.00 | verdict match (REJECT). 2/2 findings recalled |
| INV-3026 | CALC_DISCREPANCY | REJECT | REJECT | yes | 1.00 | verdict match (REJECT). 2/2 findings recalled |
| INV-3027 | CALC_DISCREPANCY | REJECT | REJECT | yes | 0.50 | verdict match (REJECT). 1/2 findings recalled. missing: total overstated by $100.00 |
| INV-3028 | CALC_DISCREPANCY | REJECT | REJECT | yes | 1.00 | verdict match (REJECT). 2/2 findings recalled |
| INV-3029 | CALC_DISCREPANCY | REJECT | REJECT | yes | 1.00 | verdict match (REJECT). 2/2 findings recalled |
| INV-3030 | CALC_DISCREPANCY | REJECT | REJECT | yes | 1.00 | verdict match (REJECT). 2/2 findings recalled |

## What 'baseline' means

This run used the **canned mock responder**, a deterministic rule-based test
double -- not the LLM. High scores here validate the harness plumbing
(prompt construction, brief parsing, judging, reporting), not the agent.
For the honest agent baseline, set `GEMINI_API_KEY` and re-run:

```bash
GEMINI_API_KEY=... JUDGE_MODE=gemini python evals/run_evals.py
```

Note: without a key, `AgentAuditor.call_gemini_api` itself returns a hardcoded
`FLAGGED` mock brief (see core/agent_auditor.py); the canned responder is used
instead so the harness exercises varied verdicts end-to-end.

## Methodology
See `evals/README.md` for golden-set design, judge scoring, and how to extend the set.
