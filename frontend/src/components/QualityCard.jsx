const LABEL_COLOR = {
  ACCEPTABLE: '#10b981',
  DEGRADED:   '#f59e0b',
  DEFECTIVE:  '#ef4444',
}

export default function QualityCard({ score, label }) {
  const color = LABEL_COLOR[label] || '#6366f1'
  const r = 54
  const circ = 2 * Math.PI * r
  const dash = circ * (1 - score / 100)

  return (
    <div className="card score-ring-wrap" id="quality-card">
      <svg width="140" height="140" viewBox="0 0 140 140">
        {/* Track */}
        <circle cx="70" cy="70" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10" />
        {/* Progress */}
        <circle
          cx="70" cy="70" r={r}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={dash}
          transform="rotate(-90 70 70)"
          style={{ transition: 'stroke-dashoffset 1s ease, stroke 0.5s' }}
        />
        <text x="70" y="70" textAnchor="middle" dominantBaseline="central"
          fill={color} fontSize="26" fontWeight="800" fontFamily="Inter">
          {score}
        </text>
      </svg>
      <div className={`quality-badge badge-${label}`} id="quality-badge">
        <span>{label === 'ACCEPTABLE' ? '✅' : label === 'DEGRADED' ? '⚠️' : '🚫'}</span>
        {label}
      </div>
      <p className="text-muted" style={{ fontSize: '0.8rem', textAlign: 'center' }}>Quality Score / 100</p>
    </div>
  )
}
