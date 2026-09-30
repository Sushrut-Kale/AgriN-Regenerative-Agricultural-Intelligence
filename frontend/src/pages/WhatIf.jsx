import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { runWhatIf, getCrops } from '../services/api'
import { ArrowLeft, Zap, AlertTriangle, RotateCcw } from 'lucide-react'

const SIMULATABLE = [
  { key: 'ph',          label: 'Soil pH',               unit: '',      min: 3.5, max: 10.0, step: 0.1, emoji: '⚗️' },
  { key: 'OC',          label: 'Organic Carbon (OC)',   unit: '%',     min: 0.1, max: 3.0,  step: 0.05, emoji: '🍂' },
  { key: 'rainfall',    label: 'Rainfall Assumption',   unit: 'mm',    min: 100, max: 2500, step: 25,   emoji: '🌧️' },
  { key: 'temperature', label: 'Temperature Assumption', unit: '°C',   min: 10,  max: 48,   step: 0.5,  emoji: '🌡️' },
  { key: 'N',           label: 'Nitrogen (N)',          unit: 'kg/ha', min: 0,   max: 800,  step: 10,   emoji: '🌱' },
  { key: 'P',           label: 'Phosphorus (P)',        unit: 'kg/ha', min: 0,   max: 300,  step: 5,    emoji: '🌿' },
  { key: 'K',           label: 'Potassium (K)',         unit: 'kg/ha', min: 0,   max: 1200, step: 10,   emoji: '🍃' },
  { key: 'EC',          label: 'Salinity (EC)',         unit: 'dS/m',  min: 0.1, max: 8.0,  step: 0.1,  emoji: '🧂' },
]


