// HeatmapOverlay — renders an 8×8 sharpness grid over the image preview.
// High value (1.0) = sharp (green), low (0.0) = blurry (red).

const lerp = (a, b, t) => Math.round(a + (b - a) * t)
const heatColor = (v) => {
  // red (blurry) → yellow → green (sharp)
  if (v < 0.5) {
    const t = v * 2
    return `rgb(239,${lerp(68,200,t)},68)`
  } else {
    const t = (v - 0.5) * 2
    return `rgb(${lerp(200,16,t)},${lerp(200,185,t)},${lerp(68,129,t)})`
  }
}

export default function HeatmapOverlay({ heatmap }) {
  if (!heatmap || !heatmap.length) return null
  const rows = heatmap.length
  const cols = heatmap[0].length

  return (
    <div id="heatmap-overlay">
      <p className="section-title">🗺️ Sharpness Heatmap (8×8 grid)</p>
      <div
        className="heatmap-grid"
        style={{ gridTemplateColumns: `repeat(${cols}, 1fr)`, width: '100%', maxWidth: 320 }}
      >
        {heatmap.flat().map((v, i) => (
          <div
            key={i}
            className="heatmap-cell"
            title={`Cell sharpness: ${(v * 100).toFixed(1)}%`}
            style={{ background: heatColor(v), opacity: 0.75, minHeight: 32 }}
          />
        ))}
      </div>
      <p className="text-muted" style={{ marginTop: '0.4rem' }}>
        🔴 Blurry → 🟢 Sharp
      </p>
    </div>
  )
}
