import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import AnalyzePage from './pages/AnalyzePage'
import HistoryPage from './pages/HistoryPage'
import ResultDetailPage from './pages/ResultDetailPage'

export default function App() {
  const location = useLocation();
  const isLanding = location.pathname === '/';

  return (
    <div className={`app-shell ${isLanding ? 'is-landing' : ''}`}>
      <nav className={`navbar ${isLanding ? 'navbar-landing' : ''}`}>
        <NavLink to="/" className="navbar-brand">
          IMAGE<span>IQ</span>
        </NavLink>
        <div className="navbar-links">
          <NavLink to="/" className={({isActive}) => `nav-link ${isActive && isLanding ? 'active' : ''}`} end>Home</NavLink>
          <NavLink to="/analyze" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>Analyze</NavLink>
          <NavLink to="/history" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>History</NavLink>
        </div>
      </nav>
      <Routes>
        <Route path="/"              element={<LandingPage />} />
        <Route path="/analyze"       element={<div className="page"><AnalyzePage /></div>} />
        <Route path="/history"       element={<div className="page"><HistoryPage /></div>} />
        <Route path="/results/:id"   element={<div className="page"><ResultDetailPage /></div>} />
      </Routes>
    </div>
  )
}
