import { Link, useLocation } from 'react-router-dom'
import { History, LogOut, Siren, UserRound } from 'lucide-react'
import { clearTouristSession } from '../api/client'
import { goToTravelLogin } from '../api/sessionHandoff'
import { T } from '../theme'

const tabs = [
  { to: '/', label: 'SOS', icon: Siren },
  { to: '/history', label: 'History', icon: History },
  { to: '/profile', label: 'Profile', icon: UserRound },
]

export default function TouristNav() {
  const location = useLocation()
  const name = localStorage.getItem('touristName') || 'Visitor'

  const logout = () => {
    clearTouristSession()
    goToTravelLogin()
  }

  return (
    <header
      style={{
        background: T.white,
        borderBottom: `1px solid ${T.line}`,
      }}
    >
      <div className="sos-nav-inner">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
          <div style={{ minWidth: 0 }}>
            <p style={{ margin: 0, fontSize: 11, fontWeight: 700, color: T.muted, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
              Case desk
            </p>
            <p style={{ margin: 0, fontSize: 15, fontWeight: 700, color: T.navy, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {name}
            </p>
          </div>
        </div>
        <nav style={{ display: 'flex', gap: 8, alignItems: 'center', flexShrink: 0 }}>
          {tabs.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to
            return (
              <Link
                key={to}
                to={to}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '8px 12px',
                  borderRadius: 8,
                  textDecoration: 'none',
                  fontSize: 13,
                  fontWeight: 700,
                  background: active ? T.navy : T.lineSoft,
                  color: active ? T.white : T.navy,
                }}
              >
                <Icon size={15} strokeWidth={2} />
                {label}
              </Link>
            )
          })}
          <button
            type="button"
            onClick={logout}
            title="Log out"
            style={{
              border: 'none',
              background: T.lineSoft,
              color: T.navy,
              borderRadius: 8,
              height: 36,
              padding: '0 12px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              cursor: 'pointer',
              fontWeight: 700,
              fontSize: 13,
              fontFamily: T.fontBody,
            }}
          >
            <LogOut size={15} strokeWidth={2} />
            Log out
          </button>
        </nav>
      </div>
    </header>
  )
}
