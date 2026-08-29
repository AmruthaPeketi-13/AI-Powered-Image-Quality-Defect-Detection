import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getResults, thumbnailUrl } from '../api/client'

const LABEL_COLORS = { ACCEPTABLE: '#10b981', DEGRADED: '#f59e0b', DEFECTIVE: '#ef4444' }

export default function HistoryPage() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getResults()
      .then(res => setRecords(res.data))
      .catch(() => setRecords([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page"><div className="spinner" /></div>

  return (
    <div className="page" id="history-page">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '0.3rem' }}>
        Analysis <span style={{ color: 'var(--accent)' }}>History</span>
      </h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        {records.length} past analysis{records.length !== 1 ? 'es' : ''} — click any row to view details.
      </p>

      {records.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          No analyses yet. <a href="/" style={{ color: 'var(--accent)' }}>Upload an image</a> to get started.
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="history-table" id="history-table">
            <thead>
              <tr>
                <th style={{ width: 64 }}>Image</th>
                <th>Filename</th>
                <th>Score</th>
                <th>Label</th>
                <th>Issues</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {records.map(r => (
                <tr key={r.id} onClick={() => navigate(`/results/${r.id}`)}>
                  <td>
                    {r.thumbnail_url ? (
                      <img
                        src={thumbnailUrl(r.thumbnail_url)}
                        alt={r.filename}
                        style={{ width: 48, height: 48, objectFit: 'cover', borderRadius: 6, display: 'block' }}
                        onError={e => { e.target.style.display = 'none' }}
                      />
                    ) : (
                      <div style={{ width: 48, height: 48, background: 'rgba(255,255,255,0.05)', borderRadius: 6, display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1.2rem' }}>🖼️</div>
                    )}
                  </td>
                  <td style={{ fontWeight: 500 }}>{r.filename}</td>
                  <td style={{ fontWeight: 700, color: LABEL_COLORS[r.quality_label] }}>
                    {r.quality_score}
                  </td>
                  <td>
                    <span className={`quality-badge badge-${r.quality_label}`} style={{ fontSize: '0.72rem' }}>
                      {r.quality_label}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{r.issue_count}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                    {new Date(r.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
