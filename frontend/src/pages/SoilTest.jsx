import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { Info, Sprout, FlaskConical, Beaker } from 'lucide-react'
import StepLayout from '../components/StepLayout'

const SOIL_PARAMS = [
  {
    section: 'Macronutrients',
    accent: 'var(--ff-primary)',
    accentBg: 'var(--ff-soft)',
    icon: '🌱',
    params: [
      { key: 'N',  label: 'Nitrogen (N)',    unit: 'kg/ha', min: 0, max: 800,  placeholder: 'e.g. 280', tip: 'Available nitrogen. Alkaline KMnO₄ method. Low <240, Medium 240–480, High >480 kg/ha (ICAR)' },
      { key: 'P',  label: 'Phosphorus (P)',  unit: 'kg/ha', min: 0, max: 300,  placeholder: 'e.g. 15',  tip: 'Available phosphorus. Olsen method. Low <11, Medium 11–22, High >22 kg/ha (ICAR)' },
      { key: 'K',  label: 'Potassium (K)',   unit: 'kg/ha', min: 0, max: 1200, placeholder: 'e.g. 180', tip: 'Available potassium. NH₄OAc method. Low <110, Medium 110–280, High >280 kg/ha (ICAR)' },
    ],
  },
  {
    section: 'Secondary Nutrient',
    accent: '#3978B8',
    accentBg: '#EDF4FF',
    icon: '💧',
    params: [
      { key: 'S', label: 'Sulphur (S)', unit: 'ppm', min: 0, max: 100, placeholder: 'e.g. 12', tip: 'Available sulphur. Critical level: 10 ppm. Below 10 = deficient (ICAR SHC)' },
    ],
  },
  {
    section: 'Micronutrients',
    accent: '#7C3AED',
    accentBg: '#F5F0FF',
    icon: '🔬',
    params: [
      { key: 'Zn', label: 'Zinc (Zn)',       unit: 'ppm', min: 0, max: 20,  placeholder: 'e.g. 0.8', tip: 'DTPA-extractable zinc. Critical level: 0.6 ppm (ICAR)' },
      { key: 'Fe', label: 'Iron (Fe)',        unit: 'ppm', min: 0, max: 100, placeholder: 'e.g. 6.5', tip: 'DTPA-extractable iron. Critical level: 4.5 ppm (ICAR SHC)' },
      { key: 'Cu', label: 'Copper (Cu)',      unit: 'ppm', min: 0, max: 20,  placeholder: 'e.g. 0.5', tip: 'DTPA-extractable copper. Critical level: 0.2 ppm (ICAR SHC)' },
      { key: 'Mn', label: 'Manganese (Mn)',   unit: 'ppm', min: 0, max: 50,  placeholder: 'e.g. 3.2', tip: 'DTPA-extractable manganese. Critical level: 2.0 ppm (ICAR SHC)' },
      { key: 'B',  label: 'Boron (B)',        unit: 'ppm', min: 0, max: 10,  placeholder: 'e.g. 0.7', tip: 'Hot water extractable boron. Critical level: 0.5 ppm (ICAR SHC)' },
    ],
  },
  {
    section: 'Soil Properties',
    accent: '#D89B18',
    accentBg: '#FFF7E1',
    icon: '⚗️',
    params: [
      { key: 'ph', label: 'Soil pH',                      unit: '',     min: 3.0, max: 11.0, placeholder: 'e.g. 7.2', step: 0.1,  tip: 'pH in 1:2 soil:water. Optimal 6.5–7.5. <6 acidic, >8.5 alkaline (ICAR)' },
      { key: 'EC', label: 'Electrical Conductivity (EC)', unit: 'dS/m', min: 0,   max: 20,   placeholder: 'e.g. 0.4', step: 0.01, tip: 'Soil salinity. Normal <1.0 dS/m. >4 dS/m injurious to most crops (ICAR)' },
      { key: 'OC', label: 'Organic Carbon (OC)',           unit: '%',    min: 0,   max: 5,    placeholder: 'e.g. 0.45', step: 0.01, tip: 'Walkley-Black method. Low <0.5%, Medium 0.5–0.75%, High >0.75% (ICAR)' },
    ],
  },
]

