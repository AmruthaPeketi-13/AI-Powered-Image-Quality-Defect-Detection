"""
Quality scorer — combines per-issue predictions into a single quality_score [0,100]
and a quality_label (ACCEPTABLE / DEGRADED / DEFECTIVE).

Scoring formula (fully explainable):
  base_score = 100
  Each detected issue subtracts a penalty proportional to its confidence.
  Penalties are weighted by severity — severe issues (corruption, blur) cost more.

  quality_score = max(0, 100 - Σ(penalty_i × confidence_i))

  Thresholds:
    ≥ 75 → ACCEPTABLE
    45–74 → DEGRADED
    < 45  → DEFECTIVE
"""

ISSUE_PENALTIES = {
    "blur":          30,   # Heavy — directly impacts image usability
    "corruption":    30,   # Heavy — data loss / artefacts
    "underexposure": 20,
    "overexposure":  20,
    "noise":         15,
    "visual_defect": 20,
}

QUALITY_THRESHOLDS = {"ACCEPTABLE": 75, "DEGRADED": 45}


def compute_quality_score(predictions: list[dict]) -> tuple[float, str]:
    """
    Parameters
    ----------
    predictions : list of {"issue": str, "confidence": float, "severity": str}

    Returns
    -------
    quality_score : float in [0, 100]
    quality_label : "ACCEPTABLE" | "DEGRADED" | "DEFECTIVE"
    """
    penalty_total = 0.0
    for pred in predictions:
        issue = pred["issue"]
        confidence = pred["confidence"]
        base_penalty = ISSUE_PENALTIES.get(issue, 15)
        # Scale penalty by confidence (0–1) so uncertain detections cost less
        penalty_total += base_penalty * confidence

    quality_score = round(max(0.0, 100.0 - penalty_total), 1)

    if quality_score >= QUALITY_THRESHOLDS["ACCEPTABLE"]:
        quality_label = "ACCEPTABLE"
    elif quality_score >= QUALITY_THRESHOLDS["DEGRADED"]:
        quality_label = "DEGRADED"
    else:
        quality_label = "DEFECTIVE"

    return quality_score, quality_label
