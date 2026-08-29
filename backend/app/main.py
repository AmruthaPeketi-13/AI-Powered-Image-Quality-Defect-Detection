"""FastAPI application factory."""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.db.database import init_db

# Ensure runtime directories exist
Path("data/uploads").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle handler (replaces deprecated on_event)."""
    init_db()          # Create DB tables on startup
    yield              # App runs here
    # (add shutdown cleanup here if needed)


app = FastAPI(
    title="AI-Powered Image Quality & Defect Detector",
    description=(
        "Evaluates image quality using computer vision features and a trained "
        "Random Forest classifier. Detects blur, noise, exposure issues, and corruption."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serve uploaded thumbnails as static files → GET /uploads/{id}.jpg
app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")
