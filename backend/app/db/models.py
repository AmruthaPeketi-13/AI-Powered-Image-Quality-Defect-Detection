"""ORM models for persisting analysis results."""
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, String, Text

from app.db.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    quality_score = Column(Float, nullable=False)
    quality_label = Column(String, nullable=False)  # ACCEPTABLE | DEGRADED | DEFECTIVE
    issues_json = Column(Text, nullable=False, default="[]")
    features_json = Column(Text, nullable=False, default="{}")
    feature_importance_json = Column(Text, nullable=False, default="{}")
    heatmap_json = Column(Text, nullable=True)  # Optional 8×8 sharpness grid
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ---------- helpers ----------
    @property
    def issues(self):
        return json.loads(self.issues_json)

    @property
    def features(self):
        return json.loads(self.features_json)

    @property
    def feature_importance(self):
        return json.loads(self.feature_importance_json)
