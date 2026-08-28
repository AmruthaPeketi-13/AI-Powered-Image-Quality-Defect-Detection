"""
Model Training Script
======================
Reads labels.csv, extracts CV features from all images,
trains a RandomForestClassifier, and saves artifacts to ml/artifacts/.

Usage:
  cd backend
  python ml/train.py
"""

import csv
import sys
from pathlib import Path

import joblib
import numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Add backend to path so app modules resolve
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.core.feature_extractor import extract_features, FEATURE_NAMES

LABELS_CSV = Path("data/labels.csv")
ARTIFACT_DIR = Path("ml/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42


def load_dataset():
    """Load labels CSV and extract features from each image."""
    X, y = [], []
    failed = 0

    with open(LABELS_CSV, newline="") as f:
        rows = list(csv.DictReader(f))

    print(f"Loading features from {len(rows)} images...")
    for i, row in enumerate(rows):
        try:
            img = Image.open(row["filename"]).convert("RGB")
            feats = extract_features(img)
            X.append([feats[k] for k in FEATURE_NAMES])
            y.append(row["defect_type"])
        except Exception as e:
            failed += 1
        if (i + 1) % 200 == 0:
            print(f"  Processed {i + 1}/{len(rows)} ({failed} failed)")

    print(f"Dataset: {len(X)} samples, {failed} failed to load.")
    return np.array(X, dtype=np.float32), np.array(y)


def train():
    X, y = load_dataset()

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    print(f"Classes: {list(le.classes_)}")

    # Train/test split — stratified to preserve class balance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=RANDOM_SEED, stratify=y_enc
    )

    # Scale features
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # Train RandomForest
    print("Training RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=20,
        min_samples_split=4,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    model.fit(X_train_s, y_train)

    # Quick accuracy on test set
    acc = model.score(X_test_s, y_test)
    print(f"Test accuracy: {acc:.4f}")

    # Save artifacts
    joblib.dump(model, ARTIFACT_DIR / "model.joblib")
    joblib.dump(scaler, ARTIFACT_DIR / "scaler.joblib")
    joblib.dump(le, ARTIFACT_DIR / "label_encoder.joblib")

    # Save test split for evaluation script
    np.save(ARTIFACT_DIR / "X_test.npy", X_test_s)
    np.save(ARTIFACT_DIR / "y_test.npy", y_test)

    print(f"Artifacts saved to {ARTIFACT_DIR}/")
    return model, scaler, le, X_test_s, y_test


if __name__ == "__main__":
    train()
