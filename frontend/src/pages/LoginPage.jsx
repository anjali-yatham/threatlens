import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.')
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

          <h2 className="form-title">Welcome Back</h2>
          <p className="form-sub">Sign in to continue protecting yourself</p>

          <div className="glass-card form-card">
            <div className="field-group">
              <label>Email</label>
              <input
                type="email"
                className="cyber-input"
                placeholder="your@email.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSubmit(e)}
              />
            </div>

            <div className="field-group">
              <label>Password</label>
              <input
                type="password"
                className="cyber-input"
                placeholder="Enter your password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSubmit(e)}
              />
            </div>

            {error && <div className="err-msg">{error}</div>}

            <button
              className="glow-btn full"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>

            <p className="switch-link">
              Don&apos;t have an account? <Link to="/signup">Sign Up</Link>
            </p>
          </div>
        </div>
      </div>
    </>
  )
}