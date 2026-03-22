import { useEffect } from 'react'
import { Link } from 'react-router-dom'

export default function LandingPage() {
  useEffect(() => {
    const particles = []
    for (let i = 0; i < 40; i++) {
      const p = document.createElement('div')
      p.className = 'particle'
      const size = Math.random() * 3 + 1
      const color = Math.random() > 0.5 ? '#00d4ff' : '#7b2fff'
      p.style.position = 'fixed'
      p.style.left = Math.random() * 100 + '%'
      p.style.bottom = '-10px'
      p.style.width = size + 'px'
      p.style.height = size + 'px'
      p.style.background = color
      p.style.borderRadius = '50%'
      p.style.boxShadow = '0 0 ' + (size * 2) + 'px ' + color
      p.style.pointerEvents = 'none'
      p.style.zIndex = '0'
      p.style.animation = 'floatUp ' + (Math.random() * 14 + 8) + 's linear infinite'
      p.style.animationDelay = '-' + (Math.random() * 14) + 's'
      document.body.appendChild(p)
      particles.push(p)
    }
    return () => particles.forEach(p => p.remove())
  }, [])

  return (
    <>
      <div className="corner corner-tl" />
      <div className="corner corner-tr" />
      <div className="corner corner-bl" />
      <div className="corner corner-br" />
      <div className="scan-line" />

      <div className="landing-page">
        <div className="landing-container">

          <div className="badge-pill">
            <span className="pulse-dot" />
            Next-Gen Security
          </div>

          <div className="brand-wrap">
            <span className="brand-icon">🛡️</span>
            <h1 className="brand-title">ThreatLens</h1>
          </div>

          <p className="brand-tagline">Protect Yourself from Cyber Threats</p>
          <p className="brand-sub">Advanced AI-powered threat detection in seconds</p>

          <div className="auth-cards">
            <div className="glass-card auth-card">
              <span className="card-icon-emoji">🔒</span>
              <h3>Sign In</h3>
              <p>Access your existing account and start scanning URLs, emails and messages immediately.</p>
              <Link to="/login" className="glow-btn full">Sign In</Link>
            </div>
            <div className="glass-card auth-card">
              <span className="card-icon-emoji">👤</span>
              <h3>Create Account</h3>
              <p>Join thousands of users protecting themselves with ThreatLens AI detection.</p>
              <Link to="/signup" className="glow-btn outline full">Get Started</Link>
            </div>
          </div>

          <div className="glass-card why-card">
            <h4>Why Choose ThreatLens?</h4>
            <div className="why-list">
              <div className="why-item">
                <span style={{fontSize:'1.2rem'}}>✅</span>
                <div>
                  <strong>99.7% Accurate</strong>
                  <span>AI-powered ML detection</span>
                </div>
              </div>
              <div className="why-item">
                <span style={{fontSize:'1.2rem'}}>✅</span>
                <div>
                  <strong>Real-time Results</strong>
                  <span>Scans in under 2 seconds</span>
                </div>
              </div>
              <div className="why-item">
                <span style={{fontSize:'1.2rem'}}>✅</span>
                <div>
                  <strong>4 Detection Types</strong>
                  <span>URL, Email, SMS, Jobs</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </>
  )
}