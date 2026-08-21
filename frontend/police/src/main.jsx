import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { T } from './theme'

Object.assign(document.documentElement.style, { minHeight: '100%' })
Object.assign(document.body.style, {
  margin: '0', minHeight: '100%', fontFamily: T.fontBody, color: T.ink, background: T.page, WebkitFontSmoothing: 'antialiased',
})
Object.assign(document.getElementById('root').style, { minHeight: '100%' })

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter><App /></BrowserRouter>
  </React.StrictMode>,
)