export default function WhatIf() {
  const navigate = useNavigate()
  const { soilData, envData, getApiPayload } = useApp()
  const [crops, setCrops] = useState([])
  const [selectedCrop, setSelectedCrop] = useState('')
  const [changes, setChanges] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getCrops().then(d => setCrops(d.crops || [])).catch(() => {})
  }, [])

  const getCurrentValue = key => {
    const soil = soilData[key]
    const env = envData[key]
    return soil !== '' ? soil : env !== '' ? env : null
  }

  const handleChange = (key, value) =>
    setChanges(prev => ({ ...prev, [key]: parseFloat(value) }))

  const resetParam = key =>
    setChanges(prev => { const n = { ...prev }; delete n[key]; return n })

  const handleSimulate = async () => {
    if (!selectedCrop || Object.keys(changes).length === 0) return
    setLoading(true); setError(null)
    const payload = getApiPayload()
    try {
      const res = await runWhatIf({
        crop_name: selectedCrop,
        original_soil: payload.soil_data,
        original_env: payload.env_data,
        farm_data: payload.farm_data,
        simulated_changes: changes,
        session_id: payload.session_id,
      })
      setResult(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const changeCount = Object.keys(changes).length
  const cropInfo = crops.find(c => c.id === selectedCrop)

  return (
    <div className="page-bg" style={{ minHeight: '100vh' }}>

      {/* ── Top bar ───────────────────────────────────────────── */}
      <div className="ff-nav px-6 py-4 flex items-center gap-3" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            background: 'var(--ff-soft)', border: '1px solid var(--ff-border)',
            borderRadius: 10, padding: '6px 10px', cursor: 'pointer',
            display: 'flex', alignItems: 'center', color: 'var(--ff-text-secondary)',
          }}
        >
          <ArrowLeft size={18} />
        </button>
        <div>
          <h1 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--ff-text)', display: 'flex', alignItems: 'center', gap: 7 }}>
            <Zap size={18} style={{ color: 'var(--ff-warning)' }} />
            What-If Simulator
          </h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--ff-text-secondary)' }}>
            Explore how changing conditions affects crop suitability
          </p>
        </div>
      </div>

      <div className="ff-container-narrow" style={{ paddingTop: 24, paddingBottom: 48 }}>

        {/* Disclaimer */}
        <div className="ff-alert-warning animate-fade-in" style={{ marginBottom: 20, display: 'flex', alignItems: 'flex-start', gap: 10 }}>
          <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
          <span style={{ lineHeight: 1.6 }}>
            <strong>Simulation only.</strong> Values entered here are hypothetical and have not been measured in your field.
            Simulated results do not guarantee the same outcome in practice.
          </span>
        </div>

        {/* Step 1 — Crop selector */}
        <div className="ff-card animate-fade-in" style={{ padding: 24, marginBottom: 16 }}>
          <h2 style={{ fontWeight: 700, color: 'var(--ff-text)', fontSize: '0.95rem', marginBottom: 14 }}>
            1. Select crop to simulate
          </h2>
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8,
            maxHeight: 200, overflowY: 'auto',
          }} className="crop-sel-grid">
            {crops.map(c => {
              const isSel = selectedCrop === c.id
              return (
                <button
                  key={c.id}
                  onClick={() => setSelectedCrop(c.id)}
                  style={{
                    textAlign: 'left', padding: '8px 12px',
                    borderRadius: 10,
                    border: isSel ? '2px solid var(--ff-warning)' : '1.5px solid var(--ff-border)',
                    background: isSel ? 'var(--ff-warning-bg)' : 'white',
                    color: isSel ? 'var(--ff-warning)' : 'var(--ff-text-secondary)',
                    fontWeight: isSel ? 700 : 400,
                    fontSize: '0.82rem',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {c.common_name}
                </button>
              )
            })}
          </div>
        </div>

        {/* Step 2 — Sliders */}
        <div className="ff-card animate-fade-in" style={{ padding: 24, marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <h2 style={{ fontWeight: 700, color: 'var(--ff-text)', fontSize: '0.95rem' }}>
              2. Change conditions to simulate
              {changeCount > 0 && (
                <span style={{
                  marginLeft: 10, fontSize: '0.75rem', fontWeight: 700,
                  background: 'var(--ff-warning-bg)', color: 'var(--ff-warning)',
                  padding: '2px 10px', borderRadius: 999,
                  border: '1px solid rgba(216,155,24,0.3)',
                }}>
                  {changeCount} changed
                </span>
              )}
            </h2>
            {changeCount > 0 && (
              <button
                onClick={() => setChanges({})}
                style={{
                  display: 'flex', alignItems: 'center', gap: 5,
                  fontSize: '0.78rem', color: 'var(--ff-error)',
                  background: 'none', border: 'none', cursor: 'pointer',
                }}
              >
                <RotateCcw size={13} /> Reset All
              </button>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {SIMULATABLE.map(param => {
              const original = getCurrentValue(param.key)
              const simValue = changes[param.key] ?? (original !== null ? parseFloat(original) : (param.min + param.max) / 2)
              const isChanged = changes[param.key] !== undefined

              return (
                <div
                  key={param.key}
                  className={isChanged ? 'sim-card-changed' : 'sim-card-default'}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: '1rem' }}>{param.emoji}</span>
                      <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--ff-text)' }}>
                        {param.label}
                      </span>
                      {param.unit && (
                        <span style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', background: '#F1F4F2', padding: '1px 7px', borderRadius: 6 }}>
                          {param.unit}
                        </span>
                      )}
                      {isChanged && (
                        <span style={{
                          fontSize: '0.68rem', fontWeight: 700,
                          background: 'var(--ff-warning-bg)', color: 'var(--ff-warning)',
                          padding: '2px 8px', borderRadius: 999,
                          border: '1px solid rgba(216,155,24,0.3)',
                        }}>
                          Changed
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {original !== null && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--ff-text-muted)' }}>
                          Original: <strong>{original}{param.unit}</strong>
                        </span>
                      )}
                      <span style={{ fontSize: '0.9rem', fontWeight: 800, color: isChanged ? 'var(--ff-warning)' : 'var(--ff-text)' }}>
                        {simValue}{param.unit}
                      </span>
                      {isChanged && (
                        <button
                          onClick={() => resetParam(param.key)}
                          style={{ fontSize: '0.72rem', color: 'var(--ff-error)', background: 'none', border: 'none', cursor: 'pointer' }}
                        >
                          <RotateCcw size={12} />
                        </button>
                      )}
                    </div>
                  </div>
                  <input
                    type="range"
                    min={param.min} max={param.max} step={param.step}
                    value={simValue}
                    onChange={e => handleChange(param.key, e.target.value)}
                    style={{ accentColor: isChanged ? 'var(--ff-warning)' : 'var(--ff-primary)' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 2 }}>
                    <span style={{ fontSize: '0.68rem', color: 'var(--ff-text-muted)' }}>{param.min}{param.unit}</span>
                    <span style={{ fontSize: '0.68rem', color: 'var(--ff-text-muted)' }}>{param.max}{param.unit}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Run button */}
        <button
          className="btn-primary"
          style={{ width: '100%', justifyContent: 'center', padding: '14px', fontSize: '0.95rem' }}
          onClick={handleSimulate}
          disabled={!selectedCrop || changeCount === 0 || loading}
        >
          <Zap size={20} />
          {loading
            ? 'Simulating...'
            : `Run What-If Simulation${changeCount > 0 ? ` (${changeCount} parameter${changeCount !== 1 ? 's' : ''})` : ''}`
          }
        </button>

        {/* Error */}
        {error && (
          <div className="ff-alert-error animate-fade-in" style={{ marginTop: 14 }}>⚠️ {error}</div>
        )}

        {/* Result */}
        {result && !loading && (
          <div className="animate-fade-in" style={{ marginTop: 24 }}>
            <WhatIfResult result={result} cropName={cropInfo?.common_name || selectedCrop} />
          </div>
        )}
      </div>

      <style>{`
        @media (max-width: 640px) { .crop-sel-grid { grid-template-columns: repeat(2, 1fr) !important; } }
      `}</style>
    </div>
  )
}

function WhatIfResult({ result, cropName }) {
  const { before, after, score_change, changed_params, explanation, disclaimer, scenario_comparison } = result
  const improved = score_change > 0
  const neutral = score_change === 0

  return (
    <div className="ff-card" style={{ padding: 24 }}>
      {/* Explicit Simulation Label (Requirement 6) */}
      <div style={{
        background: '#FEF3C7', border: '1px solid #F59E0B', borderRadius: 8,
        padding: '8px 14px', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8
      }}>
        <span style={{ fontSize: '1rem' }}>🔬</span>
        <div>
          <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#92400E' }}>
            Scenario simulation
          </span>
          <span style={{ fontSize: '0.78rem', color: '#B45309', marginLeft: 6 }}>
            — Not a prediction of actual future yield
          </span>
        </div>
      </div>

      <h3 style={{
        fontSize: '1.15rem', fontWeight: 800, color: 'var(--ff-text)',
        display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20,
      }}>
        <Zap size={20} style={{ color: 'var(--ff-warning)' }} />
        Simulation Result: {cropName}
      </h3>

      {/* Before / After cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: 10, alignItems: 'center', marginBottom: 20 }}>
        <div className="before-card">
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--ff-info)', marginBottom: 8 }}>
            CURRENT
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 900, color: 'var(--ff-info)', lineHeight: 1 }}>
            {before.score}
            <span style={{ fontSize: '1rem', color: 'var(--ff-text-muted)', fontWeight: 400 }}>/100</span>
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--ff-text-secondary)', marginTop: 6 }}>{before.classification}</div>
        </div>

        {/* Delta */}
        <div style={{ textAlign: 'center' }}>
          <div className={improved ? 'delta-pill-positive' : neutral ? 'delta-pill-neutral' : 'delta-pill-negative'}>
            {improved ? '↑' : neutral ? '→' : '↓'}
            {score_change > 0 ? '+' : ''}{score_change.toFixed(1)}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--ff-text-muted)', marginTop: 4 }}>points</div>
        </div>

        <div className="after-card">
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--ff-primary)', marginBottom: 8 }}>
            SCENARIO
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 900, color: 'var(--ff-primary)', lineHeight: 1 }}>
            {after.score}
            <span style={{ fontSize: '1rem', color: 'var(--ff-text-muted)', fontWeight: 400 }}>/100</span>
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--ff-text-secondary)', marginTop: 6 }}>{after.classification}</div>
        </div>
      </div>

      {/* Multi-Dimensional CURRENT vs SCENARIO Matrix (Requirement 6) */}
      {scenario_comparison && (
        <div style={{ marginBottom: 20, background: '#F8FAF8', padding: 14, borderRadius: 10, border: '1px solid #E5E7EB' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 800, color: '#1F2937', marginBottom: 10 }}>
            CURRENT vs SCENARIO Agricultural Comparison
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: 10 }}>
            <div style={{ background: '#FFFFFF', padding: 10, borderRadius: 8, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.7rem', color: '#6B7280', fontWeight: 600 }}>Crop Suitability</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#111827', marginTop: 2 }}>
                {scenario_comparison.crop_suitability?.current} → {scenario_comparison.crop_suitability?.scenario}
                <span style={{ fontSize: '0.75rem', color: scenario_comparison.crop_suitability?.delta >= 0 ? '#059669' : '#DC2626', marginLeft: 6 }}>
                  ({scenario_comparison.crop_suitability?.delta >= 0 ? '+' : ''}{scenario_comparison.crop_suitability?.delta} pts)
                </span>
              </div>
            </div>

            <div style={{ background: '#FFFFFF', padding: 10, borderRadius: 8, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.7rem', color: '#6B7280', fontWeight: 600 }}>Soil Compatibility</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#111827', marginTop: 2 }}>
                {scenario_comparison.soil_compatibility?.current}% → {scenario_comparison.soil_compatibility?.scenario}%
              </div>
            </div>

            <div style={{ background: '#FFFFFF', padding: 10, borderRadius: 8, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.7rem', color: '#6B7280', fontWeight: 600 }}>Water Fit</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#111827', marginTop: 2 }}>
                {scenario_comparison.water_requirement?.current_water_fit}% → {scenario_comparison.water_requirement?.scenario_water_fit}%
              </div>
            </div>

            <div style={{ background: '#FFFFFF', padding: 10, borderRadius: 8, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.7rem', color: '#6B7280', fontWeight: 600 }}>Detected Risks</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#111827', marginTop: 2 }}>
                {scenario_comparison.risk_profile?.current_risk_count} risks → {scenario_comparison.risk_profile?.scenario_risk_count} risks
              </div>
            </div>

            <div style={{ background: '#FFFFFF', padding: 10, borderRadius: 8, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.7rem', color: '#6B7280', fontWeight: 600 }}>Farm Resilience</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#111827', marginTop: 2 }}>
                {scenario_comparison.farm_resilience?.current_score} → {scenario_comparison.farm_resilience?.scenario_score}
                <span style={{ fontSize: '0.7rem', color: '#6B7280', marginLeft: 4 }}>
                  ({scenario_comparison.farm_resilience?.scenario_tier || 'MODERATE'})
                </span>
              </div>
            </div>

            <div style={{ background: '#FFFFFF', padding: 10, borderRadius: 8, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.7rem', color: '#6B7280', fontWeight: 600 }}>Data Confidence</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#111827', marginTop: 2 }}>
                {scenario_comparison.data_confidence?.current_level} → {scenario_comparison.data_confidence?.scenario_level}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Changed params */}
      <div style={{ marginBottom: 16 }}>
        <h4 style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--ff-text-secondary)', marginBottom: 8 }}>
          Parameters changed in simulation:
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }} className="params-changed-grid">
          {Object.entries(changed_params).map(([key, vals]) => (
            <div key={key} style={{
              background: '#F6F8F7', borderRadius: 10, padding: '10px 12px',
              border: '1px solid var(--ff-border)',
            }}>
              <p style={{ fontSize: '0.72rem', color: 'var(--ff-text-secondary)', fontWeight: 600, marginBottom: 4 }}>{key}</p>
              <p style={{ fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ color: 'var(--ff-info)', fontWeight: 700 }}>{vals.before ?? '—'}</span>
                <span style={{ color: 'var(--ff-text-muted)' }}>→</span>
                <span style={{ color: 'var(--ff-warning)', fontWeight: 700 }}>{vals.after}</span>
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* AI Explanation */}
      <div className="ai-card" style={{ marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <div className="ai-sparkle">✦</div>
          <span style={{ fontWeight: 600, fontSize: '0.82rem', color: 'var(--ff-primary)' }}>AgriN Agricultural Reasoning</span>
        </div>
        <p style={{ fontSize: '0.88rem', color: 'var(--ff-text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
          {explanation}
        </p>
      </div>

      {/* Simulation disclaimer */}
      <div className="ff-alert-warning" style={{ fontSize: '0.78rem' }}>
        ⚠️ {disclaimer}
      </div>

      <style>{`
        @media (max-width: 640px) { .params-changed-grid { grid-template-columns: repeat(2, 1fr) !important; } }
      `}</style>
    </div>
  )
}

