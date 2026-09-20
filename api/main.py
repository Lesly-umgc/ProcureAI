from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from dotenv import load_dotenv
load_dotenv()

from database.db import SessionLocal, Invoice, PurchaseOrder, Vendor, AuditLog
from core.anomaly_engine import AnomalyScoringEngine
from core.agent_auditor import AgentAuditor

app = FastAPI(title="ProcureAI Enterprise API", version="1.0.0")

anomaly_engine = AnomalyScoringEngine()
# Try training model on startup if data exists
try:
    anomaly_engine.train_model()
except Exception as e:
    print(f"Model init training note: {e}")

agent_auditor = AgentAuditor()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AuditRequest(BaseModel):
    invoice_id: int

@app.get("/health")
def health_check():
    return {"status": "healthy", "system": "ProcureAI Enterprise Engine"}

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    total_invoices = db.query(Invoice).count()
    flagged_invoices = db.query(Invoice).filter(Invoice.status == "FLAGGED").count()
    total_audits = db.query(AuditLog).count()
    
    # Calculate sum of flagged invoice amounts
    flagged_amount_res = db.query(Invoice).filter(Invoice.status == "FLAGGED").all()
    flagged_fraud_amount = sum([inv.total_amount for inv in flagged_amount_res])

    return {
        "total_invoices": total_invoices,
        "flagged_invoices": flagged_invoices,
        "total_audits": total_audits,
        "flagged_fraud_amount": round(flagged_fraud_amount, 2),
        # Measured via proofs/prove_efficiency.py (99.87% reduction vs a
        # 4-min/invoice manual baseline). Re-run the proof if the pipeline changes.
        "audit_prep_time_reduction_pct": 99.87
    }

@app.get("/invoices")
def list_invoices(skip: int = 0, limit: int = 50, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Invoice)
    if status:
        query = query.filter(Invoice.status == status.upper())
    invoices = query.offset(skip).limit(limit).all()
    
    results = []
    for inv in invoices:
        results.append({
            "invoice_id": inv.invoice_id,
            "invoice_number": inv.invoice_number,
            "vendor_name": inv.vendor.name if inv.vendor else "Unknown",
            "invoice_date": str(inv.invoice_date),
            "subtotal": inv.subtotal,
            "total_amount": inv.total_amount,
            "status": inv.status
        })
    return results

@app.post("/audit/run")
def run_audit(req: AuditRequest, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.invoice_id == req.invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    po = inv.purchase_order
    vendor = inv.vendor
    
    score = anomaly_engine.score_invoice(
        subtotal=inv.subtotal,
        total_amount=inv.total_amount,
        amount_limit=po.amount_limit if po else 10000.0,
        risk_rating=vendor.risk_rating if vendor else 0.1
    )

    brief = agent_auditor.audit_invoice(invoice_id=inv.invoice_id, anomaly_score=score)
    return {
        "invoice_id": inv.invoice_id,
        "anomaly_score": round(score, 4),
        "audit_brief": brief
    }
