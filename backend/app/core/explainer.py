"""
Explainability module.

Provides two forms of explanation:
  1. Feature-level: RF feature importances per issue class (returned in every response).
  2. Spatial heatmap: 8×8 grid of local Laplacian variance — shows WHICH regions
     of the image are blurry/sharp. Frontend overlays this as a colour grid.
"""

import cv2
import numpy as np
from PIL import Image


def compute_sharpness_heatmap(pil_image: Image.Image, grid_size: int = 8) -> list[list[float]]:
    """
    Divide image into a grid_size × grid_size grid.
    Compute Laplacian variance in each cell → normalise to [0, 1].
    Returns a 2D list (rows × cols) of normalised sharpness scores.
    High value = sharp, low value = blurry.
    """
    rgb = np.array(pil_image.convert("RGB"), dtype=np.uint8)
    gray_u8 = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)   # uint8 for Laplacian

    h, w = gray_u8.shape
    cell_h = h // grid_size
    cell_w = w // grid_size

    grid = []
    for r in range(grid_size):
        row = []
        for c in range(grid_size):
            cell = gray_u8[r * cell_h:(r + 1) * cell_h, c * cell_w:(c + 1) * cell_w]
            lap = cv2.Laplacian(cell, cv2.CV_64F)
            row.append(float(lap.var()))
        grid.append(row)

    # Normalise across all cells
    flat = [v for row in grid for v in row]
    max_val = max(flat) if max(flat) > 0 else 1.0
    return [[round(v / max_val, 4) for v in row] for row in grid]


def build_feature_importance(model, label_encoder) -> dict[str, dict[str, float]]:
    """
    Extract per-class feature importances from the trained RandomForest.
    Returns { issue_class: { feature_name: importance } }.
    """
    from app.core.feature_extractor import FEATURE_NAMES

    importances: dict[str, dict[str, float]] = {}
    classes = label_encoder.classes_

    # RandomForest has a single global importance; for per-class detail we
    # use the raw feature_importances_ (same for all classes in a single RF).
    # For multi-class explainability we report global importance per class label.
    global_imp = model.feature_importances_
    for cls in classes:
        importances[cls] = {
            feat: round(float(imp), 4)
            for feat, imp in zip(FEATURE_NAMES, global_imp)
        }
    return importances
