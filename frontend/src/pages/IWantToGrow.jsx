import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { checkFeasibility, getCrops } from '../services/api'
import { ArrowLeft, Search, Shield, Zap, CheckCircle } from 'lucide-react'
import SuitabilityMeter from '../components/SuitabilityMeter'

export default function IWantToGrow() {
  const navigate = useNavigate()
  const { getApiPayload, setFeasibilityResult, setSelectedCrop } = useApp()
  const [crops, setCrops] = useState([])
  const [search, setSearch] = useState('')
  const [chosen, setChosen] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getCrops().then(data => setCrops(data.crops || [])).catch(() => {})
  }, [])

  const filtered = crops.filter(c =>
    c.common_name.toLowerCase().includes(search.toLowerCase()) ||
    c.local_name?.toLowerCase().includes(search.toLowerCase())
  )

  const handleAnalyse = async () => {
    if (!chosen) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const payload = { ...getApiPayload(), chosen_crop: chosen }
      const res = await checkFeasibility(payload)
      setResult(res)
      setFeasibilityResult(res)
      setSelectedCrop(res.result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const chosenCropInfo = crops.find(c => c.id === chosen)

  return (
    <div className="page-bg" style={{ minHeight: '100vh' }}>

      {/* ── Top bar ───────────────────────────────────────────── */}
      <div className="ff-nav px-6 py-4 flex items-center gap-3" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
        <button
          onClick={() => navigate('/recommendations')}
          style={{
            background: 'var(--ff-soft)', border: '1px solid var(--ff-border)',
            borderRadius: 10, padding: '6px 10px', cursor: 'pointer',
            display: 'flex', alignItems: 'center', color: 'var(--ff-text-secondary)',
          }}
        >
          <ArrowLeft size={18} />
        </button>
        <div>
          <h1 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--ff-text)' }}>I Want to Grow This</h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--ff-text-secondary)' }}>Check feasibility for your chosen crop</p>
        </div>
      </div>

      <div className="ff-container-narrow" style={{ paddingTop: 24, paddingBottom: 48 }}>

        {/* Explanation */}
        <div className="ff-alert-info animate-fade-in" style={{ marginBottom: 20, display: 'flex', alignItems: 'flex-start', gap: 10 }}>
          <span style={{ fontSize: '1rem', flexShrink: 0 }}>💡</span>
          <span style={{ lineHeight: 1.6 }}>
            Have a specific crop in mind? Select it below and FarmFriend AI will check how well your current soil
            and environmental conditions match that crop's requirements.
          </span>
        </div>

        {/* Crop selector */}
        <div className="ff-card animate-fade-in" style={{ padding: 24, marginBottom: 20 }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--ff-text)', marginBottom: 16 }}>
            What would you like to grow?
          </h2>

          {/* Search input */}
          <div style={{ position: 'relative', marginBottom: 16 }}>
            <Search size={16} style={{
              position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
              color: 'var(--ff-text-muted)', pointerEvents: 'none',
            }} />
            <input
              className="farm-input"
              style={{ paddingLeft: 38 }}
              placeholder="🔍 Search crops..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>

          {/* Crop grid */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8,
            maxHeight: 280, overflowY: 'auto',
            paddingRight: 4,
          }} className="crops-grid">
            {filtered.map(crop => {
              const isChosen = chosen === crop.id
              return (
                <button
                  key={crop.id}
                  onClick={() => setChosen(crop.id)}
                  style={{
                    textAlign: 'left', padding: '10px 12px',
                    borderRadius: 12,
                    border: isChosen ? '2px solid var(--ff-primary)' : '1.5px solid var(--ff-border)',
                    background: isChosen ? 'var(--ff-light)' : 'white',
                    color: isChosen ? 'var(--ff-primary)' : 'var(--ff-text)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    position: 'relative',
                  }}
                >
                  {isChosen && (
                    <CheckCircle size={12} style={{
                      position: 'absolute', top: 6, right: 6,
                      color: 'var(--ff-primary)',
                    }} />
                  )}
                  <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{crop.common_name}</div>
                  {crop.local_name && (
                    <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', marginTop: 1 }}>{crop.local_name}</div>
                  )}
                </button>
              )
            })}
          </div>

          {/* Selected + CTA */}
          {chosen && (
            <div style={{
              marginTop: 16, paddingTop: 16,
              borderTop: '1px solid var(--ff-border)',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12,
            }}>
              <div>
                <span style={{ fontSize: '0.85rem', color: 'var(--ff-text-secondary)' }}>Selected: </span>
                <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--ff-primary)' }}>
                  {chosenCropInfo?.common_name}
                </span>
              </div>
              <button
                className="btn-primary"
                onClick={handleAnalyse}
                disabled={loading}
              >
                {loading ? '🌱 Analysing...' : 'Check Feasibility →'}
              </button>
            </div>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '40px 0', gap: 14 }}>
            <div className="loader" />
            <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.9rem' }}>
              Analysing {chosenCropInfo?.common_name} feasibility...
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="ff-alert-error animate-fade-in">
            ⚠️ {error}
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <div className="animate-fade-in">
            <FeasibilityResult result={result} onWhatIf={() => navigate('/what-if')} />
          </div>
        )}
      </div>

      <style>{`
        @media (max-width: 640px) { .crops-grid { grid-template-columns: repeat(2, 1fr) !important; } }
      `}</style>
    </div>
  )
}

