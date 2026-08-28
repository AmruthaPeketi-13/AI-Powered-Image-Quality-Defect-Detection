const FEATURE_LABELS = {
  laplacian_variance: 'Sharpness (Laplacian Var.)',
  mean_brightness:    'Mean Brightness',
  brightness_std:     'Brightness Std Dev',
  noise_estimate:     'Noise Estimate',
  contrast_rms:       'RMS Contrast',
  edge_density:       'Edge Density',
  saturation_mean:    'Saturation Mean',
  histogram_entropy:  'Histogram Entropy',
}

export default function FeatureStats({ features }) {
  if (!features) return null
  return (
    <div id="feature-stats">
      <p className="section-title">Raw CV Features</p>
      <table className="feature-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(features).map(([k, v]) => (
            <tr key={k}>
              <td>{FEATURE_LABELS[k] || k}</td>
              <td>{typeof v === 'number' ? v.toFixed(4) : v}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
