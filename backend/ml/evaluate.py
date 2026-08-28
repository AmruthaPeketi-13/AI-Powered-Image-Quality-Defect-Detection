"""
Model Evaluation Script
========================
Loads saved artifacts + test split and generates:
  - Classification report (precision, recall, F1 per class)
  - Confusion matrix heatmap (PNG)
  - ROC-AUC curves (one-vs-rest, PNG)
  - Feature importance bar chart (PNG)

Usage:
  cd backend
  python ml/evaluate.py
"""

import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.preprocessing import label_binarize

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.core.feature_extractor import FEATURE_NAMES

ARTIFACT_DIR = Path("ml/artifacts")
PLOT_DIR = ARTIFACT_DIR / "eval_plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)


def load():
    model = joblib.load(ARTIFACT_DIR / "model.joblib")
    le = joblib.load(ARTIFACT_DIR / "label_encoder.joblib")
    X_test = np.load(ARTIFACT_DIR / "X_test.npy")
    y_test = np.load(ARTIFACT_DIR / "y_test.npy")
    return model, le, X_test, y_test


def plot_confusion_matrix(model, le, X_test, y_test):
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=le.classes_, yticklabels=le.classes_, ax=ax
    )
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("True", fontsize=12)
    ax.set_title("Confusion Matrix — Image Quality Classifier", fontsize=14)
    plt.tight_layout()
    path = PLOT_DIR / "confusion_matrix.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")
    return y_pred


def plot_roc_curves(model, le, X_test, y_test):
    n_classes = len(le.classes_)
    y_bin = label_binarize(y_test, classes=list(range(n_classes)))
    y_proba = model.predict_proba(X_test)

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = plt.cm.tab10(np.linspace(0, 1, n_classes))

    aucs = []
    for i, (cls, color) in enumerate(zip(le.classes_, colors)):
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
        auc = roc_auc_score(y_bin[:, i], y_proba[:, i])
        aucs.append(auc)
        ax.plot(fpr, tpr, color=color, lw=2, label=f"{cls} (AUC={auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves — One-vs-Rest per Defect Class")
    ax.legend(loc="lower right")
    plt.tight_layout()
    path = PLOT_DIR / "roc_curves.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")
    print(f"Mean ROC-AUC: {np.mean(aucs):.4f}")


def plot_feature_importance(model, le):
    imp = model.feature_importances_
    indices = np.argsort(imp)[::-1]
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = sns.color_palette("viridis", len(FEATURE_NAMES))
    ax.bar(range(len(FEATURE_NAMES)), imp[indices], color=[colors[i] for i in indices])
    ax.set_xticks(range(len(FEATURE_NAMES)))
    ax.set_xticklabels([FEATURE_NAMES[i] for i in indices], rotation=35, ha="right")
    ax.set_title("Random Forest — Global Feature Importances")
    ax.set_ylabel("Importance")
    plt.tight_layout()
    path = PLOT_DIR / "feature_importance.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def evaluate():
    model, le, X_test, y_test = load()
    y_pred = plot_confusion_matrix(model, le, X_test, y_test)
    plot_roc_curves(model, le, X_test, y_test)
    plot_feature_importance(model, le)

    report = classification_report(y_test, y_pred, target_names=le.classes_)
    print("\n--- Classification Report ---")
    print(report)

    report_path = PLOT_DIR / "classification_report.txt"
    report_path.write_text(report)
    print(f"Saved: {report_path}")


if __name__ == "__main__":
    evaluate()
