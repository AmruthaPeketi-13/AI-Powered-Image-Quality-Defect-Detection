import { useState, useCallback } from 'react'
import DropZone from '../components/DropZone'
import QualityCard from '../components/QualityCard'
import IssueList from '../components/IssueList'
import FeatureStats from '../components/FeatureStats'
import HeatmapOverlay from '../components/HeatmapOverlay'
import { analyzeImage } from '../api/client'

export default function AnalyzePage() {
  const [preview, setPreview]   = useState(null)
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const [progress, setProgress] = useState(0)

  const handleFile = useCallback(async (file) => {
    setError(null)
    setResult(null)
    setProgress(0)

    // Show local preview
    const url = URL.createObjectURL(file)
    setPreview(url)
    setLoading(true)

    try {
      const res = await analyzeImage(file, setProgress)
      setResult(res.data)
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Analysis failed.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [])

  const reset = () => {
    setPreview(null); setResult(null); setError(null); setProgress(0)
  }

  return (
    <div className="page" id="analyze-page">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '0.4rem' }}>
          Image <span style={{ color: 'var(--accent)' }}>Quality Analyzer</span>
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Upload any image to detect blur, noise, exposure issues, and corruption — powered by CV + ML.
        </p>
      </div>

      {!preview && <DropZone onFile={handleFile} />}

      {preview && (
        <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
          <div className="img-preview-wrap" style={{ flex: '0 0 auto' }}>
            <img src={preview} className="img-preview" alt="Uploaded preview" style={{ maxWidth: 280 }} />
          </div>
          <button className="btn btn-ghost" onClick={reset} id="reset-btn">← Upload another</button>
        </div>
      )}

      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: '2rem' }}>
          <div className="spinner" />
          <p style={{ color: 'var(--text-secondary)' }}>Analyzing image… {progress > 0 ? `${progress}%` : ''}</p>
        </div>
      )}

      {error && (
        <div className="toast toast-error" id="error-toast">⚠️ {error}</div>
      )}

      {result && (
        <div className="results-grid" id="results-panel">
          {/* Left column: score + heatmap */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <QualityCard score={result.quality_score} label={result.quality_label} />
            <div className="card">
              <HeatmapOverlay heatmap={result.heatmap} />
            </div>
          </div>

          {/* Right column: issues + features */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="card">
              <p className="section-title">Detected Issues ({result.issues.length})</p>
              <IssueList issues={result.issues} />
            </div>
            <div className="card">
              <FeatureStats features={result.features} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