function FeasibilityResult({ result, onWhatIf }) {
  const r = result.result
  const label = result.feasibility_label
  const color = result.feasibility_color

  const colorMap = {
    green:  { bg: 'var(--ff-success-bg)', border: 'rgba(19,138,75,0.25)',   text: 'var(--ff-primary)', top: 'var(--ff-primary)' },
    yellow: { bg: 'var(--ff-warning-bg)', border: 'rgba(216,155,24,0.3)',   text: 'var(--ff-warning)', top: 'var(--ff-warning)' },
    orange: { bg: '#FFF4EE',              border: 'rgba(224,123,58,0.3)',    text: '#E07B3A',           top: '#E07B3A' },
    red:    { bg: 'var(--ff-error-bg)',   border: 'rgba(217,75,75,0.25)',   text: 'var(--ff-error)',   top: 'var(--ff-error)' },
  }

  const c = colorMap[color] || colorMap.yellow

  return (
    <div>
      <h3 style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--ff-text)', marginBottom: 12 }}>
        Feasibility Result
      </h3>

      <div
        className="ff-card"
        style={{ borderTop: `4px solid ${c.top}`, padding: 24 }}
      >
        {/* Score + Name */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
          <SuitabilityMeter score={r.final_score} size="md" showLabel={false} />
          <div>
            <h4 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--ff-text)' }}>{r.common_name}</h4>
            <p style={{ fontWeight: 700, fontSize: '0.9rem', color: c.text }}>
              {label} — {r.final_score}/100
            </p>
          </div>
        </div>

        {/* Score bar */}
        <div className="score-bar" style={{ marginBottom: 16 }}>
          <div className="score-bar-fill" style={{
            width: `${r.final_score}%`,
            background: c.top,
          }} />
        </div>

        {/* Explanation */}
        <div style={{
          background: c.bg, border: `1px solid ${c.border}`,
          borderRadius: 12, padding: 16, marginBottom: 16,
        }}>
          <p style={{ fontSize: '0.88rem', color: 'var(--ff-text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
            {result.feasibility_explanation}
          </p>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn-secondary" style={{ flex: 1 }} onClick={onWhatIf}>
            <Zap size={15} /> Try What-If Simulation
          </button>
        </div>

        {/* Disclaimer */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, marginTop: 14 }}>
          <Shield size={13} style={{ color: 'var(--ff-text-muted)', flexShrink: 0, marginTop: 2 }} />
          <p style={{ fontSize: '0.75rem', color: 'var(--ff-text-muted)', lineHeight: 1.5 }}>
            This feasibility analysis is a model-based estimate. Consult your local KVK or agricultural officer before farming decisions.
          </p>
        </div>
      </div>
    </div>
  )
}
