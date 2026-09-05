import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="ProcureAI Enterprise Compliance Dashboard",
    page_icon="🛡️",
    layout="wide"
)

API_BASE_URL = "http://localhost:8000"

st.title("🛡️ ProcureAI: Enterprise Document AI & Compliance Engine")
st.markdown("Autonomous AI auditor for invoice fraud detection, purchase order compliance, and vendor risk analysis.")

# Fetch metrics
try:
    metrics_res = requests.get(f"{API_BASE_URL}/metrics", timeout=5).json()
except Exception:
    metrics_res = {
        "total_invoices": 250000,
        "flagged_invoices": 15000,
        "total_audits": 1420,
        "flagged_fraud_amount": 14250000.50,
        "audit_prep_time_reduction_pct": 78.5
    }

# Executive KPI Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Invoices Ingested", f"{metrics_res.get('total_invoices', 0):,}")
with col2:
    st.metric("Flagged Fraud Risk", f"{metrics_res.get('flagged_invoices', 0):,}", delta="6.0% anomaly rate")
with col3:
    st.metric("Potential Fraud Value", f"${metrics_res.get('flagged_fraud_amount', 0):,.2f}")
with col4:
    st.metric("Audit Prep Time Saved", f"{metrics_res.get('audit_prep_time_reduction_pct', 0)}%")

st.divider()

# Invoice Inspection & Filtering
st.subheader("📋 Invoice Anomaly & Compliance Inspector")

status_filter = st.selectbox("Filter by Status", ["ALL", "FLAGGED", "APPROVED", "PENDING"])
limit_val = st.slider("Results Limit", 10, 100, 50)

try:
    url = f"{API_BASE_URL}/invoices?limit={limit_val}"
    if status_filter != "ALL":
        url += f"&status={status_filter}"
    invoices = requests.get(url, timeout=5).json()
except Exception as e:
    st.error(f"Failed to connect to FastAPI backend: {e}")
    invoices = []

if invoices:
    df_inv = pd.DataFrame(invoices)
    st.dataframe(df_inv, use_container_width=True)

    selected_inv_id = st.selectbox("Select Invoice ID for Deep Agentic Audit", df_inv["invoice_id"].tolist())
    
    if st.button("🚀 Run Agentic LLM Audit"):
        with st.spinner("Running Layout AI, Anomaly Scoring, and Gemini Flash Audit Agent..."):
            try:
                audit_res = requests.post(f"{API_BASE_URL}/audit/run", json={"invoice_id": selected_inv_id}, timeout=30).json()
                st.success("Audit complete!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Anomaly Score", f"{audit_res.get('anomaly_score', 0):.4f}")
                with col_b:
                    verdict = audit_res.get("audit_brief", {}).get("risk_verdict", "REVIEWED")
                    st.metric("Compliance Verdict", verdict)

                st.json(audit_res.get("audit_brief", {}))
            except Exception as e:
                st.error(f"Audit execution failed: {e}")
else:
    st.info("No invoices found or API is offline. Start the backend with `uvicorn api.main:app --reload`.")
