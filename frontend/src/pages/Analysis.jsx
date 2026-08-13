import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { runAnalysis } from '../services/api'
import { Leaf } from 'lucide-react'

const ANALYSIS_STEPS = [
  { text: 'Validating your soil and farm data...', emoji: '📋' },
  { text: 'Running ML model prediction...', emoji: '🤖' },
  { text: 'Applying ICAR/TNAU agricultural rules...', emoji: '📚' },
  { text: 'Computing suitability scores for 22 crops...', emoji: '🌾' },
  { text: 'Ranking crops by combined score...', emoji: '📊' },
  { text: 'Generating analysis explanations...', emoji: '✍️' },
  { text: 'Preparing your results...', emoji: '✅' },
]

export default function Analysis() {
  const navigate = useNavigate()
  const { getApiPayload, setAnalysisResult, setSessionId } = useApp()
  const [step, setStep] = useState(0)
  const [error, setError] = useState(null)

  useEffect(() => {
    const interval = setInterval(() => {
      setStep(s => s < ANALYSIS_STEPS.length - 1 ? s + 1 : s)
    }, 600)

    const payload = getApiPayload()
    runAnalysis(payload)
      .then(result => {
        clearInterval(interval)
        setAnalysisResult(result)
        setSessionId(result.session_id)
        navigate('/recommendations')
      })
      .catch(err => {
        clearInterval(interval)
        setError(err.message)
      })

    return () => clearInterval(interval)
  }, [])

  if (error) return (
    <div className="page-bg" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div className="ff-card animate-fade-in" style={{ maxWidth: 440, width: '100%', padding: 36, textAlign: 'center' }}>
        <div style={{
          width: 64, height: 64, borderRadius: 16,
          background: 'var(--ff-error-bg)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 20px', fontSize: 28,
        }}>⚠️</div>
        <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--ff-text)', marginBottom: 10 }}>
          We couldn't complete the analysis
        </h2>
        <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.9rem', marginBottom: 24, lineHeight: 1.6 }}>
          {error}
        </p>
        <p style={{ color: 'var(--ff-text-muted)', fontSize: '0.8rem', marginBottom: 20 }}>
          Please check your inputs and try again.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          <button className="btn-secondary" onClick={() => navigate('/soil-test')}>← Edit Inputs</button>
          <button className="btn-primary" onClick={() => window.location.reload()}>Try Again</button>
        </div>
      </div>
    </div>
  )

  const progress = ((step + 1) / ANALYSIS_STEPS.length) * 100

  return (
    <div className="hero-bg" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div className="ff-card animate-fade-in" style={{ maxWidth: 440, width: '100%', padding: '44px 36px', textAlign: 'center' }}>

        {/* Animated leaf icon */}
        <div style={{ position: 'relative', width: 100, height: 100, margin: '0 auto 28px' }}>
          {/* Outer pulse ring */}
          <div style={{
            position: 'absolute', inset: 0, borderRadius: '50%',
            background: 'rgba(19, 138, 75, 0.1)',
            animation: 'pulse 2s ease-in-out infinite',
          }} />
          {/* Inner circle */}
          <div style={{
            position: 'absolute', inset: 8, borderRadius: '50%',
            background: 'var(--ff-soft)',
            border: '2px solid rgba(19,138,75,0.2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Leaf size={38} style={{ color: 'var(--ff-primary)', animation: 'leafPulse 1.8s ease-in-out infinite' }} />
          </div>
        </div>

        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--ff-text)', marginBottom: 8 }}>
          Analysing Your Farm
        </h2>
        <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.9rem', marginBottom: 28 }}>
          Running ML model + agricultural rules for 22 crops...
        </p>

        {/* Current step text */}
        <div style={{
          height: 50, display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: 'var(--ff-soft)', borderRadius: 12,
          border: '1px solid rgba(19,138,75,0.15)',
          padding: '0 16px', marginBottom: 20,
          transition: 'all 0.4s ease',
        }}>
          <span style={{ fontSize: '0.85rem' }}>{ANALYSIS_STEPS[step].emoji}</span>
          <p style={{ color: 'var(--ff-primary)', fontSize: '0.85rem', fontWeight: 500, marginLeft: 8 }}>
            {ANALYSIS_STEPS[step].text}
          </p>
        </div>

        {/* Progress bar */}
        <div className="score-bar">
          <div
            className="score-bar-fill score-gradient-high"
            style={{ width: `${progress}%`, transition: 'width 0.5s ease' }}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)' }}>Step {step + 1} of {ANALYSIS_STEPS.length}</span>
          <span style={{ fontSize: '0.72rem', color: 'var(--ff-primary)', fontWeight: 600 }}>{Math.round(progress)}%</span>
        </div>

        <p style={{ color: 'var(--ff-text-muted)', fontSize: '0.75rem', marginTop: 20 }}>
          No external AI API called — analysis runs entirely on your data
        </p>
      </div>
    </div>
  )
}
