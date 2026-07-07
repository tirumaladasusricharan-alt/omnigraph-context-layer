# 🧠 Analytos Context Layer — Omnigraph POC

> A governed, single-source-of-truth **context layer** for Analytos, built on top of the open-source **Omnigraph** engine — with human-in-the-loop review, agent-scoped access control, and automated testing.

![Python](https://img.shields.io/badge/Python-65.5%25-3776AB?logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-22.9%25-3178C6?logo=typescript&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-10.6%25-1572B6?logo=css3&logoColor=white)
![License](https://img.shields.io/badge/status-proof--of--concept-yellow)

---

## 📖 Overview

Most organizations scatter their product knowledge — feature specs, customer personas, incident threads, metrics — across docs, emails, and tribal memory. This makes it nearly impossible for AI agents (or new hires) to answer questions *accurately* and *safely*.

**Analytos Context Layer** solves this by turning unstructured company knowledge into a **governed knowledge graph**:

- Unstructured docs (`.md` files, email threads, product overviews) are parsed into structured graph nodes.
- Every change lands on an isolated branch and goes through **human review** before merging into the main graph.
- Downstream **AI agents** query the graph exclusively through an MCP tool layer, gated by **Cedar policy rules** — so an agent can be *scoped* to only see what it's allowed to see (e.g., a marketing agent can read `Product`/`Feature`/`Metric` nodes but is denied access to sensitive `EmailThread` nodes).

This repo is a working, runnable proof-of-concept of that entire pipeline.

---

## 🏗️ Architecture

```
Unstructured Docs ──▶ Ingestion Pipeline ──▶ Isolated Branch ──▶ HITL Review Dashboard ──▶ Main Graph
 (.md, email threads)      (ingest.py)          (graph mutation)      (React + FastAPI)         │
                                                                                                   ▼
                                                                              Agents ──▶ MCP Tool Layer ──▶ Cedar Policy Engine
                                                                        (content_agent.py,           (mcp_config.json)   (policy.yaml)
                                                                         gtm_agent.py)
```

| Component | Path | Responsibility |
|---|---|---|
| **Ingestion Pipeline** | `ingest.py` | Uses Google Gemini (`google-genai`) with strict **Pydantic** schemas to idempotently parse unstructured source documents into structured graph mutations on isolated branches. |
| **Graph Schema** | `schema.pg`, `cluster.yaml` | Defines the property-graph schema and cluster topology for the Omnigraph backend. |
| **Query Layer** | `queries.gq` | GraphQL-style queries used to read from the knowledge graph. |
| **Review Dashboard (Backend)** | `dashboard/backend`, `main.py` | FastAPI service exposing endpoints to diff, review, and merge branch changes into the main graph. Runs at `http://127.0.0.1:8000/docs`. |
| **Review Dashboard (Frontend)** | `dashboard/frontend`, `App.tsx`, `main.tsx`, `App.css`, `index.html` | Vite + React "Review Surface" and "Knowledge Browser" UI with a glassmorphism design. |
| **Agent Layer** | `content_agent.py`, `gtm_agent.py` | Python agents that simulate real workflows — writing content, building GTM briefs — by reading the graph through the governed MCP layer. |
| **Access Policy** | `policy.yaml`, `mcp_config.json` | Cedar-based policy rules that scope exactly which node types each agent role may read. |
| **Test Harness** | `run_tests.py` | Unified script that exercises the full agent + security pipeline in one run. |
| **Seed Data** | `icp-analytos.md`, `stockly-product-overview.md`, `inspectly-product-overview.md`, `email-01-stockly-pilot-thread.md`, `email-02-inspectly-medical-thread.md` | Mock organizational knowledge (ICPs, product docs, email threads) used to populate and demo the graph. |

---

## 🧩 Tech Stack

**Backend**
- Python 3
- `fastapi==0.104.1`
- `uvicorn==0.24.0`
- `pydantic==2.5.2`
- `google-genai` (Gemini 2.5 Flash) for document parsing
- Cedar policy engine for access control

**Frontend** (`analytos-dashboard`)
- React `^18.2.0`
- TypeScript `^5.0.2`
- Vite `^4.4.5`

---

## 🚀 Getting Started

### 1. Prerequisites

- Node.js
- Python 3
- A Gemini API key

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 2. Run the unified test suite (agents + security)

The fastest way to validate the whole pipeline — agent behavior *and* Cedar security gating — in one shot:

```bash
python run_tests.py
```

This will:
1. Run the **Content Agent** — verifying it writes a blog post citing 3 correct metrics, and confirming it is explicitly **denied** access to email threads by the Cedar policy.
2. Run the **GTM Agent** — verifying it builds a GTM brief using the correct customer personas.

### 3. Spin up the dashboard for human-in-the-loop review

**Backend:**
```bash
cd dashboard/backend
pip install -r requirements.txt
python main.py
```


**Frontend** (in a new terminal):
```bash
cd dashboard/frontend
npm install
npm run dev
```

Navigate to the dev server URL to explore the **Review Surface** and **Knowledge Browser**.

---

## 🔐 Access Control Model

Agent access to the graph is not implicit — it's explicitly scoped per role via Cedar policy (`policy.yaml`), enforced at the MCP tool boundary. For example, the `content-agent` role is permitted to read only `Product`, `Feature`, and `Metric` nodes — it cannot traverse into `EmailThread` nodes, even ones logically connected to a product it can see.

---

## 🧠 Evaluator Q&A (Demo Reference)

These are worked examples showing how the graph resolves multi-hop questions and enforces access control, based on the mock seed data:

**Q1 — Metric lookup:** *"What metric should an agent cite when writing about Inspectly's time-saving benefits?"*
→ A **60% reduction** in Audit Prep Time (4 weeks → 1.5 weeks).
Trace: `Product(inspectly)` → `Feature(auto-audit-log)` → `Metric(audit-prep-time)`

**Q2 — Persona targeting:** *"Who should a sales rep contact when selling the Auto-Restock feature, and what's the pain point?"*
→ The **Supply Chain Manager** at a Mid-Market Retail company, whose core pain points are manual spreadsheet overload and stockout risk during peak seasons.
Trace: `Product(stockly)` → `ICPSegment(retail-mid-market)` → `Persona(supply-chain-manager)`

**Q3 — Access control:** *"Can the Content Agent see the MedTech Corp audit-log failure incident?"*
→ **No.** That incident lives in an `EmailThread` node. The `content-agent` Cedar policy only grants read access to `Product`, `Feature`, and `Metric` nodes — so the request is blocked at policy evaluation, not at the application layer.
Trace: attempted `EmailThread(email-02-inspectly-medical-thread)` access → blocked by Cedar.

---

## 📂 Repository Structure

```
omnigraph-context-layer/
├── ingest.py                          # Document → graph mutation pipeline
├── content_agent.py                   # Content-writing agent (scoped access)
├── gtm_agent.py                       # GTM brief-building agent
├── run_tests.py                       # Unified agent + security test runner
├── main.py                            # FastAPI dashboard backend entrypoint
├── App.tsx / main.tsx / App.css       # React dashboard frontend
├── index.html                         # Frontend entry
├── schema.pg                          # Property-graph schema
├── cluster.yaml                       # Graph cluster config
├── queries.gq                         # Graph query definitions
├── policy.yaml                        # Cedar access-control policy
├── mcp_config.json                    # MCP tool layer config
├── icp-analytos.md                    # Seed: ICP definitions
├── stockly-product-overview.md        # Seed: product doc
├── inspectly-product-overview.md      # Seed: product doc
├── email-01-stockly-pilot-thread.md   # Seed: email thread
├── email-02-inspectly-medical-thread.md # Seed: sensitive email thread (access-restricted)
├── requirements.txt                   # Backend dependencies
├── package.json                       # Frontend dependencies
└── tsconfig*.json / vite.config.ts    # Frontend build config
```

---

## 🗺️ Roadmap Ideas

- [ ] Add authentication to the review dashboard
- [ ] Expand Cedar policies to cover write/merge permissions per role
- [ ] Add CI workflow to run `run_tests.py` on every PR
- [ ] Persist branch history for audit trail
- [ ] Add more seed products/personas to stress-test graph traversal

---

## 📄 License

No license file currently specified — add one (MIT/Apache-2.0 recommended) before treating this as reusable beyond the POC.
