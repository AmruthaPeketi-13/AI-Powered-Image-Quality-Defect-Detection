import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();

  const features = [
    { title: "15 METRICS", desc: "Advanced image quality assessment using Laplacian variance, FFT high-frequency ratio, and HSV shifts." },
    { title: "FAST INFERENCE", desc: "Powered by a highly optimized HistGradientBoosting model, returning inferences in milliseconds." },
    { title: "XAI HEATMAPS", desc: "Explainable AI visualizes exactly where your image suffers from defects or corruption." },
    { title: "HISTORY", desc: "Automatically stores your results with a beautifully rendered dashboard to compare over time." },
  ];

  return (
    <div className="landing-container">
      {/* Background Dots */}
      <div className="dotted-bg left-dots"></div>
      <div className="dotted-bg right-dots"></div>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            DISCOVER TRUE<br/>QUALITY
          </h1>
          <p className="hero-subtitle">
            AI-powered image analysis for blur, noise, and exposure.
          </p>
          <div className="hero-actions">
            <button className="primary-btn" onClick={() => navigate('/analyze')}>TRY IT OUT</button>
          </div>
        </div>
      </section>

      {/* Showcase Section */}
      <section className="showcase-section">
        <div className="showcase-header">
          <h2 className="showcase-title">EXPERIENCE IT ON<br/>OUR WEBSITE</h2>
          <p className="showcase-desc">Upload your images and let our AI engine reveal hidden quality issues, noise, and exposure defects in seconds.</p>
        </div>
        
        <div className="showcase-cards">
          <div className="showcase-card" onClick={() => navigate('/analyze')}>
            <img src="/assets/user_blur.png" alt="Blur Detection" />
            <h3>BLUR</h3>
          </div>
          <div className="showcase-card" onClick={() => navigate('/analyze')}>
            <img src="/assets/user_noise.png" alt="Noise Detection" />
            <h3>NOISE</h3>
          </div>
          <div className="showcase-card" onClick={() => navigate('/analyze')}>
            <img src="/assets/user_exposure.jpg" alt="Exposure Detection" />
            <h3>EXPOSURE</h3>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-list">
          {features.map((feat, idx) => (
            <div key={idx} className={`feature-row ${idx % 2 === 1 ? 'reverse' : ''}`}>
              <h2 className="feature-title">{feat.title}</h2>
              <p className="feature-desc">{feat.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer Section */}
      <section className="footer-section">
        <div className="footer-cta">
          <h1 className="footer-title">START<br/>ANALYZING</h1>
          <button className="primary-btn" onClick={() => navigate('/analyze')}>GET STARTED</button>
        </div>
        
        <footer className="footer-bottom">
          <div className="footer-logo">IMAGE<span>IQ</span></div>
          <div className="footer-socials">
            <a href="https://github.com/amrut/image-quality-detector" className="social-icon">GH</a>
            <a href="#" className="social-icon">IN</a>
            <a href="#" className="social-icon">TW</a>
          </div>
        </footer>
      </section>
    </div>
  );
}
