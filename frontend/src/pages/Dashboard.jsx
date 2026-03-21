import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [activeTab, setActiveTab] = useState('url')
  const [urlInput, setUrlInput] = useState('')
  const [emailInput, setEmailInput] = useState('')
  const [scamInput, setScamInput] = useState('')
  const [jobInput, setJobInput] = useState('')
  const [result, setResult] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)

  useEffect(() => {
    const particles = []
    for (let i = 0; i < 40; i++) {
      const p = document.createElement('div')
      p.className = 'particle'
      const size = Math.random() * 3 + 1
      const color = Math.random() > 0.5 ? '#00d4ff' : '#7b2fff'
      p.style.cssText = `left:${Math.random()*100}%;width:${size}px;height:${size}px;background:${color};box-shadow:0 0 ${size*2}px ${color};animation-duration:${Math.random()*14+8}s;animation-delay:-${Math.random()*14}s;`
      document.body.appendChild(p)
      particles.push(p)
    }
    return () => particles.forEach(p => p.remove())
  }, [])

  const analyzeContent = async (type) => {
    const inputs = { url: urlInput, email: emailInput, scam: scamInput, job: jobInput }
    const endpoints = {
      url: 'http://localhost:5000/api/predict-url',
      email: 'http://localhost:5000/api/predict-email',
      scam: 'http://localhost:5000/api/predict-scam',
      job: 'http://localhost:5000/api/predict-job'
    }
    const value = inputs[type]
    if (!value.trim()) return
    setAnalyzing(true)
    setResult(null)
    try {
      const token = localStorage.getItem('token')
      const body = type === 'url' ? { url: value } : { text: value }
      const res = await axios.post(endpoints[type], body, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setResult(res.data)
    } catch {
      setResult({ result: 'Error', confidence: 0 })
    } finally {
      setAnalyzing(false)
    }
  }

  const isThreat = result && ['Phishing', 'Spam/Phishing', 'Fake'].includes(result.result)

  return (
    <>
      <div className="corner corner-tl" />
      <div className="corner corner-tr" />
      <div className="corner corner-bl" />
      <div className="corner corner-br" />
      <div className="scan-line" />

      {/* NAVBAR */}
      <nav className="navbar">
        <div className="nav-logo">🛡️ <span>ThreatLens</span></div>
        <div className="nav-links">
          <a href="#how-it-works">How It Works</a>
          <a href="#detection">Detection</a>
          <a href="#features">Features</a>
        </div>
        <div className="nav-right">
          <span className="nav-user">👤 Welcome, {user?.name}</span>
          <button className="logout-btn" onClick={logout}>⬅ Logout</button>
        </div>
      </nav>

      {/* HERO */}
      <section className="hero">
        <div className="hero-inner">
          <div className="hero-left">
            <div className="badge-pill">
              <span className="pulse-dot" />
              AI-Powered Security
            </div>
            <h1 className="hero-h1">
              <span className="grad-text">Detect Phishing</span><br />
              <span style={{ color: '#fff' }}>Websites Instantly</span><br />
              <span className="grad-text2">with AI</span>
            </h1>
            <p className="hero-desc">
              Our advanced machine learning system analyzes URLs, emails, messages
              and job postings in real-time, detecting threats before they can harm you.
            </p>
            <div className="hero-pills">
              <div className="stat-pill">✅ 10M+ URLs Scanned</div>
              <div className="stat-pill">🛡️ 99.7% Accuracy</div>
              <div className="stat-pill">⚡ Real-time Analysis</div>
            </div>
            <button
              className="glow-btn large"
              onClick={() => document.getElementById('detection').scrollIntoView({ behavior: 'smooth' })}
            >
              🔍 Start Scanning
            </button>
          </div>

          <div className="hero-right">
            <div className="shield-wrap">
              <div className="shield-glow" />
              <div className="shield-anim">
                <svg viewBox="0 0 200 220" style={{ width: '100%', height: '100%', filter: 'drop-shadow(0 0 20px rgba(0,212,255,0.4))' }}>
                  <defs>
                    <linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style={{ stopColor: '#00d4ff' }} />
                      <stop offset="50%" style={{ stopColor: '#7b68ee' }} />
                      <stop offset="100%" style={{ stopColor: '#00d4ff' }} />
                    </linearGradient>
                    <filter id="gf">
                      <feGaussianBlur stdDeviation="4" result="b" />
                      <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
                    </filter>
                  </defs>
                  <path d="M100 10 L180 50 L180 120 C180 170 140 200 100 210 C60 200 20 170 20 120 L20 50 Z"
                    fill="rgba(13,21,37,0.9)" stroke="url(#sg)" strokeWidth="3" filter="url(#gf)" />
                  <path d="M100 30 L160 60 L160 115 C160 155 130 180 100 190 C70 180 40 155 40 115 L40 60 Z"
                    fill="none" stroke="rgba(0,212,255,0.25)" strokeWidth="1" />
                  <g transform="translate(70,70)">
                    <rect x="10" y="35" width="40" height="35" rx="5" fill="none" stroke="#00d4ff" strokeWidth="2.5" />
                    <path d="M20 35 L20 25 C20 15 30 5 40 5 C50 5 60 15 60 25 L60 35"
                      transform="translate(-10,0)" fill="none" stroke="#00d4ff" strokeWidth="2.5" strokeLinecap="round" />
                    <circle cx="30" cy="52" r="4" fill="#00d4ff" />
                    <line x1="30" y1="56" x2="30" y2="62" stroke="#00d4ff" strokeWidth="2.5" />
                  </g>
                  <line x1="40" y1="80" x2="60" y2="80" stroke="#00d4ff" strokeWidth="1" opacity="0.5">
                    <animate attributeName="opacity" values="0.2;1;0.2" dur="2s" repeatCount="indefinite" />
                  </line>
                  <line x1="140" y1="80" x2="160" y2="80" stroke="#00d4ff" strokeWidth="1" opacity="0.5">
                    <animate attributeName="opacity" values="0.2;1;0.2" dur="2s" repeatCount="indefinite" begin="0.7s" />
                  </line>
                </svg>
              </div>
              <div className="node" style={{ top: '10%', left: '-5%' }} />
              <div className="node" style={{ top: '30%', right: '-10%' }} />
              <div className="node" style={{ bottom: '25%', left: '-10%' }} />
              <div className="node" style={{ bottom: '10%', right: '-5%' }} />
            </div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="section" id="how-it-works">
        <div className="sec-head">
          <span className="sec-label">Process</span>
          <h2>How It Works</h2>
          <p>Three simple steps to protect yourself from cyber threats using advanced AI.</p>
        </div>
        <div className="grid-3">
          <div className="glass-card step-card">
            <span className="step-num" style={{ color: 'rgba(0,212,255,0.1)' }}>01</span>
            <span className="card-icon-lg">🔗</span>
            <h3>Enter Content</h3>
            <p>Paste any suspicious URL, email, message or job posting into our secure scanner.</p>
            <div className="card-tag cyan"><span className="dot-sm cyan" />Instant validation</div>
          </div>
          <div className="glass-card step-card">
            <span className="step-num" style={{ color: 'rgba(123,104,238,0.1)' }}>02</span>
            <span className="card-icon-lg">🖥️</span>
            <h3>AI Analysis</h3>
            <p>Our ML models analyze 50+ features including patterns, keywords and domain info.</p>
            <div className="card-tag purple"><span className="dot-sm purple" />Deep learning models</div>
          </div>
          <div className="glass-card step-card">
            <span className="step-num" style={{ color: 'rgba(0,255,136,0.1)' }}>03</span>
            <span className="card-icon-lg">🛡️</span>
            <h3>Risk Detection</h3>
            <p>Get instant results with confidence score and detailed threat analysis.</p>
            <div className="card-tag green"><span className="dot-sm green" />Detailed threat report</div>
          </div>
        </div>
      </section>

      {/* DETECTION */}
      <section className="section" id="detection">
        <div className="sec-head">
          <span className="sec-label">Scanner</span>
          <h2>Detection Dashboard</h2>
          <p>Analyze suspicious content across 4 threat categories using AI-powered detection.</p>
        </div>
        <div className="glass-card detect-box">
          <div className="tabs">
            {['url', 'email', 'scam', 'job'].map(type => (
              <button
                key={type}
                className={`tab ${activeTab === type ? 'active' : ''}`}
                onClick={() => { setActiveTab(type); setResult(null) }}
              >
                {type === 'url' && '🔗 URL Check'}
                {type === 'email' && '📧 Email Check'}
                {type === 'scam' && '⚠️ Scam Message'}
                {type === 'job' && '💼 Job Posting'}
              </button>
            ))}
          </div>

          <div className={`tab-panel ${activeTab === 'url' ? 'active' : ''}`}>
            <p className="input-label">Enter suspicious URL to analyze</p>
            <input type="text" className="cyber-input" value={urlInput}
              onChange={e => setUrlInput(e.target.value)}
              placeholder="https://suspicious-site.com/login" />
            <button className="glow-btn large" style={{ marginTop: '16px' }}
              onClick={() => analyzeContent('url')}>
              🔍 Analyze URL
            </button>
          </div>

          <div className={`tab-panel ${activeTab === 'email' ? 'active' : ''}`}>
            <p className="input-label">Paste suspicious email content below</p>
            <textarea className="cyber-textarea" value={emailInput}
              onChange={e => setEmailInput(e.target.value)}
              placeholder="Paste the suspicious email content here..." />
            <button className="glow-btn large" style={{ marginTop: '16px' }}
              onClick={() => analyzeContent('email')}>
              🔍 Analyze Email
            </button>
          </div>

          <div className={`tab-panel ${activeTab === 'scam' ? 'active' : ''}`}>
            <p className="input-label">Paste suspicious message below</p>
            <textarea className="cyber-textarea" value={scamInput}
              onChange={e => setScamInput(e.target.value)}
              placeholder="Paste the suspicious message here..." />
            <button className="glow-btn large" style={{ marginTop: '16px' }}
              onClick={() => analyzeContent('scam')}>
              🔍 Analyze Message
            </button>
          </div>

          <div className={`tab-panel ${activeTab === 'job' ? 'active' : ''}`}>
            <p className="input-label">Paste job posting description below</p>
            <textarea className="cyber-textarea" value={jobInput}
              onChange={e => setJobInput(e.target.value)}
              placeholder="Paste the job posting description here..." />
            <button className="glow-btn large" style={{ marginTop: '16px' }}
              onClick={() => analyzeContent('job')}>
              🔍 Analyze Job Post
            </button>
          </div>

          {(analyzing || result) && (
            <div className="result-box">
              {analyzing && (
                <div className="res-loading">
                  <div className="spinner" />
                  <span>Analyzing with AI...</span>
                </div>
              )}
              {result && !analyzing && (
                isThreat ? (
                  <div className="res-threat">
                    <div className="res-icon">⚠️</div>
                    <div className="res-title threat">THREAT DETECTED</div>
                    <div className="res-type threat">{result.result}</div>
                    <div className="res-conf">Confidence: {result.confidence}%</div>
                  </div>
                ) : (
                  <div className="res-safe">
                    <div className="res-icon">✅</div>
                    <div className="res-title safe">SAFE</div>
                    <div className="res-type safe">{result.result}</div>
                    <div className="res-conf">Confidence: {result.confidence}%</div>
                  </div>
                )
              )}
            </div>
          )}
        </div>
      </section>

      {/* FEATURES */}
      <section className="section" id="features">
        <div className="sec-head">
          <span className="sec-label">Capabilities</span>
          <h2>Advanced Features</h2>
          <p>Powered by cutting-edge machine learning and comprehensive threat intelligence.</p>
        </div>
        <div className="grid-4">
          <div className="glass-card feat-card">
            <span className="feat-icon">🖥️</span>
            <h3>AI-Powered Detection</h3>
            <p>Deep learning models trained on millions of phishing samples.</p>
          </div>
          <div className="glass-card feat-card">
            <span className="feat-icon">⚡</span>
            <h3>Real-time Analysis</h3>
            <p>Instant scanning with results in under 2 seconds.</p>
          </div>
          <div className="glass-card feat-card">
            <span className="feat-icon">📊</span>
            <h3>Multi-Threat Detection</h3>
            <p>Detects URL, email, SMS and job posting scams.</p>
          </div>
          <div className="glass-card feat-card">
            <span className="feat-icon">📋</span>
            <h3>Explainable Results</h3>
            <p>Clear confidence scores and threat explanations.</p>
          </div>
        </div>
        <div className="glass-card stats-row">
          <div className="stat-item">
            <div className="stat-num grad-text">99.7%</div>
            <div className="stat-lbl">Detection Accuracy</div>
          </div>
          <div className="stat-item">
            <div className="stat-num" style={{ background: 'linear-gradient(135deg,#9b5de5,#c77dff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>1.2s</div>
            <div className="stat-lbl">Avg. Scan Time</div>
          </div>
          <div className="stat-item">
            <div className="stat-num" style={{ background: 'linear-gradient(135deg,#00ff88,#00cc6a)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>10M+</div>
            <div className="stat-lbl">URLs Analyzed</div>
          </div>
          <div className="stat-item">
            <div className="stat-num" style={{ background: 'linear-gradient(135deg,#ffaa00,#ff8800)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>500K+</div>
            <div className="stat-lbl">Threats Blocked</div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <div className="foot-brand">🛡️ <span>ThreatLens</span></div>
        <div className="foot-links">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">Contact</a>
        </div>
        <div className="foot-copy">© 2025 ThreatLens. All rights reserved.</div>
      </footer>
    </>
  )
}