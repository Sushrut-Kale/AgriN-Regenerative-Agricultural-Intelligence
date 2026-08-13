import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { getLiveWeather } from '../services/api'
import { Info, Thermometer, Droplets, CloudRain, Radio } from 'lucide-react'
import StepLayout from '../components/StepLayout'

const ENV_PARAMS = [
  {
    key: 'temperature', label: 'Average Temperature',
    unit: '°C', min: -5, max: 50, step: 0.5, placeholder: 'e.g. 28',
    icon: <Thermometer size={18} style={{ color: '#E07B3A' }} />,
    color: '#E07B3A', bg: '#FFF4EE',
    tip: 'Average temperature during the growing season. Can be obtained from IMD website or local weather station.',
  },
  {
    key: 'humidity', label: 'Average Relative Humidity',
    unit: '%', min: 0, max: 100, step: 1, placeholder: 'e.g. 65',
    icon: <Droplets size={18} style={{ color: 'var(--ff-info)' }} />,
    color: '#3978B8', bg: '#EDF4FF',
    tip: 'Average relative humidity. Typical: Konkan 70–90%, Vidarbha 50–75%, Marathwada 40–65%.',
  },
  {
    key: 'rainfall', label: 'Annual Rainfall',
    unit: 'mm/yr', min: 0, max: 5000, step: 10, placeholder: 'e.g. 750',
    icon: <CloudRain size={18} style={{ color: 'var(--ff-primary)' }} />,
    color: 'var(--ff-primary)', bg: 'var(--ff-soft)',
    tip: 'Total annual rainfall in mm. Maharashtra range: 400mm (Solapur) to 3500mm (Konkan). Check IMD data.',
  },
]

const TYPICAL_VALUES = [
  { region: 'Vidarbha',        temp: 30, humidity: 60, rainfall: 1000 },
  { region: 'Marathwada',      temp: 29, humidity: 55, rainfall: 750  },
  { region: 'Western Plateau', temp: 27, humidity: 60, rainfall: 600  },
  { region: 'North MH',        temp: 28, humidity: 50, rainfall: 700  },
  { region: 'Konkan',          temp: 28, humidity: 80, rainfall: 2500 },
]

