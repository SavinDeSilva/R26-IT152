import { Navigate, Route, Routes } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import IncidentDetail from './pages/IncidentDetail'
import AmbientBackground from './components/AmbientBackground'
import SiteChrome from '@shared/SiteChrome'
import { T } from './theme'

function RequireAuth({ children }) {
  const token = localStorage.getItem('policeToken')
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <SiteChrome app="police" active="">
    <div style={{ position: 'relative', minHeight: 'calc(100dvh - 12.5rem)', fontFamily: T.fontBody, color: T.ink, background: T.page }}>
      <AmbientBackground variant="light" scan />
      <div style={{ position: 'relative', zIndex: 1 }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<RequireAuth><Dashboard /></RequireAuth>} />
          <Route path="/incidents/:id" element={<RequireAuth><IncidentDetail /></RequireAuth>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
    </SiteChrome>
  )
}
