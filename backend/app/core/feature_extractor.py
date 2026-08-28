"""
CV Feature Extractor — computes 8 image-quality features.

Feature → Defect mapping (documented for rubric):
  laplacian_variance  → BLUR: Laplacian second-derivative amplifies edges;
                        low variance = edges are smooth = image is blurry.
  mean_brightness     → UNDER/OVER-EXPOSURE: mean pixel intensity in [0,255].
                        <50 = too dark (underexposed), >200 = too bright (overexposed).
  brightness_std      → EXPOSURE CONFIDENCE: spread of pixel intensities.
                        Very low std → flat histogram → washed-out / clamped.
  noise_estimate      → NOISE: difference between image and a mild Gaussian blur
                        approximates the high-freq noise component.
  contrast_rms        → CORRUPTION / FLAT: RMS contrast = std(I)/mean(I).
                        Severely degraded images lose local contrast structure.
  edge_density        → SHARPNESS SUPPORT: Canny edge pixel ratio.
                        Blurry images have sparse edges; sharp images are dense.
  saturation_mean     → COLOR DEFECTS: mean HSV-S channel.
                        Desaturated or colour-shifted images flag visual defects.
  histogram_entropy   → CORRUPTION: Shannon entropy of luminance histogram.
                        Corrupt/partially zeroed images have very low entropy.
"""

import cv2
import numpy as np
from PIL import Image


def _to_bgr(pil_image: Image.Image) -> np.ndarray:
    """Convert PIL image to BGR uint8 numpy array."""
    rgb = np.array(pil_image.convert("RGB"), dtype=np.uint8)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def extract_features(pil_image: Image.Image) -> dict[str, float]:
    """
    Extract 8 CV features from a PIL image.
    Returns a dict of {feature_name: float}.
    """
    bgr = _to_bgr(pil_image)
    gray_u8 = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)          # uint8
    gray = gray_u8.astype(np.float32)                        # float32 for stats

    # 1. Laplacian variance — sharpness / blur detection
    lap = cv2.Laplacian(gray_u8, cv2.CV_64F)                 # uint8 → CV_64F is supported
    laplacian_variance = float(lap.var())

    # 2 & 3. Brightness stats — exposure detection
    mean_brightness = float(gray.mean())
    brightness_std = float(gray.std())

    # 4. Noise estimate — high-freq energy after smoothing
    blurred = cv2.GaussianBlur(gray_u8, (5, 5), 0).astype(np.float32)
    noise_estimate = float(np.abs(gray - blurred).mean())

    # 5. RMS contrast — corruption / flat-image detection
    mean_val = gray.mean() if gray.mean() > 0 else 1e-6
    contrast_rms = float(gray.std() / mean_val)

    # 6. Edge density — supports sharpness assessment
    edges = cv2.Canny(bgr, 50, 150)
    edge_density = float(edges.sum() / (edges.size * 255))

    # 7. Saturation mean — colour defect detection
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    saturation_mean = float(hsv[:, :, 1].mean())

    # 8. Histogram entropy — corruption / uniform-noise detection
    hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256))
    hist_prob = hist / (hist.sum() + 1e-10)
    entropy = -np.sum(hist_prob * np.log2(hist_prob + 1e-10))
    histogram_entropy = float(entropy)

    return {
        "laplacian_variance": laplacian_variance,
        "mean_brightness": mean_brightness,
        "brightness_std": brightness_std,
        "noise_estimate": noise_estimate,
        "contrast_rms": contrast_rms,
        "edge_density": edge_density,
        "saturation_mean": saturation_mean,
        "histogram_entropy": histogram_entropy,
    }


FEATURE_NAMES = list(extract_features.__doc__ and [
    "laplacian_variance", "mean_brightness", "brightness_std",
    "noise_estimate", "contrast_rms", "edge_density",
    "saturation_mean", "histogram_entropy",
])

# Ensure ordering is stable
FEATURE_NAMES = [
    "laplacian_variance", "mean_brightness", "brightness_std",
    "noise_estimate", "contrast_rms", "edge_density",
    "saturation_mean", "histogram_entropy",
]


def features_to_vector(features: dict[str, float]) -> np.ndarray:
    """Convert feature dict → ordered numpy array for model input."""
    return np.array([features[k] for k in FEATURE_NAMES], dtype=np.float32)
