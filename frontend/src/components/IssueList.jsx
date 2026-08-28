const ISSUE_ICONS = {
  blur:          '🌫️',
  underexposure: '🌑',
  overexposure:  '☀️',
  noise:         '📡',
  corruption:    '💥',
  visual_defect: '🎨',
}

const barColor = (conf) => {
  if (conf >= 0.75) return '#ef4444'
  if (conf >= 0.55) return '#f59e0b'
  return '#6366f1'
}

export default function IssueList({ issues }) {
  if (!issues || issues.length === 0) {
    return <p className="clean-msg">✅ No issues detected — image looks great!</p>
  }

  return (
    <div className="issue-list" id="issue-list">
      {issues.map((issue, i) => (
        <div className="issue-item" key={i} id={`issue-${issue.issue}`}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '1.4rem' }}>{ISSUE_ICONS[issue.issue] || '⚠️'}</span>
            <div>
              <div className="issue-name">{issue.issue.replace('_', ' ')}</div>
              <span className={`sev-${issue.severity}`}>{issue.severity}</span>
            </div>
          </div>
          <div className="issue-right">
            <div className="confidence-bar-wrap">
              <div
                className="confidence-bar"
                style={{
                  width: `${issue.confidence * 100}%`,
                  background: barColor(issue.confidence),
                }}
              />
            </div>
            <span style={{ color: '#94a3b8', fontSize: '0.82rem', minWidth: '38px' }}>
              {Math.round(issue.confidence * 100)}%
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
