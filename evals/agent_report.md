# ProcureAI Agent Eval Report

Generated: 2026-09-20 07:16 UTC (run by evals/run_agent_evals.py, live mode)
Git commit: `0f87ccb`
Golden set: `30` invoices (CALC_DISCREPANCY: 5, DUPLICATE: 5, GHOST: 5, NORMAL: 5, PRICE_DRIFT: 5, SPLIT_PO: 5)
Responder: **live Gemini `gemini-3.5-flash-lite`** via `core/agent/agentic_auditor.py` (ReAct loop over deterministic tools)
Judge: **mock** (`JUDGE_MODE`)

## Headline metrics

- Verdict accuracy: **60.0%** (18/30; 95% Wilson CI 42.3%–75.4%)
- Mean findings recall: **0.278**
- Agent errors: **0** (each counted as a verdict miss)

## By fraud type

| fraud type | n | verdict accuracy | mean findings recall |
|---|---|---|---|
| CALC_DISCREPANCY | 5 | 40.0% | 0.400 |
| DUPLICATE | 5 | 80.0% | 0.700 |
| GHOST | 5 | 20.0% | 0.000 |
| NORMAL | 5 | 40.0% | 0.467 |
| PRICE_DRIFT | 5 | 80.0% | 0.000 |
| SPLIT_PO | 5 | 100.0% | 0.100 |

## Per-invoice results

