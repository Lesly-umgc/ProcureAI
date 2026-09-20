"""ProcureAI audit agent: a real ReAct loop over deterministic tools.

Unlike the legacy single-prompt auditor, this agent:
  1. reasons about what evidence it needs,
  2. calls a deterministic tool (XGBoost score, arithmetic check, duplicate
     search, PO match, vendor assessment),
  3. observes the result and decides the next step,
  4. issues a final verdict with cited evidence.

The LLM reasons; the tools compute. Free-tier Gemini model only
(GEMINI_MODEL env, default gemini-3.1-flash-lite).
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


from core.agent.tools import TOOLS, tool_descriptions
from core.agent.llm_throttle import GeminiClient, redact

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
# Note: free-tier enforcement happens inside GeminiClient.__init__ (via
# llm_throttle.assert_free_tier) so that misconfiguration fails with a clean
# config error instead of at import time.
MAX_STEPS = int(os.getenv("AGENT_MAX_STEPS", "8"))

SYSTEM_PROMPT = """You are a procurement fraud audit agent. You investigate ONE invoice
at a time using the tools below. Think step by step.

Rules:
- ALWAYS call verify_arithmetic first — arithmetic certainty beats ML suspicion.
- Then gather evidence with the other tools as needed (score, duplicates, PO, vendor).
- Never invent numbers: cite only values returned by tools.
- After at most {max_steps} tool calls, give the final verdict.

Tools:
{tools}

Respond in exactly one of these two JSON shapes, no other text:

To call a tool:
{{"thought": "<why this tool next>", "action": "<tool_name>", "action_input": {{<args as JSON>}} }}

For the final verdict (no more tools needed):
{{"thought": "<summary of evidence>", "verdict": "APPROVE|FLAG|REJECT",
  "confidence": <0-1>, "findings": ["<evidence-backed finding>", ...],
  "amount_at_risk": <number>}}

Findings must explicitly address each of these (one finding per line):
- whether line totals reconcile with subtotal and total (cite the numbers)
- whether the total is within the PO amount limit (cite billed vs limit)
- vendor standing (risk rating, history, ghost signals if any)
- duplicates found or explicitly none
- XGBoost anomaly score and what it means

Verdict guidance:
- APPROVE: arithmetic checks out, no duplicates, within PO, vendor normal.
- FLAG: suspicious pattern (near-threshold, price drift, ghost signals, high ML score)
  needing human review.
- REJECT: certain fraud — arithmetic proof of overbilling, exact duplicate, or
  billed over PO limit with no justification.
"""


def _extract_json(text: str) -> Dict[str, Any]:
    """Pull the first {...} JSON object out of model output."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"no JSON in model output: {text[:200]}")
    return json.loads(match.group(0))


class AuditAgent:
    """ReAct audit agent.

    Live mode needs GEMINI_API_KEY (free-tier model only, enforced by
    llm_throttle). Pass ``llm_fn`` to inject a deterministic backend instead
    (used by the eval harness's --mock-llm dry-run; never a real evaluation).
    """

    def __init__(self, api_key: str | None = None, max_steps: int = MAX_STEPS,
                 llm_fn=None):
        self.max_steps = max_steps
        self.trace: List[Dict[str, Any]] = []
        if llm_fn is not None:
            self._llm = llm_fn
            self.model = "mock-llm (dry-run, not a real evaluation)"
            return
        self._client = GeminiClient(api_key=api_key, model=GEMINI_MODEL)
        self._llm = self._client.generate
        self.model = self._client.model

    def _dispatch(self, action: str, action_input: Dict[str, Any],
                  context: Dict[str, Any]) -> Any:
        """Run a tool by name. history/po/vendor come from the audit context."""
        if action not in TOOLS:
            return {"error": f"unknown tool: {action}"}
        fn, _ = TOOLS[action]
        try:
            if action == "find_duplicates":
                return fn(context["invoice"], context.get("history", []))
            if action == "check_po":
                return fn(context["invoice"], context.get("po", {}))
            if action == "assess_vendor":
                return fn(context.get("vendor", {}), context.get("history", []))
            return fn(context["invoice"])
        except Exception as e:  # tools must never crash the loop
            return {"error": f"{action} failed: {e}"}

    def _redacted_llm(self, prompt: str) -> str:
        """Call the LLM backend; any failure surfaces with secrets redacted."""
        try:
            return self._llm(prompt)
        except Exception as e:  # noqa: BLE001 - redacted, then re-raised
            key = getattr(self, "_client", None)
            raise RuntimeError(
                redact(e, key.api_key if key else None)
            ) from e

    def audit(self, invoice: Dict[str, Any], po: Dict[str, Any] | None = None,
              vendor: Dict[str, Any] | None = None,
              history: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        """Run the ReAct loop and return the final verdict dict."""
        context = {"invoice": invoice, "po": po or {},
                   "vendor": vendor or {}, "history": history or []}
        self.trace = []
        system = SYSTEM_PROMPT.format(max_steps=self.max_steps,
                                      tools=tool_descriptions())
        transcript = [
            f"Invoice under audit:\n{json.dumps(invoice, indent=2, default=str)}"
        ]

        for step in range(self.max_steps):
            prompt = system + "\n\n" + "\n\n".join(transcript)
            if step == self.max_steps - 1:
                prompt += ("\n\nThis is your LAST step. You MUST return the final "
                           "verdict JSON now (no action).")
            raw = self._redacted_llm(prompt)
            try:
                msg = _extract_json(raw)
            except ValueError:
                transcript.append(f"Agent output (unparseable, retry): {raw[:300]}")
                continue

            self.trace.append({"step": step, "thought": msg.get("thought"),
                               "action": msg.get("action")})
            if "verdict" in msg:
                return self._finalize(msg)
            action = msg.get("action")
            if not action:
                transcript.append("No action or verdict given; provide one.")
                continue
            obs = self._dispatch(action, msg.get("action_input", {}), context)
            self.trace[-1]["observation"] = obs
            transcript.append(
                f"Thought: {msg.get('thought')}\nAction: {action}\n"
                f"Observation: {json.dumps(obs, default=str)[:1500]}"
            )

        # Forced verdict if the loop never concluded
        return self._finalize({
            "verdict": "FLAG",
            "confidence": 0.5,
            "findings": ["agent did not converge within step budget; needs human review"],
            "amount_at_risk": float(invoice.get("total_amount", 0)),
        })

    def _finalize(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        verdict = str(msg.get("verdict", "FLAG")).upper()
        if verdict not in ("APPROVE", "FLAG", "REJECT"):
            verdict = "FLAG"
        return {
            "verdict": verdict,
            "confidence": float(msg.get("confidence", 0.5)),
            "findings": list(msg.get("findings", [])),
            "amount_at_risk": float(msg.get("amount_at_risk", 0)),
            "steps": len(self.trace),
            "model": self.model,
        }
