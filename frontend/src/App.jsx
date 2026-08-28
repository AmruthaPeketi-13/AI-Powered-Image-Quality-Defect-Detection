import { Routes, Route, NavLink } from 'react-router-dom'
import AnalyzePage from './pages/AnalyzePage'
import HistoryPage from './pages/HistoryPage'
import ResultDetailPage from './pages/ResultDetailPage'

export default function App() {
  return (
    <div className="app-shell">
      <nav className="navbar">
        <NavLink to="/" className="navbar-brand">
          🔍 Image<span>IQ</span>
        </NavLink>
        <div className="navbar-links">
          <NavLink to="/"        className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`} end>Analyze</NavLink>
          <NavLink to="/history" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>History</NavLink>
        </div>
      </nav>
      <Routes>
        <Route path="/"              element={<AnalyzePage />} />
        <Route path="/history"       element={<HistoryPage />} />
        <Route path="/results/:id"   element={<ResultDetailPage />} />
      </Routes>
    </div>
  )
}
