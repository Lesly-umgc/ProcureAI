# TASK: End-to-End Build of ProcureAI (Enterprise Document AI & Compliance Engine)

You are acting as an autonomous Principal AI Engineer building "ProcureAI", a production-grade enterprise invoice anomaly detection and compliance system.
Operate directly in this repository (/Users/Shared/AI_Workspace). Implement the architecture modularly, verify every stage, and write production-grade code.

## System Constraints & Hardware Guardrails
- Target Role: Senior AI Engineer hiring bar (clean OOP/modular design, type hints, Pydantic schemas, clear metric evaluation).
- Hardware: Apple Silicon M1 (8 GB RAM, CPU/MPS, 256 GB SSD).
- Design Pattern: Asymmetric Architecture. Local execution for storage, embedding, tabular ML, and LayoutLMv3. Cloud API for LLM agent reasoning.
- Memory Limits: Ingest and generate data in streaming batches of 5,000–10,000 records. Never load 250K rows into a single in-memory DataFrame.
- API Quota & Rate-Limit Guardrails (Gemini Flash API):
  * Strictly enforce client-side rate limiting and exponential backoff (`tenacity` or custom token-bucket limiter).
  * Design the audit workflow to operate within free/tier quota bounds: batch requests cautiously, respect RPM constraints, and cache responses to avoid redundant calls.
  * Never spam the API across all 250K invoices: only route high-risk anomalies (top ~1–2% suspicious records or on-demand UI queries) to the LLM agent.

---

## IMPLEMENTATION PHASES

### Phase 1: Environment & PostgreSQL + pgvector Setup
1. Check Homebrew installation for PostgreSQL 16 and pgvector. Install and start services if missing.
2. Initialize database `procureai_db`.
3. Create the database connection pool using SQLAlchemy and asyncpg/psycopg2.
4. Apply the DDL schema with pgvector enabled:
   - `vendors` (vendor_id, name, tax_id, bank_account, address, risk_rating, embedding vector(384))
   - `purchase_orders` (po_id, po_number, vendor_id, department_id, amount_limit, status, issue_date)
   - `invoices` (invoice_id, invoice_number, vendor_id, po_id, invoice_date, subtotal, tax_amount, total_amount, raw_text, embedding vector(384), status)
   - `invoice_line_items` (line_id, invoice_id, item_description, quantity, unit_price, line_total, category_code)
   - `audit_logs` (audit_id, invoice_id, anomaly_score, risk_level, triggered_rules, agent_reasoning, status, created_at)
5. Create B-tree and IVFFlat vector indexes on all search and foreign key columns.

### Phase 2: Hybrid Data Synthesis Pipeline (250,000+ Invoices)
1. Ingest seed patterns from real public datasets (ICDAR SROIE receipts structure & Kaggle procurement fraud features).
2. Build `scripts/generate_data.py`:
   - Generate realistic vendor profiles, departments, and historical PO contracts.
   - Stream batch-inserts into PostgreSQL using `psycopg2.extras.execute_batch` or `COPY`.
   - Inject realistic enterprise fraud patterns into ~6% of records:
     * Duplicate Invoicing (subtle date or invoice number mutations).
     * Split POs / Threshold Dodging (multiple invoices just below $10,000 sign-off limits).
     * Unit Price Drift (30-60% sudden inflation above historical PO terms).
     * Ghost Vendors (bank routing and address mismatch anomalies).
     * Sum Calculation Discrepancies (line item drift vs. total).

### Phase 3: Document AI & Embedding Pipeline
1. Ingest invoice layout data using Hugging Face's `microsoft/layoutlmv3-base` with `pytesseract` to demonstrate token classification (Vendor, Date, Total, Tax) from document bounding boxes.
2. Build an embedding module using `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) to compute dense representations of line items and vendor metadata. Store directly into PostgreSQL `vector(384)` columns.

### Phase 4: Core Anomaly Scoring Engine
1. Implement tabular feature engineering: PO matching ratio, historical price delta, threshold proximity score, vendor tenure, vector cosine distance to known fraud patterns.
2. Train an `XGBoost` classifier with class-imbalance weighting (`scale_pos_weight`) to output an anomaly probability score.
3. Combine model output with rule-based compliance gates (e.g., duplicate hash detection).

### Phase 5: Rate-Limited Agentic LLM Audit & Policy Reasoning Layer
1. Build `core/agent_auditor.py` configured with strict rate-limiting and exponential backoff retry wrappers.
2. For high-risk records (score > 0.80 or on-demand user clicks in the UI), trigger the audit agent via the Gemini Flash API.
3. The agent executes multi-step audit verification:
   - Compares PO terms vs. line-item charges.
   - Evaluates vendor similarity scores and flags potential duplicate/shell entities.
   - Outputs a validated JSON audit brief: summary, cited policy rules, and risk verdict (Approve / Flag / Reject).
4. Persist structured responses to `audit_logs`.

### Phase 6: FastAPI Backend & Streamlit Interactive UI
1. `api/main.py`: FastAPI endpoints for querying invoices, running on-demand invoice audits, and retrieving risk metrics.
2. `dashboard/app.py`: Streamlit interface with:
   - Executive KPI cards (Total Audited, Flagged Fraud Amount, Audit prep time reduced).
   - Anomaly inspection table with risk filters.
   - Detailed Inspector View showing extracted layout tokens, vector similarity matches, and the agentic LLM audit brief.

---

## EXECUTION DIRECTIVE
Begin with Phase 1. Run the terminal verification, inspect existing files, execute commands step-by-step, and report status as you finish each phase.