export default function Environment() {
  const navigate = useNavigate()
  const { farmData, envData, setEnvData } = useApp()
  const [tooltip, setTooltip] = useState(null)
  const [fetchingLive, setFetchingLive] = useState(false)
  const [liveNotice, setLiveNotice] = useState(null)

  const update = (key, value) => setEnvData(prev => ({ ...prev, [key]: value }))
  const prefill = vals => setEnvData({ temperature: vals.temp, humidity: vals.humidity, rainfall: vals.rainfall })

  const handleFetchLiveWeather = async () => {
    setFetchingLive(true)
    setLiveNotice(null)
    try {
      const district = farmData.district || 'Parbhani'
      const res = await getLiveWeather(district)
      setEnvData({
        temperature: res.temperature,
        humidity: res.humidity,
        rainfall: res.rainfall
      })
      setLiveNotice(`Fetched live weather for ${res.district} (${res.source}): Temp ${res.temperature}°C, Humidity ${res.humidity}%`)
    } catch (err) {
      setLiveNotice('Failed to fetch live weather. Please enter values manually.')
    } finally {
      setFetchingLive(false)
    }
  }

  return (
    <StepLayout step={3} title="Environmental Conditions" subtitle="Temperature, humidity, and rainfall in your growing area">

      {/* Live weather banner */}
      <div className="ff-card" style={{ padding: '16px 20px', marginBottom: 20, background: 'linear-gradient(135deg, #F0FDF4 0%, #E6F4EA 100%)', border: '1px solid #BBF7D0' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ fontWeight: 600, color: '#166534', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 6 }}>
              <Radio size={16} className="pulse-icon" /> Live Real-Time Weather Sync
            </div>
            <div style={{ fontSize: '0.78rem', color: '#15803D', marginTop: 2 }}>
              Automatically fetch real-time climate data for {farmData.district || 'Parbhani'}, Maharashtra
            </div>
          </div>
          <button
            className="btn-primary"
            style={{ fontSize: '0.82rem', padding: '8px 16px' }}
            onClick={handleFetchLiveWeather}
            disabled={fetchingLive}
          >
            {fetchingLive ? 'Fetching Live Data...' : '📡 Fetch Live Weather'}
          </button>
        </div>
        {liveNotice && (
          <div style={{ marginTop: 10, fontSize: '0.78rem', color: '#166534', fontWeight: 500 }}>
            {liveNotice}
          </div>
        )}
      </div>

      {/* Info notice */}
      <div className="ff-alert-info" style={{ marginBottom: 20, display: 'flex', alignItems: 'flex-start', gap: 10 }}>
        <span style={{ fontSize: '1rem', flexShrink: 0 }}>ℹ️</span>
        <span>
          Values can be obtained from the{' '}
          <strong>India Meteorological Department (IMD)</strong> website, local weather stations, or your district agricultural office.
          All fields are optional.
        </span>
      </div>

      {/* Quick-fill region pills */}
      <div className="ff-card" style={{ padding: '16px 20px', marginBottom: 20 }}>
        <p style={{ fontSize: '0.82rem', color: 'var(--ff-text-secondary)', marginBottom: 10, fontWeight: 500 }}>
          Quick-fill with typical Maharashtra regional values:
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {TYPICAL_VALUES.map(v => (
            <button
              key={v.region}
              className="region-pill"
              onClick={() => prefill(v)}
            >
              📍 {v.region} ({v.rainfall}mm, {v.temp}°C)
            </button>
          ))}
        </div>
        <p style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', marginTop: 8 }}>
          These are approximate regional averages — enter your actual local values for best results.
        </p>
      </div>


      {/* Parameter cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }} className="env-grid">
        {ENV_PARAMS.map(param => (
          <div
            key={param.key}
            className="ff-card"
            style={{ padding: 20, borderTop: `3px solid ${param.color}`, position: 'relative' }}
          >
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <div style={{
                width: 34, height: 34, borderRadius: 9,
                background: param.bg,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                {param.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--ff-text)' }}>{param.label}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)' }}>Optional</div>
              </div>
              <button
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--ff-text-muted)', padding: 2 }}
                onMouseEnter={() => setTooltip(param.key)}
                onMouseLeave={() => setTooltip(null)}
              >
                <Info size={14} />
              </button>
            </div>

            {/* Tooltip */}
            {tooltip === param.key && (
              <div style={{
                position: 'absolute', zIndex: 20, bottom: '100%', left: 0, marginBottom: 6, right: 0,
                background: 'white', border: '1px solid var(--ff-border)',
                borderRadius: 10, padding: '10px 12px', fontSize: '0.75rem',
                color: 'var(--ff-text-secondary)', boxShadow: '0 8px 24px rgba(20,50,30,0.12)', lineHeight: 1.5,
              }}>
                {param.tip}
              </div>
            )}

            {/* Input */}
            <div style={{ position: 'relative' }}>
              <input
                id={`env-${param.key}`}
                className="farm-input"
                type="number"
                min={param.min} max={param.max} step={param.step}
                placeholder={param.placeholder}
                value={envData[param.key]}
                onChange={e => update(param.key, e.target.value)}
                style={{ paddingRight: 56 }}
              />
              <span style={{
                position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)',
                fontSize: '0.75rem', color: 'var(--ff-text-muted)', pointerEvents: 'none',
              }}>
                {param.unit}
              </span>
            </div>

            {/* Mini range bar */}
            {envData[param.key] !== '' && (
              <div style={{ marginTop: 10 }}>
                <div className="score-bar">
                  <div
                    className="score-bar-fill"
                    style={{
                      width: `${Math.min(100, ((parseFloat(envData[param.key]) - param.min) / (param.max - param.min)) * 100)}%`,
                      background: param.color,
                    }}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
                  <span style={{ fontSize: '0.68rem', color: 'var(--ff-text-muted)' }}>{param.min}{param.unit}</span>
                  <span style={{ fontSize: '0.68rem', color: 'var(--ff-text-muted)' }}>{param.max}{param.unit}</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 28 }}>
        <button className="btn-secondary" onClick={() => navigate('/soil-test')}>← Back</button>
        <button className="btn-primary" onClick={() => navigate('/analysis')}>
          Analyse My Farm →
        </button>
      </div>

      <style>{`
        @media (max-width: 768px) { .env-grid { grid-template-columns: 1fr !important; } }
      `}</style>
    </StepLayout>
  )
}