export default function SoilTest() {
  const navigate = useNavigate()
  const { soilData, setSoilData } = useApp()
  const [tooltip, setTooltip] = useState(null)

  const update = (key, value) => setSoilData(prev => ({ ...prev, [key]: value }))

  const filledCount = Object.values(soilData).filter(v => v !== '' && v !== null).length
  const totalCount = 12
  const pct = (filledCount / totalCount) * 100

  return (
    <StepLayout
      step={2}
      title="Soil Test Values"
      subtitle="Enter values from your Soil Health Card, soil testing lab report, or soil-testing device"
    >

      {/* Progress indicator */}
      <div className="ff-card" style={{ padding: '16px 20px', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--ff-text-secondary)' }}>Parameters entered</span>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--ff-primary)' }}>{filledCount} / {totalCount}</span>
          </div>
          <div className="score-bar">
            <div className="score-bar-fill score-gradient-high" style={{ width: `${pct}%` }} />
          </div>
        </div>
        <div style={{ fontSize: '0.78rem', color: 'var(--ff-text-muted)', maxWidth: 200, lineHeight: 1.4 }}>
          More data improves accuracy. Missing values are indicated, not penalised.
        </div>
      </div>

      {/* Info notice */}
      <div className="ff-alert-warning" style={{ marginBottom: 20, display: 'flex', alignItems: 'flex-start', gap: 10 }}>
        <span style={{ fontSize: '1rem', flexShrink: 0 }}>ℹ️</span>
        <span>
          <strong>Source:</strong> Get these values from your{' '}
          <strong>Soil Health Card</strong> (soilhealth.dac.gov.in), soil testing lab report, or soil-testing device.
          Do not guess values.
        </span>
      </div>

      {/* Soil parameter sections */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {SOIL_PARAMS.map(section => (
          <div
            key={section.section}
            className="ff-card"
            style={{
              padding: 20,
              borderLeft: `4px solid ${section.accent}`,
            }}
          >
            {/* Section header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <span style={{ fontSize: '1.1rem' }}>{section.icon}</span>
              <span style={{
                fontSize: '0.78rem', fontWeight: 700,
                textTransform: 'uppercase', letterSpacing: '0.06em',
                color: section.accent,
              }}>
                {section.section}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }} className="params-grid">
              {section.params.map(param => (
                <div key={param.key} style={{ position: 'relative' }}>
                  {/* Label row */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 6 }}>
                    <label style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--ff-text)', flex: 1 }}>
                      {param.label}
                    </label>
                    {param.unit && (
                      <span style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', background: '#F1F4F2', padding: '1px 7px', borderRadius: 6 }}>
                        {param.unit}
                      </span>
                    )}
                    <button
                      style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 2, color: 'var(--ff-text-muted)' }}
                      onMouseEnter={() => setTooltip(param.key)}
                      onMouseLeave={() => setTooltip(null)}
                    >
                      <Info size={13} />
                    </button>
                  </div>

                  {/* Tooltip */}
                  {tooltip === param.key && (
                    <div style={{
                      position: 'absolute', zIndex: 30, bottom: '100%', left: 0, marginBottom: 6,
                      background: 'white', border: '1px solid var(--ff-border)',
                      borderRadius: 10, padding: '10px 12px', fontSize: '0.75rem',
                      color: 'var(--ff-text-secondary)', width: 240,
                      boxShadow: '0 8px 24px rgba(20,50,30,0.12)', lineHeight: 1.5,
                    }}>
                      {param.tip}
                    </div>
                  )}

                  {/* Input */}
                  <div style={{ position: 'relative' }}>
                    <input
                      id={`soil-${param.key}`}
                      className="farm-input"
                      type="number"
                      min={param.min}
                      max={param.max}
                      step={param.step || 0.1}
                      placeholder={param.placeholder}
                      value={soilData[param.key]}
                      onChange={e => update(param.key, e.target.value)}
                      style={{ paddingRight: param.unit ? 56 : 14 }}
                    />
                    {param.unit && (
                      <span style={{
                        position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)',
                        fontSize: '0.75rem', color: 'var(--ff-text-muted)', pointerEvents: 'none',
                      }}>
                        {param.unit}
                      </span>
                    )}
                  </div>

                  {soilData[param.key] === '' && (
                    <p style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', marginTop: 3 }}>
                      Optional
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 28 }}>
        <button className="btn-secondary" onClick={() => navigate('/farm-details')}>← Back</button>
        <button className="btn-primary" onClick={() => navigate('/environment')}>
          Next: Environment →
        </button>
      </div>

      <style>{`
        @media (max-width: 768px) { .params-grid { grid-template-columns: repeat(2, 1fr) !important; } }
        @media (max-width: 480px) { .params-grid { grid-template-columns: 1fr !important; } }
      `}</style>
    </StepLayout>
  )
}
