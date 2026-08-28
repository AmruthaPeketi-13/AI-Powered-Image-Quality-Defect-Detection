"""
Synthetic Dataset Generator
============================
Downloads ~200 clean images from Unsplash Source (free, no API key needed),
then applies 6 programmatic degradations at 3 severity levels each to create
a labeled training dataset.

Output:
  data/clean/        — original images
  data/synthetic/    — degraded copies
  data/labels.csv    — filename, defect_type, severity, label (int)

Usage:
  cd backend
  python ml/generate_dataset.py
"""

import csv
import hashlib
import os
import random
import sys
import time
import urllib.request
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

# ── Config ───────────────────────────────────────────────────────────────────
CLEAN_DIR = Path("data/clean")
SYNTH_DIR = Path("data/synthetic")
LABELS_CSV = Path("data/labels.csv")
N_CLEAN_IMAGES = 80       # Download target (some may fail → ok)
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ── Image sources (Unsplash — royalty-free) ───────────────────────────────────
UNSPLASH_TOPICS = [
    "nature", "architecture", "people", "food", "travel",
    "technology", "animals", "city", "landscape", "abstract",
]

PIXABAY_URLS = [
    f"https://picsum.photos/seed/{i}/640/480" for i in range(1, N_CLEAN_IMAGES + 1)
]  # Lorem Picsum — no API key, deterministic seeds


# ── Degradation functions ─────────────────────────────────────────────────────

def apply_blur(img: np.ndarray, level: int) -> np.ndarray:
    """Gaussian blur — simulates camera motion/focus blur."""
    ksize = [9, 19, 31][level]
    return cv2.GaussianBlur(img, (ksize, ksize), 0)


def apply_underexposure(img: np.ndarray, level: int) -> np.ndarray:
    """Gamma darkening — simulates low-light / underexposed photos."""
    gamma = [1.8, 2.8, 4.0][level]
    lut = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(img, lut)


def apply_overexposure(img: np.ndarray, level: int) -> np.ndarray:
    """Gamma brightening — simulates overexposed / blown-out photos."""
    gamma = [0.6, 0.35, 0.2][level]
    lut = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(img, lut)


def apply_noise(img: np.ndarray, level: int) -> np.ndarray:
    """Gaussian noise — simulates sensor noise."""
    sigma = [15, 35, 60][level]
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    noisy = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return noisy


def apply_corruption(img: np.ndarray, level: int) -> np.ndarray:
    """Random block corruption — simulates data loss / transmission errors."""
    out = img.copy()
    n_blocks = [3, 8, 15][level]
    h, w = img.shape[:2]
    block_size = max(20, min(h, w) // 8)
    for _ in range(n_blocks):
        r = random.randint(0, h - block_size)
        c = random.randint(0, w - block_size)
        # Randomly zero out or scramble the block
        if random.random() > 0.5:
            out[r:r + block_size, c:c + block_size] = 0
        else:
            out[r:r + block_size, c:c + block_size] = np.random.randint(
                0, 256, (block_size, block_size, 3), dtype=np.uint8
            )
    return out


def apply_visual_defect(img: np.ndarray, level: int) -> np.ndarray:
    """Colour channel shift + saturation reduction — simulates sensor defects."""
    shift = [20, 50, 90][level]
    out = img.astype(np.int32)
    out[:, :, 0] = np.clip(out[:, :, 0] + shift, 0, 255)   # R channel boost
    out[:, :, 2] = np.clip(out[:, :, 2] - shift, 0, 255)   # B channel reduction
    out = out.astype(np.uint8)
    # Reduce saturation
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] *= [0.6, 0.3, 0.05][level]
    hsv = np.clip(hsv, 0, 255).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


DEGRADATIONS = {
    "blur":          apply_blur,
    "underexposure": apply_underexposure,
    "overexposure":  apply_overexposure,
    "noise":         apply_noise,
    "corruption":    apply_corruption,
    "visual_defect": apply_visual_defect,
}

SEVERITY_NAMES = ["mild", "medium", "severe"]

# ── Download helper ───────────────────────────────────────────────────────────

def download_images():
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    for i, url in enumerate(PIXABAY_URLS):
        dest = CLEAN_DIR / f"clean_{i:04d}.jpg"
        if dest.exists():
            downloaded += 1
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
            with open(dest, "wb") as f:
                f.write(data)
            downloaded += 1
            if downloaded % 10 == 0:
                print(f"  Downloaded {downloaded}/{N_CLEAN_IMAGES}")
            time.sleep(0.1)
        except Exception as e:
            print(f"  Skip {url}: {e}")
    print(f"Clean images available: {downloaded}")
    return list(CLEAN_DIR.glob("*.jpg"))


# ── Main ──────────────────────────────────────────────────────────────────────

def generate():
    SYNTH_DIR.mkdir(parents=True, exist_ok=True)
    print("Downloading clean images...")
    clean_files = download_images()

    rows = []

    # Write clean samples (label = "clean", severity = "none")
    for path in clean_files:
        rows.append({
            "filename": str(path),
            "defect_type": "clean",
            "severity": "none",
        })

    print(f"Generating synthetic degradations from {len(clean_files)} images...")
    total = len(clean_files) * len(DEGRADATIONS) * 3
    done = 0

    for img_path in clean_files:
        try:
            bgr = cv2.imread(str(img_path))
            if bgr is None:
                continue
            bgr = cv2.resize(bgr, (320, 240))  # Normalise size for speed
        except Exception:
            continue

        stem = img_path.stem
        for defect_name, fn in DEGRADATIONS.items():
            for level, sev_name in enumerate(SEVERITY_NAMES):
                out_name = f"{stem}_{defect_name}_{sev_name}.jpg"
                out_path = SYNTH_DIR / out_name
                if not out_path.exists():
                    degraded = fn(bgr.copy(), level)
                    cv2.imwrite(str(out_path), degraded, [cv2.IMWRITE_JPEG_QUALITY, 92])
                rows.append({
                    "filename": str(out_path),
                    "defect_type": defect_name,
                    "severity": sev_name,
                })
                done += 1
                if done % 100 == 0:
                    print(f"  {done}/{total} synthetic images generated")

    # Write labels CSV
    with open(LABELS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "defect_type", "severity"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone! {len(rows)} total samples written to {LABELS_CSV}")


if __name__ == "__main__":
    generate()
