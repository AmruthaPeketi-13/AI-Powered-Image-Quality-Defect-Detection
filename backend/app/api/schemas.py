"""Pydantic request / response schemas for the API."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IssueDetail(BaseModel):
    issue: str
    confidence: float
    severity: str   # mild | medium | severe


class AnalysisResponse(BaseModel):
    id: str
    filename: str
    quality_score: float
    quality_label: str  # ACCEPTABLE | DEGRADED | DEFECTIVE
    issues: list[IssueDetail]
    features: dict[str, float]
    feature_importance: dict[str, dict[str, float]]
    heatmap: Optional[list[list[float]]] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisListItem(BaseModel):
    id: str
    filename: str
    quality_score: float
    quality_label: str
    issue_count: int
    thumbnail_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    model_ready: bool
    version: str = "1.0.0"
