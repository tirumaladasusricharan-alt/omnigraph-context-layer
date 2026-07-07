import React, { useState, useEffect } from 'react'
import './App.css'

interface Branch {
  id: string
  status: string
  created_at: string
}

interface Change {
  commit: string
  message: string
  author: string
  date: string
}

interface SearchResult {
  type: string
  id: string
  snippet: string
  score: number
}

function App() {
  const [branches, setBranches] = useState<Branch[]>([])
  const [recentChanges, setRecentChanges] = useState<Change[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [selectedBranchDiff, setSelectedBranchDiff] = useState<any>(null)
  const [activeBranch, setActiveBranch] = useState<string | null>(null)

  const API_BASE = 'http://localhost:8000'

  useEffect(() => {
    fetchBranches()
    fetchRecentChanges()
  }, [])

  const fetchBranches = async () => {
    try {
      const res = await fetch(`${API_BASE}/branches`)
      const data = await res.json()
      setBranches(data)
    } catch (e) {
      console.error("Failed to fetch branches", e)
    }
  }

  const fetchRecentChanges = async () => {
    try {
      const res = await fetch(`${API_BASE}/recent_changes`)
      const data = await res.json()
      setRecentChanges(data)
    } catch (e) {
      console.error("Failed to fetch recent changes", e)
    }
  }

  const loadDiff = async (branchName: string) => {
    try {
      // url encode branch name because it contains slashes like ingest/2023...
      const encoded = encodeURIComponent(branchName)
      const res = await fetch(`${API_BASE}/branches/${encoded}/diff`)
      const data = await res.json()
      setSelectedBranchDiff(data)
      setActiveBranch(branchName)
    } catch (e) {
      console.error("Failed to load diff", e)
    }
  }

  const handleMerge = async (branchName: string) => {
    try {
      const encoded = encodeURIComponent(branchName)
      await fetch(`${API_BASE}/branches/${encoded}/merge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer_name: 'Sri Charan Tirumaladasu' })
      })
      alert(`Branch ${branchName} merged successfully!`)
      setActiveBranch(null)
      fetchBranches()
      fetchRecentChanges()
    } catch (e) {
      console.error("Failed to merge", e)
    }
  }

  const handleReject = async (branchName: string) => {
    try {
      const encoded = encodeURIComponent(branchName)
      await fetch(`${API_BASE}/branches/${encoded}/reject`, { method: 'POST' })
      alert(`Branch ${branchName} rejected.`)
      setActiveBranch(null)
      fetchBranches()
    } catch (e) {
      console.error("Failed to reject", e)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery) return
    try {
      const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(searchQuery)}`)
      const data = await res.json()
      setSearchResults(data)
    } catch (e) {
      console.error("Search failed", e)
    }
  }

  return (
    <div className="app-container">
      <header>
        <h1>Analytos Context Layer</h1>
        <div className="subtitle">Omnigraph Governance & Knowledge Browser</div>
      </header>

      <div className="dashboard-grid">
        {/* Left Column: HITL Review Surface */}
        <section className="card">
          <h2>HITL Review Surface</h2>
          <p style={{color: 'var(--text-secondary)', marginBottom: '1rem'}}>
            Pending ingestion branches requiring human approval before merging to main.
          </p>
          
          {branches.length === 0 ? (
            <p>No pending branches.</p>
          ) : (
            <ul className="branch-list">
              {branches.map(b => (
                <li key={b.id} className="branch-item">
                  <div className="branch-header">
                    <span className="branch-name">{b.id}</span>
                    <button onClick={() => loadDiff(b.id)} style={{background: 'var(--accent-color)', color: 'white', border: 'none', padding: '0.3rem 0.6rem', borderRadius: '4px', cursor: 'pointer'}}>View Diff</button>
                  </div>
                  
                  {activeBranch === b.id && selectedBranchDiff && (
                    <div style={{marginTop: '1rem'}}>
                      <div className="diff-view">
                        <pre>{JSON.stringify(selectedBranchDiff, null, 2)}</pre>
                      </div>
                      <div className="branch-actions" style={{marginTop: '1rem', display: 'flex', justifyContent: 'flex-end'}}>
                        <button className="btn-reject" onClick={() => handleReject(b.id)}>Reject</button>
                        <button className="btn-approve" onClick={() => handleMerge(b.id)}>Approve & Merge</button>
                      </div>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Right Column: Knowledge Browser */}
        <section style={{display: 'flex', flexDirection: 'column', gap: '2rem'}}>
          
          <div className="card">
            <h2>Knowledge Browser</h2>
            <form onSubmit={handleSearch}>
              <input 
                type="text" 
                className="search-box" 
                placeholder="Search the graph (hybrid retrieval)..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
            </form>
            
            {searchResults.length > 0 && (
              <ul className="search-results">
                {searchResults.map(res => (
                  <li key={res.id} className="search-item">
                    <div style={{display: 'flex', justifyContent: 'space-between'}}>
                      <strong style={{color: 'var(--accent-color)'}}>[{res.type}] {res.id}</strong>
                      <span className="score-badge">Score: {res.score}</span>
                    </div>
                    <p style={{margin: '0.5rem 0 0 0', fontSize: '0.9rem'}}>{res.snippet}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="card">
            <h2>Recent Changes</h2>
            <ul className="changes-list">
              {recentChanges.map(c => (
                <li key={c.commit} className="change-item">
                  <strong>{c.message}</strong>
                  <div className="change-meta">
                    <span>{c.author}</span>
                    <span>{new Date(c.date).toLocaleString()}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>

        </section>
      </div>
    </div>
  )
}

export default App
