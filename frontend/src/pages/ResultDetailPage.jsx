import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getResult } from '../api/client'
import QualityCard from '../components/QualityCard'
import IssueList from '../components/IssueList'
import FeatureStats from '../components/FeatureStats'
import HeatmapOverlay from '../components/HeatmapOverlay'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ResultDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getResult(id)
      .then(res => setResult(res.data))
      .catch(() => setError('Result not found.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="page"><div className="spinner" /></div>
  if (error)   return <div className="page"><p style={{color:'var(--danger)'}}>{error}</p></div>

  return (
    <div className="page" id="result-detail-page">
      <div style={{ display:'flex', alignItems:'center', gap:'1rem', marginBottom:'1.5rem' }}>
        <button className="btn btn-ghost" onClick={() => navigate('/history')}>← Back</button>
        <div>
          <h1 style={{ fontSize:'1.5rem', fontWeight:800 }}>
            Analysis: <span style={{color:'var(--accent)'}}>{result.filename}</span>
          </h1>
          <p style={{color:'var(--text-muted)', fontSize:'0.82rem'}}>
            {new Date(result.created_at).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Image preview from stored thumbnail */}
      {result.thumbnail_url && (
        <div className="card" style={{marginBottom:'1.5rem', padding:'1rem'}}>
          <p className="section-title">Uploaded Image</p>
          <img
            src={`${API_BASE}${result.thumbnail_url}`}
            alt={result.filename}
            style={{ maxHeight:280, maxWidth:'100%', borderRadius:8, objectFit:'cover', display:'block' }}
          />
        </div>
      )}

      <div className="results-grid">
        <div style={{ display:'flex', flexDirection:'column', gap:'1.5rem' }}>
          <QualityCard score={result.quality_score} label={result.quality_label} />
          <div className="card">
            <HeatmapOverlay heatmap={result.heatmap} />
          </div>
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:'1.5rem' }}>
          <div className="card">
            <p className="section-title">Detected Issues ({result.issues.length})</p>
            <IssueList issues={result.issues} />
          </div>
          <div className="card">
            <FeatureStats features={result.features} />
          </div>
        </div>
      </div>
    </div>
  )
}
