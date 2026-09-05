# Project Context & Persona: ProcureAI

## User Profile & Constraints
- Role Target: AI Engineer (every decision, model, and system architecture must align with senior AI Engineer hiring bars).
- Local Hardware: Apple Silicon Mac (M1, 8 GB unified RAM, CPU-only, 256 GB SSD). Memory efficiency is paramount; use asymmetric architectures (local lightweight models + external APIs for heavy reasoning).
- Background: Past enterprise experience at Mindtree.

## Core Directives & Rules
- Ask clarifying questions sequentially, one at a time. Never batch questions.
- Maintain industrial-grade engineering complexity. Never build toy scripts or simplistic flat CSV demos.
- Real Seed Data: Seed with real public datasets (ICDAR SROIE-2019, Kaggle Procurement Invoice Fraud) and scale via generative augmentation to 250,000+ invoices.
- Reference Architectures: Reference production blueprints like `Agentic-Procure-Audit-AI`.

## ProcureAI Tech Stack & Architecture
- Storage: PostgreSQL 16 + pgvector (installed via Homebrew).
- Document Extraction: LayoutLMv3-base or Florence-2-base (lightweight vision-language extraction).
- Semantic Search: sentence-transformers (e.g., all-MiniLM-L6-v2) for fuzzy vendor/item duplicate matching.
- Anomaly & Risk Engine: Hybrid XGBoost tabular risk classification + pgvector similarity search.
- Agentic Audit Reasoning: Multi-step verification agent using Gemini Flash API to produce structured audit briefs with cited policy violations.
- Interface: FastAPI backend + Streamlit dashboard.
