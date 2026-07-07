# Analytos Org Context Layer POC

This repository contains a working proof-of-concept for a governed, single-source-of-truth context layer for Analytos, built on top of the open-source Omnigraph engine.

## Architecture

1. **Ingestion Pipeline (`ingest.py`)**: Uses `google-genai` (Gemini 2.5 Flash) and strict Pydantic structures to idempotently parse unstructured documents into structured graph mutations on isolated branches.
2. **Review Dashboard (`dashboard/`)**: A Vite/React frontend and FastAPI backend where humans can review, diff, and merge branch changes into the main graph.
3. **Agent MCP Access (`agents/`)**: Python agent scripts that simulate reading from the graph via an MCP tool layer securely governed by Cedar policy rules.

---

## 🚀 How to Run

### 1. Prerequisites
Ensure you have Node.js, Python 3, and your LLM API Key ready.
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 2. Run the Unified Test Suite (Agents & Security)
The easiest way to verify the entire agent pipeline and security gating is to run our unified test script:
```bash
python run_tests.py
```
*This will execute the Content Agent (verifying it writes a blog with 3 metrics and gets explicitly denied access to emails by Cedar), followed by the GTM Agent (verifying it builds a brief based on correct personas).*

### 3. Spin up the Dashboard & HITL Review

**Start the FastAPI Backend:**
```bash
cd dashboard/backend
pip install -r requirements.txt
python main.py
```
*(Runs on http://127.0.0.1:8000/docs)*

**Start the React Frontend:**
Open a new terminal window:
```bash
cd dashboard/frontend
npm install
npm run dev
```
*(Runs on http://127.0.0.1:8000)*

Navigate to the frontend URL to view the Glassmorphism styled "Review Surface" and "Knowledge Browser".

---

## 🧠 Evaluator Unseen Logical Questions

On demo day, evaluators may ask agents complex, logical questions to ensure data extraction was accurate and access is properly scoped. Here are three expected examples based on our mock seed data:

**Q1: "If an agent is tasked with writing a blog about Inspectly's time-saving benefits, what exact metric value and context should they cite?"**
- **Expected Answer:** They should cite a **60% reduction** in Audit Prep Time, specifically dropping from 4 weeks down to 1.5 weeks.
- **Node Trace:** Product (`inspectly`) ➔ Feature (`auto-audit-log`) ➔ Metric (`audit-prep-time`).

**Q2: "Which specific persona should a sales rep contact if they are selling the Auto-Restock feature, and what is the primary pain point they need to agitate?"**
- **Expected Answer:** They should target the **Supply Chain Manager** at a Mid-Market Retail company. The primary pain point to agitate is that they are "exhausted by manual excel sheets" and face a "high risk of stockouts during peak seasons."
- **Node Trace:** Product (`stockly`) ➔ ICPSegment (`retail-mid-market`) ➔ Persona (`supply-chain-manager`).

**Q3: "Can the Content Agent access details regarding the MedTech Corp Auto-Audit Log failure incident?"**
- **Expected Answer:** **No.** The details of that incident are housed within an `EmailThread` node (specifically the Sev-1 compliance issue thread). The Cedar policy governing the `content-agent` role explicitly permits read access *only* to `Product`, `Feature`, and `Metric` nodes, resulting in a strict Access Denied response.
- **Node Trace:** Attempt to access EmailThread (`email-02-inspectly-medical-thread`) ➔ Blocked by Cedar Policy evaluation.
