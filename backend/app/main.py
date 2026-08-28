"""FastAPI application factory."""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.db.database import init_db

# Ensure data directory exists when running locally
Path("data").mkdir(exist_ok=True)

app = FastAPI(
    title="AI-Powered Image Quality & Defect Detector",
    description=(
        "Evaluates image quality using computer vision features and a trained "
        "Random Forest classifier. Detects blur, noise, exposure issues, and corruption."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serve uploaded images as static files → /uploads/{result_id}.jpg
from fastapi.staticfiles import StaticFiles
import os
os.makedirs("data/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")


@app.on_event("startup")
def startup():
    init_db()
