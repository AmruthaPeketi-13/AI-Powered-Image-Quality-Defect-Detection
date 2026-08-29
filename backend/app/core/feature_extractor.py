"""
CV Feature Extractor — computes 15 image-quality features.

Feature → Defect mapping:
  laplacian_variance   → BLUR
  mean_brightness      → UNDER/OVER-EXPOSURE
  brightness_std       → EXPOSURE CONFIDENCE
  noise_estimate       → NOISE (high-freq energy residual)
  contrast_rms         → CORRUPTION / FLAT
  edge_density         → SHARPNESS SUPPORT (Canny)
  saturation_mean      → COLOR DEFECTS (mean HSV-S)
  histogram_entropy    → CORRUPTION (Shannon entropy)
  gradient_mean        → SHARPNESS (mean Sobel gradient)
  fft_high_freq_ratio  → BLUR / NOISE (FFT energy in high freqs)
  patch_variance_mean  → TEXTURE / CORRUPTION (local patch variance)
  hue_std              → VISUAL DEFECTS (hue shift changes std)
  saturation_std       → VISUAL DEFECTS (desaturation changes spread)
  dark_pixel_ratio     → UNDEREXPOSURE (fraction of very dark pixels)
  bright_pixel_ratio   → OVEREXPOSURE (fraction of very bright pixels)
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
    Extract 11 CV features from a PIL image.
    Returns a dict of {feature_name: float}.
    """
    bgr = _to_bgr(pil_image)
    gray_u8 = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)   # uint8
    gray = gray_u8.astype(np.float32)                  # float32 for stats

    # 1. Laplacian variance — sharpness / blur detection
    lap = cv2.Laplacian(gray_u8, cv2.CV_64F)           # uint8 → CV_64F is supported
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

    # 9. Gradient magnitude mean (Sobel) — fine-grained sharpness
    sobelx = cv2.Sobel(gray_u8, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray_u8, cv2.CV_64F, 0, 1, ksize=3)
    gradient_mean = float(np.sqrt(sobelx ** 2 + sobely ** 2).mean())

    # 10. FFT high-frequency energy ratio — blur kills this, noise raises it
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude = np.abs(fshift)
    h, w = gray.shape
    cy, cx = h // 2, w // 2
    radius = min(h, w) // 6   # low-freq centre radius
    Y, X = np.ogrid[:h, :w]
    low_mask = (Y - cy) ** 2 + (X - cx) ** 2 <= radius ** 2
    total_energy = magnitude.sum() + 1e-10
    fft_high_freq_ratio = float(1.0 - magnitude[low_mask].sum() / total_energy)

    # 11. Mean local patch variance — texture richness / corruption detection
    patch_size = 16
    variances = []
    for r in range(0, h - patch_size, patch_size):
        for c in range(0, w - patch_size, patch_size):
            variances.append(float(gray[r:r + patch_size, c:c + patch_size].var()))
    patch_variance_mean = float(np.mean(variances)) if variances else 0.0

    # 12. Hue std — visual defect shifts hue; clean images have coherent hue
    hue_std = float(hsv[:, :, 0].astype(np.float32).std())

    # 13. Saturation std — desaturation / colour shifts change spread
    saturation_std = float(hsv[:, :, 1].astype(np.float32).std())

    # 14 & 15. Pixel ratio extremes — direct exposure indicators
    total_pixels = gray.size
    dark_pixel_ratio   = float((gray < 30).sum()  / total_pixels)   # underexposure
    bright_pixel_ratio = float((gray > 225).sum() / total_pixels)   # overexposure

    return {
        "laplacian_variance":  laplacian_variance,
        "mean_brightness":     mean_brightness,
        "brightness_std":      brightness_std,
        "noise_estimate":      noise_estimate,
        "contrast_rms":        contrast_rms,
        "edge_density":        edge_density,
        "saturation_mean":     saturation_mean,
        "histogram_entropy":   histogram_entropy,
        "gradient_mean":       gradient_mean,
        "fft_high_freq_ratio": fft_high_freq_ratio,
        "patch_variance_mean": patch_variance_mean,
        "hue_std":             hue_std,
        "saturation_std":      saturation_std,
        "dark_pixel_ratio":    dark_pixel_ratio,
        "bright_pixel_ratio":  bright_pixel_ratio,
    }


# Stable ordered list used everywhere
FEATURE_NAMES = [
    "laplacian_variance", "mean_brightness", "brightness_std",
    "noise_estimate", "contrast_rms", "edge_density",
    "saturation_mean", "histogram_entropy",
    "gradient_mean", "fft_high_freq_ratio", "patch_variance_mean",
    "hue_std", "saturation_std", "dark_pixel_ratio", "bright_pixel_ratio",
]


def features_to_vector(features: dict[str, float]) -> np.ndarray:
    """Convert feature dict → ordered numpy array for model input."""
    return np.array([features[k] for k in FEATURE_NAMES], dtype=np.float32)
