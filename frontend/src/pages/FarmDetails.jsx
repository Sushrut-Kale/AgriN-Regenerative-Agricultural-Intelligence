import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { getReferenceData } from '../services/api'
import StepLayout from '../components/StepLayout'
import { MapPin, Calendar, Trees, Droplets } from 'lucide-react'

export default function FarmDetails() {
  const navigate = useNavigate()
  const { farmData, setFarmData } = useApp()
  const [refData, setRefData] = useState({
    districts: [], seasons: [], soil_types: [],
    water_sources: [], drainage_conditions: [], previous_crops: [],
  })
  const [loading, setLoading] = useState(true)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    getReferenceData()
      .then(setRefData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const update = (field, value) => {
    setFarmData(prev => ({ ...prev, [field]: value }))
    setErrors(prev => ({ ...prev, [field]: null }))
  }

  const validate = () => {
    const errs = {}
    if (!farmData.district) errs.district = 'Please select your district'
    if (!farmData.season)   errs.season   = 'Please select the farming season'
    return errs
  }

  const handleNext = () => {
    const errs = validate()
    if (Object.keys(errs).length > 0) { setErrors(errs); return }
    navigate('/soil-test')
  }

  if (loading) return (
    <StepLayout step={1} title="Farm Details">
      <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 60, paddingBottom: 60 }}>
        <div className="loader" />
      </div>
    </StepLayout>
  )

  return (
    <StepLayout step={1} title="Farm Details" subtitle="Tell us about your farm location and conditions">

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }} className="form-grid">

        {/* State */}
        <Field label="State" icon={<MapPin size={15} />}>
          <select className="farm-input" value={farmData.state} onChange={e => update('state', e.target.value)}>
            <option value="Maharashtra">Maharashtra</option>
          </select>
          <p style={{ fontSize: '0.75rem', color: 'var(--ff-text-muted)', marginTop: 4 }}>
            Currently supporting Maharashtra (pilot)
          </p>
        </Field>

        {/* District */}
        <Field label="District" required icon={<MapPin size={15} />} error={errors.district}>
          <select className="farm-input" value={farmData.district} onChange={e => update('district', e.target.value)}>
            <option value="">Select district...</option>
            {refData.districts.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </Field>

        {/* Village */}
        <Field label="Village / Locality" hint="Optional">
          <input
            className="farm-input"
            placeholder="e.g. Sangamner"
            value={farmData.village}
            onChange={e => update('village', e.target.value)}
          />
        </Field>

        {/* Season */}
        <Field label="Farming Season" required icon={<Calendar size={15} />} error={errors.season}>
          <select className="farm-input" value={farmData.season} onChange={e => update('season', e.target.value)}>
            <option value="">Select season...</option>
            {refData.seasons.map(s => <option key={s.id} value={s.id}>{s.name} — {s.period}</option>)}
          </select>
        </Field>

        {/* Farm area */}
        <Field label="Farm Area" hint="Optional">
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <input
              className="farm-input"
              type="number" min="0" step="0.1"
              placeholder="e.g. 2.5"
              value={farmData.farm_area}
              onChange={e => update('farm_area', e.target.value)}
            />
            <span style={{ fontSize: '0.85rem', color: 'var(--ff-text-secondary)', whiteSpace: 'nowrap', fontWeight: 500 }}>
              acres
            </span>
          </div>
        </Field>

        {/* Soil type */}
        <Field label="Soil Type" hint="Optional" icon={<Trees size={15} />}>
          <select className="farm-input" value={farmData.soil_type} onChange={e => update('soil_type', e.target.value)}>
            <option value="">Select soil type...</option>
            {refData.soil_types.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </Field>

        {/* Irrigation */}
        <Field label="Irrigation Available?" icon={<Droplets size={15} />}>
          <div style={{ display: 'flex', gap: 10, marginTop: 2 }}>
            {[
              { val: 'yes', label: '✓ Yes, I have irrigation' },
              { val: 'no',  label: '✗ Rainfed farm only' },
            ].map(({ val, label }) => (
              <button
                key={val}
                onClick={() => update('irrigation_available', val)}
                style={{
                  flex: 1,
                  padding: '10px 12px',
                  borderRadius: 12,
                  border: farmData.irrigation_available === val
                    ? '2px solid var(--ff-primary)'
                    : '1.5px solid var(--ff-border)',
                  background: farmData.irrigation_available === val ? 'var(--ff-light)' : 'white',
                  color: farmData.irrigation_available === val ? 'var(--ff-primary)' : 'var(--ff-text-secondary)',
                  fontWeight: farmData.irrigation_available === val ? 600 : 400,
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </Field>

        {/* Water source */}
        <Field label="Water Source" hint="Optional">
          <select className="farm-input" value={farmData.water_source} onChange={e => update('water_source', e.target.value)}>
            <option value="">Select water source...</option>
            {refData.water_sources.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
          </select>
        </Field>

        {/* Drainage */}
        <Field label="Field Drainage Condition">
          <select className="farm-input" value={farmData.drainage} onChange={e => update('drainage', e.target.value)}>
            {refData.drainage_conditions.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </Field>

        {/* Previous crop */}
        <Field label="Previous Crop" hint="Optional">
          <select className="farm-input" value={farmData.previous_crop} onChange={e => update('previous_crop', e.target.value)}>
            <option value="">Select previous crop...</option>
            {refData.previous_crops.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </Field>
      </div>

      {/* Navigation buttons */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 32 }}>
        <button className="btn-secondary" onClick={() => navigate('/')}>← Back</button>
        <button className="btn-primary" onClick={handleNext}>
          Next: Soil Test →
        </button>
      </div>

      <style>{`
        @media (max-width: 640px) {
          .form-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </StepLayout>
  )
}

function Field({ label, required, hint, error, icon, children }) {
  return (
    <div>
      <label className="ff-label">
        <span style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 6 }}>
          {icon && <span style={{ color: 'var(--ff-primary)' }}>{icon}</span>}
          {label}
          {required && <span style={{ color: 'var(--ff-error)', marginLeft: 2 }}>*</span>}
          {hint && <span style={{ fontSize: '0.75rem', color: 'var(--ff-text-muted)', fontWeight: 400, marginLeft: 4 }}>({hint})</span>}
        </span>
      </label>
      {children}
      {error && <p style={{ color: 'var(--ff-error)', fontSize: '0.78rem', marginTop: 5 }}>{error}</p>}
    </div>
  )
}
