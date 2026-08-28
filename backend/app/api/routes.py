"""API route handlers — /analyze, /results, /health."""
import json
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.api.schemas import AnalysisListItem, AnalysisResponse, HealthResponse
from app.config import settings
from app.core.explainer import build_feature_importance, compute_sharpness_heatmap
from app.core.feature_extractor import extract_features
from app.core.model import model_is_ready, predict
from app.core.quality_scorer import compute_quality_score
from app.db.database import get_db
from app.db.models import AnalysisResult

UPLOADS_DIR = Path("data/uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()

MAX_BYTES = settings.max_upload_size_mb * 1024 * 1024


# ── /health ──────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    """Service liveness check — also reports whether the ML model is loaded."""
    return HealthResponse(status="ok", model_ready=model_is_ready())


# ── /analyze ─────────────────────────────────────────────────────────────────

@router.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload an image and receive a full quality analysis report.

    - Validates file type and size.
    - Extracts 8 CV features.
    - Runs the trained Random Forest classifier.
    - Returns quality score, quality label, detected issues, raw features,
      feature importances, and an 8×8 sharpness heatmap.
    """
    # --- Validation ---
    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. "
                   f"Allowed: {settings.allowed_content_types}",
        )

    raw = await file.read()
    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(raw) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(raw) / 1e6:.1f} MB). Max: {settings.max_upload_size_mb} MB.",
        )

    # --- Decode image ---
    try:
        pil_img = Image.open(BytesIO(raw))
        pil_img.verify()           # Raises if corrupt
        pil_img = Image.open(BytesIO(raw))  # Re-open after verify (verify closes stream)
        pil_img = pil_img.convert("RGB")
    except (UnidentifiedImageError, Exception) as exc:
        raise HTTPException(status_code=400, detail=f"Cannot read image: {exc}")

    # --- Feature extraction ---
    features = extract_features(pil_img)

    # --- Model inference ---
    if not model_is_ready():
        raise HTTPException(status_code=503, detail="Model not loaded. Run training first.")
    predictions, feat_importance = predict(features)

    # --- Quality score ---
    quality_score, quality_label = compute_quality_score(predictions)

    # --- Heatmap (bonus explainability) ---
    heatmap = compute_sharpness_heatmap(pil_img)

    # --- Persist image to disk (for thumbnail in history) ---
    result_id = str(uuid.uuid4())
    img_save_path = UPLOADS_DIR / f"{result_id}.jpg"
    pil_img.save(str(img_save_path), format="JPEG", quality=85)

    thumbnail_url = f"/uploads/{result_id}.jpg"

    # --- Persist to DB ---
    db_record = AnalysisResult(
        id=result_id,
        filename=file.filename or "unknown",
        quality_score=quality_score,
        quality_label=quality_label,
        issues_json=json.dumps(predictions),
        features_json=json.dumps(features),
        feature_importance_json=json.dumps(feat_importance),
        heatmap_json=json.dumps(heatmap),
        thumbnail_url=thumbnail_url,
        created_at=datetime.now(timezone.utc),
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return AnalysisResponse(
        id=result_id,
        filename=db_record.filename,
        quality_score=quality_score,
        quality_label=quality_label,
        issues=[dict(issue=p["issue"], confidence=p["confidence"], severity=p["severity"]) for p in predictions],
        features=features,
        feature_importance=feat_importance,
        heatmap=heatmap,
        thumbnail_url=thumbnail_url,
        created_at=db_record.created_at,
    )


# ── /results ─────────────────────────────────────────────────────────────────

@router.get("/results", response_model=list[AnalysisListItem], tags=["Results"])
def list_results(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Return paginated list of past analyses (newest first)."""
    records = (
        db.query(AnalysisResult)
        .order_by(AnalysisResult.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        AnalysisListItem(
            id=r.id,
            filename=r.filename,
            quality_score=r.quality_score,
            quality_label=r.quality_label,
            issue_count=len(r.issues),
            thumbnail_url=r.thumbnail_url,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/results/{result_id}", response_model=AnalysisResponse, tags=["Results"])
def get_result(result_id: str, db: Session = Depends(get_db)):
    """Retrieve a single analysis result by ID."""
    record = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Result not found.")
    return AnalysisResponse(
        id=record.id,
        filename=record.filename,
        quality_score=record.quality_score,
        quality_label=record.quality_label,
        issues=record.issues,
        features=record.features,
        feature_importance=record.feature_importance,
        heatmap=json.loads(record.heatmap_json) if record.heatmap_json else None,
        thumbnail_url=record.thumbnail_url,
        created_at=record.created_at,
    )
