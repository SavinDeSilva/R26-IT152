import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { registerSW } from 'virtual:pwa-register'
import App from './App'
import { applyTravelHandoff } from './api/sessionHandoff'
import { T } from './theme'

// Apply Tour Ceylon SOS handoff BEFORE React auth checks (avoids bounce to login)
applyTravelHandoff()

registerSW({ immediate: true })
Object.assign(document.documentElement.style, { margin: '0', minHeight: '100%' })
Object.assign(document.body.style, {
  margin: '0', minHeight: '100%', fontFamily: T.fontBody, color: T.ink, background: T.page, WebkitFontSmoothing: 'antialiased',
})
Object.assign(document.getElementById('root').style, { minHeight: '100%' })

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter><App /></BrowserRouter>
  </React.StrictMode>,
)
