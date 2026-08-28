# ImageIQ — AI-Powered Image Quality & Defect Detector

> A full-stack application that evaluates image quality using Computer Vision feature engineering and a trained Random Forest classifier — **no external AI APIs required**.

---

## Quick Start (Docker)

```bash
git clone <repo>
cd image-quality-detector

# 1. Train the model first (only needed once)
cd backend
pip install -r requirements.txt
python ml/generate_dataset.py   # Downloads ~80 clean images, generates 1,520 labeled samples
python ml/train.py              # Trains Random Forest, saves artifacts to ml/artifacts/
python ml/evaluate.py           # Generates confusion matrix, ROC curves, classification report
cd ..

# 2. Start both services
docker compose up --build

# App: http://localhost:3000
# API docs: http://localhost:8000/docs
```

---

## Local Development (without Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
python ml/generate_dataset.py
python ml/train.py
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev   # http://localhost:5173
```

---

## How the AI/ML Works

### Feature Engineering (Computer Vision)

8 hand-crafted features are extracted from every uploaded image:

| Feature | Computation | Defect Detected |
|---------|------------|-----------------|
| `laplacian_variance` | Variance of Laplacian second-derivative | **Blur** — low variance = smooth edges = blurry |
| `mean_brightness` | Mean pixel intensity [0–255] | **Under/Overexposure** — <50 dark, >200 bright |
| `brightness_std` | Std dev of pixel intensities | **Exposure confidence** — very low = flat histogram |
| `noise_estimate` | Mean abs diff vs GaussianBlur(5,5) | **Noise** — high freq energy above smooth baseline |
| `contrast_rms` | std(I) / mean(I) | **Corruption** — low ratio = flat/damaged image |
| `edge_density` | Canny edge pixel fraction | **Sharpness support** — blurry = sparse edges |
| `saturation_mean` | Mean HSV-S channel | **Visual defects** — colour shift / desaturation |
| `histogram_entropy` | Shannon entropy of luminance hist | **Corruption** — zeroed blocks = low entropy |

### Model

- **Algorithm:** `RandomForestClassifier(n_estimators=300, class_weight='balanced')`
- **Training data:** 1,520 images — 80 clean + 1,440 synthetically degraded (6 defect types × 3 severity levels × 80 images)
- **Split:** 80/20 stratified train/test
- **Explainability:** RF feature importances returned in every API response; sharpness heatmap (8×8 spatial grid) also included

### Data Generation

Clean images are downloaded from [Lorem Picsum](https://picsum.photos) (royalty-free). Six degradation functions are applied programmatically:

- **Blur** — `cv2.GaussianBlur` with increasing kernel sizes (9, 19, 31)
- **Underexposure** — gamma darkening (γ = 1.8, 2.8, 4.0)
- **Overexposure** — gamma brightening (γ = 0.6, 0.35, 0.2)
- **Noise** — Gaussian noise (σ = 15, 35, 60)
- **Corruption** — Random block zeroing / scrambling (3, 8, 15 blocks)
- **Visual defect** — Channel shift + saturation reduction

### Quality Scoring

```
quality_score = max(0, 100 − Σ(penalty_i × confidence_i))

Penalties: blur/corruption=30, under/over-exposure=20, visual_defect=20, noise=15
Thresholds: ≥75 → ACCEPTABLE | 45–74 → DEGRADED | <45 → DEFECTIVE
```

---

## Evaluation Results

> Run `python ml/evaluate.py` to regenerate all plots.

- Confusion matrix: `ml/artifacts/eval_plots/confusion_matrix.png`
- ROC curves (one-vs-rest): `ml/artifacts/eval_plots/roc_curves.png`
- Feature importances: `ml/artifacts/eval_plots/feature_importance.png`
- Full report: `ml/artifacts/eval_plots/classification_report.txt`

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health + model status |
| `/analyze` | POST | Upload image → quality analysis |
| `/results` | GET | List past analyses (paginated) |
| `/results/{id}` | GET | Get single analysis by ID |
| `/docs` | GET | Interactive Swagger UI |

### Example

```bash
# Analyze an image
curl -X POST http://localhost:8000/analyze \
  -F "file=@/path/to/photo.jpg"

# List results
curl http://localhost:8000/results?limit=10

# Health check
curl http://localhost:8000/health
```

### Response Schema

```json
{
  "id": "uuid",
  "filename": "photo.jpg",
  "quality_score": 72.0,
  "quality_label": "DEGRADED",
  "issues": [
    { "issue": "blur", "confidence": 0.88, "severity": "medium" }
  ],
  "features": {
    "laplacian_variance": 45.2,
    "mean_brightness": 128.4,
    ...
  },
  "feature_importance": { "blur": { "laplacian_variance": 0.72, ... } },
  "heatmap": [[0.9, 0.4, ...], ...],
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Architecture

```
┌─────────────────┐     HTTP      ┌──────────────────────────────┐
│  React Frontend │ ──────────── │  FastAPI Backend              │
│  (Vite + CSS)   │             │  ├─ /analyze  POST             │
│  Port 3000      │             │  ├─ /results  GET              │
└─────────────────┘             │  └─ /health   GET              │
                                │                                │
                                │  ┌─ Feature Extractor (CV)     │
                                │  ├─ Random Forest Model        │
                                │  ├─ Quality Scorer             │
                                │  └─ Sharpness Heatmap          │
                                │                                │
                                │  SQLite DB (SQLAlchemy)        │
                                └──────────────────────────────┘
```

---

## Known Limitations

- Model trained on **synthetic** degradations — may behave differently on real-world defect images not well-represented by the training distribution
- Sharpness heatmap uses Laplacian variance only — does not detect localised noise or colour issues spatially
- SQLite is used for simplicity — swap `DATABASE_URL` to a Postgres connection string for production

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## Project Structure

```
image-quality-detector/
├── backend/
│   ├── app/           # FastAPI application
│   ├── ml/            # Data generation, training, evaluation
│   ├── tests/         # pytest test suite
│   └── Dockerfile
├── frontend/
│   ├── src/           # React + Vite app
│   └── Dockerfile
├── data/              # Generated dataset (gitignored)
├── docker-compose.yml
└── README.md
```
