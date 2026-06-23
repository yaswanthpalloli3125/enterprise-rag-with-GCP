Enterprise Agentic RAG
A production-grade RAG system built with LangGraph, NeMo Guardrails, Portkey LLM Gateway, RAGAS Evals, and Google Cloud Platform. Deployed as four independent microservices on Cloud Run, managed entirely with Terraform.

Key Features
Agentic Intelligence — LangGraph cyclic graph: Planner → Retriever → Responder with persistent memory across sessions
Two-Gate Safety — Gate 1: NeMo Guardrails (blocks jailbreak/off-topic); Gate 2: Redis Semantic Cache (serves cached answers in ~50ms)
Persistent Memory — LangGraph PostgresSaver on Cloud SQL — conversation history survives container restarts and scale-to-zero
LLM Gateway — Portkey routes all LLM calls with automatic fallback (Llama 3.3 70B → Llama 3.1 8B), full dashboard visibility
Enterprise Search — Qdrant Cloud vector search + FlashRank local reranker
Event-Driven Ingestion — Upload a file to GCS → Eventarc fires → Ingestion service auto-parses, embeds, and indexes. No manual steps.
Evaluation Suite — RAGAS (5 metrics) + Jaccard Tool Correctness. GCS-persisted history. Deployed as its own Cloud Run service.
Full Observability — Pydantic Logfire + LangSmith traces across every agent node and eval run
Architecture
Monolithic (v1)
The original single-process application — all components in one container, in-memory state, manual ingestion.


Scalable Enterprise (v2 — current)
Four independent microservices, event-driven ingestion, persistent memory, semantic caching, and full IaC via Terraform.


Project Structure
├── app/
│   ├── agents/
│   │   ├── graph.py              # LangGraph graph + PostgresSaver checkpointer
│   │   ├── state.py              # AgentState schema
│   │   └── nodes/
│   │       ├── planner.py        # Intent classification node
│   │       ├── retriever.py      # Qdrant search + FlashRank reranker node
│   │       └── responder.py      # Answer generation node
│   ├── gateway/
│   │   └── client.py             # Portkey LLM gateway — primary + fallback routing
│   ├── guardrails/
│   │   ├── rails.py              # NeMo Guardrails integration
│   │   └── colang_rules.py       # Block/allow rule definitions
│   ├── ingestion/
│   │   ├── processor.py          # Dual-mode: CLI bulk load + Eventarc webhook (POST /ingest)
│   │   ├── chunking/
│   │   │   └── splitter.py       # Text splitting strategies
│   │   └── loaders/
│   │       ├── pdf.py            # Google Document AI PDF parser
│   │       ├── html.py           # HTML parser
│   │       ├── office.py         # DOCX / PPTX parser
│   │       └── text.py           # Plain text parser
│   ├── services/
│   │   ├── gcp/
│   │   │   ├── database_service.py      # psycopg3 connection pool (unix socket)
│   │   │   └── redis_semantic_cache.py  # Cosine-distance semantic cache
│   │   └── retrieval/
│   │       ├── embedding.py      # Vertex AI text-embedding-004 (lazy-loaded)
│   │       ├── qdrant_service.py # Vector search client
│   │       └── ranking_service.py # FlashRank reranker
│   ├── config.py                 # Centralized env var management
│   └── main.py                   # FastAPI entrypoint — two gates + /query
│
├── evals/
│   ├── app.py                    # Streamlit 4-tab eval dashboard
│   ├── pipeline.py               # Phase 1 — live /query calls + Groq summarization
│   ├── metrics.py                # Phase 2 — RAGAS scoring with GoogleEmbeddings
│   ├── guardrails_eval.py        # Guardrails TP/TN/FP/FN classification
│   ├── store.py                  # GCS persistence for eval history
│   ├── data_parser.py            # Golden dataset document parser
│   └── golden_dataset.json       # 15 RAG samples + 6 guardrail test cases
│
├── ui/
│   └── app.py                    # Streamlit chat interface
│
├── docker/
│   ├── backend.Dockerfile        # FastAPI + LangGraph + Guardrails + Redis + Postgres
│   ├── ui.Dockerfile             # Streamlit only (4 packages)
│   ├── ingestion.Dockerfile      # DocAI + Qdrant + parsers
│   └── evals.Dockerfile          # RAGAS + Vertex AI + Streamlit
│
├── terraform/
│   ├── main.tf                   # VPC, GCS buckets, Redis, Eventarc SA IAM
│   ├── cloud_run.tf              # All 4 Cloud Run services + public IAM
│   ├── database.tf               # Cloud SQL Postgres 15
│   ├── ingestion.tf              # Ingestion service + Eventarc trigger (POST /ingest)
│   ├── variables.tf              # Input variable declarations
│   ├── provider.tf               # GCP + hashicorp/time providers
│   └── output.tf                 # backend_url, ui_url, evals_url, ingestion_url
│
├── notebooks/
│   ├── 01_guardrails.ipynb       # NeMo Guardrails walkthrough
│   ├── 02_llm_gateway.ipynb      # Portkey gateway exploration
│   └── 03_evals.ipynb            # RAGAS metrics walkthrough
│
├── DATA/
│   └── true_data/                # Golden documents (Kubernetes, Databricks)
│
├── DOCS/                         # 24 architectural and operational guides
├── cloudbuild.yaml               # Parallel build of all 4 Docker images
├── cloudbuild-evals.yaml         # Targeted evals-only rebuild
├── requirements.txt              # Monolith / local dev dependencies
├── requirements-backend.txt      # Backend service dependencies
├── requirements-evals.txt        # Evals service dependencies
├── requirements-ingestion.txt    # Ingestion service dependencies
└── requirements-ui.txt           # UI service dependencies (4 packages)
Tech Stack
Layer	Technology
Agent Orchestration	LangGraph (cyclic graph)
LLMs	Groq Llama 3.3 70B + 3.1 8B via Portkey gateway
Guardrails	NeMo Guardrails (Gate 1)
Semantic Cache	Redis Memorystore + Vertex AI embeddings (Gate 2)
Persistent Memory	LangGraph PostgresSaver on Cloud SQL Postgres 15
Vector DB	Qdrant Cloud
Reranking	FlashRank (local, zero-latency)
Embeddings	Vertex AI text-embedding-004
Document Parsing	Google Document AI (PDF OCR)
Auto-Ingestion	GCS → Eventarc → Cloud Run (internal)
Evaluation	RAGAS (5 metrics) + Jaccard Tool Correctness
Eval Storage	GCS (eval-results/ prefix, persists across restarts)
Observability	Pydantic Logfire + LangSmith + Portkey Dashboard
Compute	Google Cloud Run (4 independent microservices)
IaC	Terraform (VPC, Cloud SQL, Redis, Eventarc, Cloud Run)
CI/CD	Google Cloud Build (parallel 4-image build)
Networking	Direct VPC Egress (no connector)
Getting Started
Local development
python -m venv tenvv
source tenvv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
Create .env — see DOCS/07_ENVIRONMENT_VARIABLES.md for all required keys.

