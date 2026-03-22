import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function SignupPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false) // Added state for toggling password visibility
  const { signup } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!name.trim()) { setError('Please enter your name'); return }
    setLoading(true)
    setError('')
    try {
      await signup(name, email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Signup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="corner corner-tl" />
      <div className="corner corner-tr" />
      <div className="corner corner-bl" />
      <div className="corner corner-br" />
      <div className="scan-line" />

      <div className="form-page">
        <div className="form-container">
          <Link to="/" className="back-btn">← Back</Link>

          <div className="form-brand">
            <span>🛡️</span>
            <span>ThreatLens</span>
          </div>

          <h2 className="form-title">Create Account</h2>
          <p className="form-sub">Start protecting yourself today — it&apos;s free</p>

          <div className="glass-card form-card">
            <div className="field-group">
              <label>Full Name</label>
              <input
                type="text"
                className="cyber-input"
                placeholder="Your Name"
                value={name}
                onChange={e => setName(e.target.value)}
              />
            </div>

            <div className="field-group">
              <label>Email</label>
              <input
                type="email"
                className="cyber-input"
                placeholder="your@email.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
              />
            </div>

            <div className="field-group">
              <label>Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="cyber-input"
                  placeholder="Create a password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  style={{ paddingRight: '48px' }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '14px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: 'rgba(224,230,240,0.5)',
                    fontSize: '1.1rem',
                    padding: '0',
                    lineHeight: '1'
                  }}
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            {error && <div className="err-msg">{error}</div>}

            <button
              className="glow-btn full"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </button>

            <p className="switch-link">
              Already have an account? <Link to="/login">Sign In</Link>
            </p>

            <div style={{
              display: 'flex', alignItems: 'center', gap: '12px', margin: '8px 0'
            }}>
              <div style={{ flex: 1, height: '1px', background: 'rgba(0,212,255,0.15)' }} />
              <span style={{ color: 'rgba(224,230,240,0.4)', fontSize: '0.85rem' }}>or continue with</span>
              <div style={{ flex: 1, height: '1px', background: 'rgba(0,212,255,0.15)' }} />
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button type="button" style={{
                flex: 1, padding: '12px', borderRadius: '12px',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(0,212,255,0.2)',
                color: '#e0e6f0', cursor: 'pointer',
                display: 'flex', alignItems: 'center',
                justifyContent: 'center', gap: '8px',
                fontSize: '0.9rem', fontFamily: 'Rajdhani,sans-serif',
                fontWeight: '600', transition: 'all 0.3s'
              }}
              onMouseOver={e => { e.currentTarget.style.borderColor = 'rgba(0,212,255,0.5)' }}
              onMouseOut={e => { e.currentTarget.style.borderColor = 'rgba(0,212,255,0.2)' }}
              onClick={() => alert('Google sign-in coming soon!')}
              >
                <svg width="18" height="18" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                Google
              </button>

              <button type="button" style={{
                flex: 1, padding: '12px', borderRadius: '12px',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(0,212,255,0.2)',
                color: '#e0e6f0', cursor: 'pointer',
                display: 'flex', alignItems: 'center',
                justifyContent: 'center', gap: '8px',
                fontSize: '0.9rem', fontFamily: 'Rajdhani,sans-serif',
                fontWeight: '600', transition: 'all 0.3s'
              }}
              onMouseOver={e => { e.currentTarget.style.borderColor = 'rgba(0,212,255,0.5)' }}
              onMouseOut={e => { e.currentTarget.style.borderColor = 'rgba(0,212,255,0.2)' }}
              onClick={() => alert('Apple sign-in coming soon!')}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
                </svg>
                Apple
              </button>

              <button type="button" style={{
                flex: 1, padding: '12px', borderRadius: '12px',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(0,212,255,0.2)',
                color: '#e0e6f0', cursor: 'pointer',
                display: 'flex', alignItems: 'center',
                justifyContent: 'center', gap: '8px',
                fontSize: '0.9rem', fontFamily: 'Rajdhani,sans-serif',
                fontWeight: '600', transition: 'all 0.3s'
              }}
              onMouseOver={e => { e.currentTarget.style.borderColor = 'rgba(0,212,255,0.5)' }}
              onMouseOut={e => { e.currentTarget.style.borderColor = 'rgba(0,212,255,0.2)' }}
              onClick={() => alert('Email sign-in coming soon!')}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
                Email
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}