"""
Model wrapper — loads trained Random Forest + scaler from disk,
runs inference, returns per-issue predictions with confidence scores.
"""

import os
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

from app.config import settings
from app.core.feature_extractor import FEATURE_NAMES, features_to_vector

CONFIDENCE_THRESHOLD = 0.40  # Minimum probability to report an issue


@lru_cache(maxsize=1)
def _load_artifacts():
    """Load model artifacts once and cache in memory."""
    artifact_dir = Path(settings.model_dir)
    model = joblib.load(artifact_dir / "model.joblib")
    scaler = joblib.load(artifact_dir / "scaler.joblib")
    label_encoder = joblib.load(artifact_dir / "label_encoder.joblib")
    return model, scaler, label_encoder


def predict(features: dict[str, float]) -> tuple[list[dict], dict]:
    """
    Run the trained classifier on extracted features.

    Returns
    -------
    predictions : list of {issue, confidence, severity}
        Only issues above CONFIDENCE_THRESHOLD are included.
    feature_importance : dict {class_label: {feature: importance}}
    """
    model, scaler, label_encoder = _load_artifacts()

    vec = features_to_vector(features).reshape(1, -1)
    vec_scaled = scaler.transform(vec)

    # Predicted probabilities per class
    proba = model.predict_proba(vec_scaled)[0]
    classes = label_encoder.classes_

    predictions = []
    for cls, conf in zip(classes, proba):
        if cls == "clean":
            continue  # Not an issue
        if conf >= CONFIDENCE_THRESHOLD:
            severity = _confidence_to_severity(conf)
            predictions.append({
                "issue": cls,
                "confidence": round(float(conf), 4),
                "severity": severity,
            })

    # Sort by confidence descending
    predictions.sort(key=lambda x: x["confidence"], reverse=True)

    # Build feature importance dict
    imp = model.feature_importances_
    feature_importance = {
        cls: {feat: round(float(v), 4) for feat, v in zip(FEATURE_NAMES, imp)}
        for cls in classes
    }

    return predictions, feature_importance


def _confidence_to_severity(conf: float) -> str:
    if conf >= 0.75:
        return "severe"
    elif conf >= 0.55:
        return "medium"
    return "mild"


def model_is_ready() -> bool:
    """Check whether model artifacts exist (used by /health endpoint)."""
    artifact_dir = Path(settings.model_dir)
    return all(
        (artifact_dir / f).exists()
        for f in ["model.joblib", "scaler.joblib", "label_encoder.joblib"]
    )