# Ingest documents locally
python -m app.ingestion.processor DATA/true_data

# Terminal 1 — backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — UI
streamlit run ui/app.py

# Terminal 3 — evals (optional)
streamlit run evals/app.py
Cloud deployment (scalable)
See commands_scalable.md for the full step-by-step. High level:

# 1. Create AR repo first
cd terraform && terraform apply -target=google_artifact_registry_repository.repo

# 2. Build all 4 Docker images in parallel
cd .. && gcloud builds submit --config cloudbuild.yaml --project=YOUR_PROJECT .

# 3. Deploy everything
cd terraform && terraform apply
Outputs: backend_url, ui_url, evals_url, ingestion_url

Documentation Index
#	Guide	What it covers
1	System Overview	High-level vision and end-to-end flow
2	Ingestion Engine	Document parsing and indexing pipeline
3	Node Intelligence	Planner, Retriever, Responder internals
4	Observability	Logfire + LangSmith tracing
5	GCP Prod Setup	Step-by-step infrastructure provisioning (monolith)
6	Deployment Strategy	Cloud Build and Cloud Run details
7	Env Variables	Complete configuration dictionary
8	GCP Roles & Services	IAM and service breakdown
9	Infra Architecture	The 3-tier cloud blueprint
10	Redis Caching	Semantic cache — cosine distance, Gate 2 design
11	Microservices Transition	Scaling beyond monolith
12	Known Gotchas	GCP quirks — Eventarc SA, HCL syntax, tfvars secrets
13	FlashRank Reranking	Local semantic reranker deep-dive
14	VPC Networking	Direct VPC egress — Cloud SQL unix socket
15	Guardrails	NeMo Guardrails implementation
16	LLM Gateway	Portkey routing, fallback, and observability
17	Evals	RAGAS metrics theory, token budget, rate limit strategy
18	Evals Pipeline	Live eval pipeline, GCS persistence, ~75 min runtime
19	Scaling Migration	Monolith → microservices roadmap (5 phases)
20	Postgres Memory	PostgresSaver — unix socket, hybrid LOCAL_MODE
21	Eventarc Ingestion	Event-driven ingestion — feedback loop fix, IAM
22	Semantic Cache	Redis semantic cache — threshold tuning, business impact
23	Microservices & Docker	4 Dockerfiles, split requirements, layer caching
24	Terraform IaC	Full Terraform reference — deployment order, gotchas
Built for High-Scale Enterprise Document Intelligence.