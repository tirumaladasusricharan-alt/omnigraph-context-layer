from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
from typing import List, Dict, Any

app = FastAPI(title="Analytos Context Layer Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MergeRequest(BaseModel):
    reviewer_name: str = "Sri Charan Tirumaladasu"

@app.get("/branches")
def list_branches():
    """List open ingestion branches."""
    # Mocking response for POC UI
    return [
        {"id": "ingest/20231012-140000", "status": "open", "created_at": "2023-10-12T14:00:00Z"},
        {"id": "ingest/20231012-153000", "status": "open", "created_at": "2023-10-12T15:30:00Z"}
    ]

@app.get("/branches/{branch_name:path}/diff")
def get_branch_diff(branch_name: str):
    """Fetch structural diff of nodes/edges for a branch."""
    # In real life: run_omnigraph_command(["branch", "diff", branch_name, "--format", "json"])
    return {
        "nodes_added": [
            {"type": "Product", "id": "stockly", "name": "Stockly"},
            {"type": "Feature", "id": "auto-restock", "name": "Auto-Restock"}
        ],
        "edges_added": [
            {"source": "stockly", "target": "auto-restock", "type": "HAS_FEATURE"}
        ]
    }

@app.post("/branches/{branch_name:path}/merge")
def merge_branch(branch_name: str, req: MergeRequest):
    """Merge the branch to main, attributing the commit."""
    # run_omnigraph_command(["branch", "merge", branch_name, "--into", "main", "--author", req.reviewer_name])
    return {"status": "success", "message": f"Branch {branch_name} merged by {req.reviewer_name}"}

@app.post("/branches/{branch_name:path}/reject")
def reject_branch(branch_name: str):
    """Discard a branch."""
    # run_omnigraph_command(["branch", "delete", branch_name])
    return {"status": "success", "message": f"Branch {branch_name} rejected and deleted."}

@app.get("/search")
def search_knowledge(q: str):
    """Search using Omnigraph hybrid retrieval."""
    # run_omnigraph_command(["query", "search", "--params", json.dumps({"q": q})])
    # Mocking for POC:
    return [
        {"type": "Product", "id": "stockly", "snippet": "Stockly is a supply chain management product...", "score": 0.95},
        {"type": "Metric", "id": "conversion-rate", "snippet": "Improved by 15% over 3 months.", "score": 0.88}
    ]

@app.get("/recent_changes")
def get_recent_changes():
    """Get the audit log of recent merges."""
    return [
        {"commit": "a1b2c3d", "message": "Merged ingest/20231011-090000", "author": "Sri Charan Tirumaladasu", "date": "2023-10-11T09:05:00Z"},
        {"commit": "e4f5g6h", "message": "Initial schema setup", "author": "System", "date": "2023-10-10T12:00:00Z"}
    ]

if __name__ == "__main__":
    import uvicorn
    print("Starting backend server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
