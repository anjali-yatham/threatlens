import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function SignupPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
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
              <input
                type="password"
                className="cyber-input"
                placeholder="Create a password"
                value={password}
                onChange={e => setPassword(e.target.value)}
              />
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
          </div>
        </div>
      </div>
    </>
  )
}