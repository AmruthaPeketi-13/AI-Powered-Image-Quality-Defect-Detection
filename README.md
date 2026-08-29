<div align="center">
  <img src="https://img.shields.io/badge/Status-Completed-success" alt="Status" />
  <img src="https://img.shields.io/badge/Platform-Web-blue" alt="Platform" />
  <img src="https://img.shields.io/badge/Machine%20Learning-OpenCV%20%7C%20Scikit--Learn-orange" alt="ML" />
  <img src="https://img.shields.io/badge/Tech%20Stack-React%20%7C%20FastAPI-blueviolet" alt="Tech Stack" />
  
  <h1>ImageIQ — AI Quality Detector</h1>
  <p>An intelligent, end-to-end full-stack application that analyzes image quality using classical Computer Vision and Machine Learning.</p>
</div>

---

## 🌟 Overview

ImageIQ is a sophisticated tool designed to evaluate the technical quality of uploaded images. By extracting raw computer vision metrics (like Laplacian variance, RMS contrast, and edge density) and feeding them into a trained Random Forest model, ImageIQ provides an instant, explainable quality score alongside a detailed breakdown of detected issues.

### 🔗 Live Demo
- **Frontend (Vercel)**: [https://ai-powered-image-quality-defect-det-gold.vercel.app](https://ai-powered-image-quality-defect-det-gold.vercel.app)
- **Backend API (Render)**: [https://ai-powered-image-quality-defect-detection-8m86.onrender.com](https://ai-powered-image-quality-defect-detection-8m86.onrender.com)

## ✨ Key Features

- **🧠 Machine Learning Core**: Uses a Scikit-Learn Random Forest model trained on OpenCV metrics to classify images into quality buckets.
- **🗺️ Explainable AI (XAI)**: Features an interactive 8x8 Sharpness Heatmap that dynamically maps to your image, visually explaining *where* the image is sharp or blurry.
- **📊 Detailed Feature Breakdown**: View exactly what the AI sees, including brightness, noise estimates, saturation mean, and edge density.
- **📚 Persistent History**: Automatically saves analysis results to a cloud PostgreSQL database (Supabase) so you can safely review past uploads at any time without data loss.
- **🎨 Premium UI/UX**: Built with Vite and React, featuring a clean, responsive, light-mode interface optimized for both desktop and mobile.

---

## 🛠️ Tech Stack

**Frontend:**
- React (Vite)
- React Router (Client-side routing)
- Vanilla CSS (Custom design system)
- Axios

**Backend:**
- Python 3.11
- FastAPI (REST API framework)
- PostgreSQL / Supabase (Database)
- SQLAlchemy (ORM)
- OpenCV / Pillow (Image processing)
- Scikit-Learn (Machine Learning inference)

---

## 🚀 Getting Started

Follow these steps to run the application locally on your machine.

### 1. Start the Backend
Open a terminal and navigate to the `backend` directory:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
python main.py
```
*The backend API will run on `http://localhost:8000`*

### 2. Start the Frontend
Open a new terminal and navigate to the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```
*The React application will run on `http://localhost:5173`*

---

## 📸 Screenshots & Usage

1. **Upload an Image**: Drag and drop or select an image on the Landing Page.
2. **Review the Score**: The AI will generate a score out of 100, assigning a label (e.g., *Acceptable*, *Blurry*, *Noisy*).
3. **Analyze the Heatmap**: View the 8x8 Sharpness grid to understand the spatial distribution of focus in your image.
4. **Browse History**: Click the "History" tab to review previously analyzed images and their specific metrics.

---

<div align="center">
  <p><i>Built for rigorous assessment of image quality metrics.</i></p>
</div>
