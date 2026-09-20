"""Eval the NEW ReAct audit agent on the golden set.

Maps golden invoices -> agent tools, runs AuditAgent.audit(), judges verdicts
with the mock judge (deterministic). Paces LLM calls to stay under the
free-tier 15 RPM limit (AGENT_EVAL_DELAY_SEC, default 5s).

Usage:
    GEMINI_API_KEY=... .venv/bin/python evals/run_agent_evals.py [--limit 6]
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from judge import MockJudge
from core.agent.agentic_auditor import AuditAgent
from core.agent import tools as agent_tools
from scripts.synthesize import make_vendors, make_purchase_orders, make_invoices
from core.anomaly_engine import engineer_features

DELAY = float(os.getenv("AGENT_EVAL_DELAY_SEC", "5"))


def train_xgb_for_tools():
    """Train the XGBoost model backing score_invoice_xgb (synthetic data)."""
    vendors = make_vendors()
    pos = make_purchase_orders(vendors)
    inv = make_invoices(vendors, pos, total=20000, seed=123)
    df = inv.merge(pos[["po_id", "amount_limit"]], on="po_id", how="left")
    df = df.merge(vendors[["vendor_id", "risk_rating"]], on="vendor_id", how="left")
    df["is_fraud"] = (df["status"] == "FLAGGED").astype(int)
    eng = agent_tools._get_engine()
    eng.train_dataframe(df)
    return eng


def golden_to_context(g: dict, all_golden: list) -> dict:
    invoice = {
        "invoice_id": g["invoice_number"],
        "vendor_id": g["vendor_name"],
        "po_id": g["po_number"],
        "subtotal": g["subtotal"],
        "tax_amount": g["tax_amount"],
        "total_amount": g["total_amount"],
        "invoice_date": g["invoice_date"],
    }
    po = {"po_id": g["po_number"], "amount_limit": g["po_amount_limit"]}
    vendor = {
        "vendor_id": g["vendor_name"],
        "vendor_name": g["vendor_name"],
        "risk_rating": g["vendor_risk_rating"],
    }
    # history: related invoices + other golden invoices (for duplicate search)
    history = []
    for h in all_golden:
        if h["invoice_number"] == g["invoice_number"]:
            continue
        history.append({
            "invoice_id": h["invoice_number"],
            "vendor_id": h["vendor_name"],
            "po_id": h["po_number"],
            "total_amount": h["total_amount"],
            "invoice_date": h["invoice_date"],
            "status": "FLAGGED" if h["fraud_type"] != "NORMAL" else "APPROVED",
        })
    # wire explicit duplicates from duplicate_of / related_invoices
    return {"invoice": invoice, "po": po, "vendor": vendor, "history": history}


# Map agent verdicts (APPROVE/FLAG/REJECT) to golden expected (APPROVE/FLAG/REJECT).
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only first N invoices (0=all)")
    args = ap.parse_args()

    print("Training XGBoost for agent tools...")
    train_xgb_for_tools()

    golden = json.load(open("evals/golden_invoices.json"))["invoices"]
    if args.limit:
        golden = golden[:args.limit]

    agent = AuditAgent()
    judge = MockJudge()
    results = []
    for i, g in enumerate(golden):
        ctx = golden_to_context(g, json.load(open("evals/golden_invoices.json"))["invoices"])
        if i > 0:
            time.sleep(DELAY)  # stay under 15 RPM free-tier limit
        try:
            out = agent.audit(ctx["invoice"], po=ctx["po"], vendor=ctx["vendor"],
                              history=ctx["history"])
        except Exception as e:
            print(f"{g['invoice_number']}: AGENT ERROR {e}")
            continue
        # judge expects a "brief" dict; adapt agent output
        findings_text = " ".join(out["findings"])
        brief = {"risk_verdict": out["verdict"],
                 "summary": findings_text,
                 "reasoning": findings_text,
                 "findings": out["findings"]}
        expected = {"expected_verdict": g["expected_verdict"],
                    "expected_findings": g["expected_findings"]}
        score = judge.score(expected, brief)
        ok = "OK" if score["verdict_match"] else "MISS"
        print(f"{g['invoice_number']} {g['fraud_type']:<16} exp={g['expected_verdict']:<7} "
              f"got={out['verdict']:<7} {ok} recall={score['findings_recall']:.2f} "
              f"steps={out['steps']}")
        results.append({"verdict_match": score["verdict_match"],
                        "recall": score["findings_recall"],
                        "type": g["fraud_type"]})

    n = len(results)
    acc = sum(r["verdict_match"] for r in results) / n if n else 0
    rec = sum(r["recall"] for r in results) / n if n else 0
    print(f"\nAgent eval: {n} invoices | verdict accuracy {acc:.1%} | mean recall {rec:.3f}")


if __name__ == "__main__":
    main()