| invoice | fraud type | expected | got | verdict match | findings recall | steps | notes |
|---|---|---|---|---|---|---|---|
| INV-3001 | NORMAL | APPROVE | FLAG | no | 0.33 | 7 | verdict mismatch: expected APPROVE, got FLAG. 1/3 findings recalled. missing: line totals reconcile with subtotal; vendor on approved vendor list |
| INV-3002 | NORMAL | APPROVE | APPROVE | yes | 0.33 | 6 | verdict match (APPROVE). 1/3 findings recalled. missing: line totals reconcile with subtotal; vendor on approved vendor list |
| INV-3003 | NORMAL | APPROVE | FLAG | no | 0.67 | 6 | verdict mismatch: expected APPROVE, got FLAG. 2/3 findings recalled. missing: vendor on approved vendor list |
| INV-3004 | NORMAL | APPROVE | APPROVE | yes | 0.67 | 6 | verdict match (APPROVE). 2/3 findings recalled. missing: vendor on approved vendor list |
| INV-3005 | NORMAL | APPROVE | FLAG | no | 0.33 | 6 | verdict mismatch: expected APPROVE, got FLAG. 1/3 findings recalled. missing: line totals reconcile with subtotal; vendor on approved vendor list |
| INV-3006 | DUPLICATE | FLAG | FLAG | yes | 1.00 | 8 | verdict match (FLAG). 2/2 findings recalled |
| INV-3007 | DUPLICATE | FLAG | FLAG | yes | 0.50 | 6 | verdict match (FLAG). 1/2 findings recalled. missing: duplicate of INV-2025-0019871 |
| INV-3008 | DUPLICATE | FLAG | FLAG | yes | 0.50 | 7 | verdict match (FLAG). 1/2 findings recalled. missing: duplicate of INV-2025-0091234 |
| INV-3009 | DUPLICATE | FLAG | APPROVE | no | 0.50 | 5 | verdict mismatch: expected FLAG, got APPROVE. 1/2 findings recalled. missing: duplicate of INV-2025-0077665 |
| INV-3010 | DUPLICATE | FLAG | FLAG | yes | 1.00 | 5 | verdict match (FLAG). 2/2 findings recalled |
| INV-3011 | SPLIT_PO | FLAG | FLAG | yes | 0.00 | 5 | verdict match (FLAG). 0/2 findings recalled. missing: total $9,987.40 just below $10,000 approval threshold; possible split billing with INV-3012 |
| INV-3012 | SPLIT_PO | FLAG | FLAG | yes | 0.00 | 6 | verdict match (FLAG). 0/2 findings recalled. missing: total $9,961.20 just below $10,000 approval threshold; possible split billing with INV-3011 |
| INV-3013 | SPLIT_PO | FLAG | FLAG | yes | 0.50 | 5 | verdict match (FLAG). 1/2 findings recalled. missing: total $9,890.55 just below $10,000 approval threshold |
| INV-3014 | SPLIT_PO | FLAG | FLAG | yes | 0.00 | 6 | verdict match (FLAG). 0/2 findings recalled. missing: total $9,945.10 just below $10,000 approval threshold; possible split billing with INV-3013 |
| INV-3015 | SPLIT_PO | FLAG | FLAG | yes | 0.00 | 6 | verdict match (FLAG). 0/2 findings recalled. missing: total $9,975.00 just below $10,000 approval threshold; threshold proximity suggests approval-limit evasion |
| INV-3016 | PRICE_DRIFT | FLAG | APPROVE | no | 0.00 | 5 | verdict mismatch: expected FLAG, got APPROVE. 0/2 findings recalled. missing: unit price 50% above PO contracted rate; price inflation on cloud compute credits |
| INV-3017 | PRICE_DRIFT | FLAG | FLAG | yes | 0.00 | 5 | verdict match (FLAG). 0/2 findings recalled. missing: unit price 45% above PO contracted rate; price inflation on software licenses |
| INV-3018 | PRICE_DRIFT | FLAG | FLAG | yes | 0.00 | 6 | verdict match (FLAG). 0/2 findings recalled. missing: unit price 40% above PO contracted rate; price inflation on facility cleaning |
| INV-3019 | PRICE_DRIFT | FLAG | FLAG | yes | 0.00 | 6 | verdict match (FLAG). 0/2 findings recalled. missing: unit price 50% above PO contracted rate; price inflation on lab equipment calibration |
| INV-3020 | PRICE_DRIFT | FLAG | FLAG | yes | 0.00 | 6 | verdict match (FLAG). 0/2 findings recalled. missing: unit price 36% above PO contracted rate; price inflation on contract review hours |
| INV-3021 | GHOST | REJECT | FLAG | no | 0.00 | 5 | verdict mismatch: expected REJECT, got FLAG. 0/2 findings recalled. missing: vendor not in approved vendor master; unregistered vendor with unverified tax ID |
| INV-3022 | GHOST | REJECT | REJECT | yes | 0.00 | 5 | verdict match (REJECT). 0/2 findings recalled. missing: vendor not in approved vendor master; unregistered vendor with unverified tax ID |
| INV-3023 | GHOST | REJECT | FLAG | no | 0.00 | 5 | verdict mismatch: expected REJECT, got FLAG. 0/2 findings recalled. missing: vendor not in approved vendor master; unregistered vendor with unverified tax ID |
| INV-3024 | GHOST | REJECT | FLAG | no | 0.00 | 6 | verdict mismatch: expected REJECT, got FLAG. 0/2 findings recalled. missing: vendor not in approved vendor master; unregistered vendor with unverified tax ID |
| INV-3025 | GHOST | REJECT | FLAG | no | 0.00 | 6 | verdict mismatch: expected REJECT, got FLAG. 0/2 findings recalled. missing: vendor not in approved vendor master; unregistered vendor with unverified tax ID |
| INV-3026 | CALC_DISCREPANCY | REJECT | FLAG | no | 0.00 | 5 | verdict mismatch: expected REJECT, got FLAG. 0/2 findings recalled. missing: line items sum to $5,000.00 but stated subtotal is $5,250.00; calculation discrepancy of $250.00 |
| INV-3027 | CALC_DISCREPANCY | REJECT | FLAG | no | 0.50 | 6 | verdict mismatch: expected REJECT, got FLAG. 1/2 findings recalled. missing: stated tax $749.60 inconsistent with 8% of subtotal ($649.60) |
| INV-3028 | CALC_DISCREPANCY | REJECT | REJECT | yes | 0.50 | 3 | verdict match (REJECT). 1/2 findings recalled. missing: subtotal plus tax equals $3,726.27 but stated total is $3,826.27 |
| INV-3029 | CALC_DISCREPANCY | REJECT | APPROVE | no | 0.50 | 7 | verdict mismatch: expected REJECT, got APPROVE. 1/2 findings recalled. missing: calculation discrepancy of $200.00 |
| INV-3030 | CALC_DISCREPANCY | REJECT | REJECT | yes | 0.50 | 3 | verdict match (REJECT). 1/2 findings recalled. missing: subtotal plus tax equals $729.54 but stated total is $779.54 |

## Methodology & honesty notes

- Every number above comes from this run only; nothing is carried over from other reports or runs.
- Agent errors (exceptions, timeouts, unparseable output) are recorded as rows with `verdict_match: false` and recall 0.0 — they are never silently dropped.
- `GEMINI_MODEL` is restricted to the free-tier allowlist in `core/agent/llm_throttle.py`; a non-free model fails the run before any API call.
- LLM calls are paced to the free-tier rate limit with retries and a circuit breaker; all logged text is redacted so API keys cannot leak into this report.
- The mock judge is deterministic and rule-based; verdict aliases (APPROVED/FLAGGED/REJECTED) are normalized before comparison.

Compare with `evals/baseline_report.md` (legacy single-prompt auditor) to measure the agent's improvement.
