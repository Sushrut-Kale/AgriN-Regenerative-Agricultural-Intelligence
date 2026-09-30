import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { getReferenceData, getLiveWeather } from '../services/api'
import StepLayout from '../components/StepLayout'
import { MapPin, Calendar, Trees, Droplets, Navigation, CheckCircle, AlertCircle, Sparkles } from 'lucide-react'
import { DEMO_SCENARIOS } from '../services/demoScenarios'

export default function FarmDetails() {
  const navigate = useNavigate()
  const { farmData, setFarmData, setSoilData, setEnvData } = useApp()
  const [refData, setRefData] = useState({
    states: [], districts: [], seasons: [], soil_types: [],
    water_sources: [], drainage_conditions: [], previous_crops: [],
  })
  const [loading, setLoading] = useState(true)
  const [districtsLoading, setDistrictsLoading] = useState(false)
  const [geoLocating, setGeoLocating] = useState(false)
  const [geoMessage, setGeoMessage] = useState(null)
  const [errors, setErrors] = useState({})

  // Initial load
  useEffect(() => {
    const currentState = farmData.state || 'Maharashtra'
    getReferenceData(currentState)
      .then(data => {
        setRefData(data)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  // When state changes, fetch updated districts for that state
  const handleStateChange = async (newState) => {
    update('state', newState)
    update('district', '')
    update('sub_district', '')
    setDistrictsLoading(true)
    try {
      const data = await getReferenceData(newState)
      setRefData(prev => ({
        ...prev,
        districts: data.districts || [],
        selected_state: newState
      }))
    } catch (e) {
      console.error('Failed to load districts for state:', e)
    } finally {
      setDistrictsLoading(false)
    }
  }

  const update = (field, value) => {
    setFarmData(prev => ({ ...prev, [field]: value }))
    setErrors(prev => ({ ...prev, [field]: null }))
  }

  // 📍 GPS Geolocation Handler
  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setGeoMessage({ type: 'error', text: 'Geolocation is not supported by your browser.' })
      return
    }

    setGeoLocating(true)
    setGeoMessage(null)

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords
        try {
          // Query weather/location resolver with coordinates
          const locInfo = await getLiveWeather({ lat: latitude, lon: longitude })
          const detectedDistrict = locInfo.district
          const detectedState = locInfo.state || farmData.state || 'Maharashtra'

          // Load districts for detected state
          const stateData = await getReferenceData(detectedState)
          setRefData(prev => ({
            ...prev,
            districts: stateData.districts || [],
            selected_state: detectedState
          }))

          setFarmData(prev => ({
            ...prev,
            latitude: Number(latitude.toFixed(4)),
            longitude: Number(longitude.toFixed(4)),
            state: detectedState,
            district: detectedDistrict,
            agro_climatic_zone: locInfo.region || ''
          }))

          setGeoMessage({
            type: 'success',
            text: `📍 GPS Detected: ${detectedDistrict}, ${detectedState} (${latitude.toFixed(2)}°N, ${longitude.toFixed(2)}°E)`
          })
        } catch (err) {
          setFarmData(prev => ({
            ...prev,
            latitude: Number(latitude.toFixed(4)),
            longitude: Number(longitude.toFixed(4)),
          }))
          setGeoMessage({
            type: 'success',
            text: `📍 GPS Captured: ${latitude.toFixed(4)}°N, ${longitude.toFixed(4)}°E`
          })
        } finally {
          setGeoLocating(false)
        }
      },
      (err) => {
        setGeoLocating(false)
        setGeoMessage({ type: 'error', text: `Unable to retrieve GPS: ${err.message}` })
      },
      { timeout: 8000 }
    )
  }

  const handleSelectDemoScenario = (scId) => {
    if (!scId) return
    const sc = DEMO_SCENARIOS.find(s => s.id === scId)
    if (!sc) return
    setFarmData(sc.farmData)
    setSoilData(sc.soilData)
    setEnvData(sc.envData)
  }

  const validate = () => {
    const errs = {}
    if (!farmData.state)    errs.state    = 'Please select your state'
    if (!farmData.district && !farmData.latitude) errs.district = 'Please select your district or use GPS'
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

  const statesList = refData.states && refData.states.length > 0
    ? refData.states
    : [{ name: 'Maharashtra', type: 'State' }]

  const isDemo = Boolean(farmData?.farm_id?.startsWith('DEMO-'))

  return (
    <StepLayout step={1} title="Farm Details" subtitle="Tell us about your farm location and conditions across India">

      {/* Demo Scenario Selector (Phase 19) */}
      <div style={{
        background: isDemo ? '#FEF3C7' : '#F9FAFB',
        border: isDemo ? '2px dashed #D97706' : '1px solid #E5E7EB',
        borderRadius: 14,
        padding: '12px 18px',
        marginBottom: 18,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 12
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Sparkles size={18} className="text-amber-600" />
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.85rem', color: isDemo ? '#92400E' : '#374151' }}>
              {isDemo ? '⚠️ DEMO DATA — NOT REAL FARM DATA' : 'Demonstration Scenarios (Phase 19)'}
            </div>
            <div style={{ fontSize: '0.72rem', color: isDemo ? '#B45309' : '#6B7280' }}>
              Pre-fill form with regional archetypes (Punjab, Rajasthan, Kerala, Maharashtra, Incomplete Data).
            </div>
          </div>
        </div>

        <select
          onChange={(e) => handleSelectDemoScenario(e.target.value)}
          style={{
            fontSize: '0.8rem', padding: '6px 12px', borderRadius: 8,
            border: '1px solid #D1D5DB', background: '#FFFFFF'
          }}
        >
          <option value="">Select a Demo Scenario...</option>
          {DEMO_SCENARIOS.map(sc => (
            <option key={sc.id} value={sc.id}>{sc.title}</option>
          ))}
        </select>
      </div>

      {/* GPS Location Bar */}
      <div style={{
        background: 'var(--ff-surface-alt, #f0fdf4)',
        border: '1.5px solid var(--ff-primary-light, #bbf7d0)',
        borderRadius: 14,
        padding: '14px 18px',
        marginBottom: 24,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 12
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 20 }}>📍</span>
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--ff-text, #166534)' }}>
              Pan-India Location-Aware Intelligence
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--ff-text-secondary, #4b5563)' }}>
              Automatically detect district and climate via GPS, or select from all Indian States & Union Territories.
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={handleUseMyLocation}
          disabled={geoLocating}
          className="btn-secondary"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '8px 16px',
            fontSize: '0.82rem',
            fontWeight: 600,
            borderRadius: 10,
            cursor: geoLocating ? 'wait' : 'pointer'
          }}
        >
          <Navigation size={14} className={geoLocating ? 'spin' : ''} />
          {geoLocating ? 'Locating...' : '📍 Use My Location (GPS)'}
        </button>
      </div>

      {/* GPS Message */}
      {geoMessage && (
        <div style={{
          padding: '10px 14px',
          borderRadius: 10,
          marginBottom: 20,
          fontSize: '0.82rem',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          background: geoMessage.type === 'success' ? '#f0fdf4' : '#fef2f2',
          color: geoMessage.type === 'success' ? '#15803d' : '#b91c1c',
          border: `1px solid ${geoMessage.type === 'success' ? '#86efac' : '#fca5a5'}`
        }}>
          {geoMessage.type === 'success' ? <CheckCircle size={15} /> : <AlertCircle size={15} />}
          {geoMessage.text}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }} className="form-grid">

        {/* State */}
        <Field label="State / Union Territory" required icon={<MapPin size={15} />} error={errors.state}>
          <select
            className="farm-input"
            value={farmData.state || 'Maharashtra'}
            onChange={e => handleStateChange(e.target.value)}
          >
            {statesList.map(s => (
              <option key={s.name} value={s.name}>
                {s.name} {s.type === 'Union Territory' ? '(UT)' : ''}
              </option>
            ))}
          </select>
          <p style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', marginTop: 4 }}>
            Supporting all 28 States & 8 Union Territories
          </p>
        </Field>

        {/* District */}
        <Field label="District" required icon={<MapPin size={15} />} error={errors.district}>
          <select
            className="farm-input"
            value={farmData.district || ''}
            onChange={e => update('district', e.target.value)}
            disabled={districtsLoading}
          >
            <option value="">{districtsLoading ? 'Loading districts...' : 'Select district...'}</option>
            {refData.districts && refData.districts.map(d => (
              <option key={d.id} value={d.id || d.name}>{d.name}</option>
            ))}
          </select>
        </Field>

        {/* Sub-District / Taluka / Tehsil / Block */}
        <Field label="Taluka / Tehsil / Block" hint="Sub-District">
          <input
            className="farm-input"
            placeholder="e.g. Haveli, Sangamner, Abohar, Pollachi"
            value={farmData.sub_district || ''}
            onChange={e => update('sub_district', e.target.value)}
          />
        </Field>

        {/* Village */}
        <Field label="Village / Locality" hint="Optional">
          <input
            className="farm-input"
            placeholder="e.g. Nimgaon, Rampur"
            value={farmData.village || ''}
            onChange={e => update('village', e.target.value)}
          />
        </Field>

        {/* Season */}
        <Field label="Farming Season" required icon={<Calendar size={15} />} error={errors.season}>
          <select className="farm-input" value={farmData.season || ''} onChange={e => update('season', e.target.value)}>
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
              value={farmData.farm_area || ''}
              onChange={e => update('farm_area', e.target.value)}
            />
            <span style={{ fontSize: '0.85rem', color: 'var(--ff-text-secondary)', whiteSpace: 'nowrap', fontWeight: 500 }}>
              acres
            </span>
          </div>
        </Field>

        {/* Soil type */}
        <Field label="Soil Type" hint="Optional" icon={<Trees size={15} />}>
          <select className="farm-input" value={farmData.soil_type || ''} onChange={e => update('soil_type', e.target.value)}>
            <option value="">Select soil type...</option>
            {refData.soil_types.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </Field>

        {/* Irrigation */}
        <Field label="Irrigation Available?" icon={<Droplets size={15} />}>
          <div style={{ display: 'flex', gap: 10, marginTop: 2 }}>
            {[
              { val: 'yes', label: '✓ Yes, irrigated' },
              { val: 'no',  label: '✗ Rainfed farm only' },
            ].map(({ val, label }) => (
              <button
                key={val}
                type="button"
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
          <select className="farm-input" value={farmData.water_source || ''} onChange={e => update('water_source', e.target.value)}>
            <option value="">Select water source...</option>
            {refData.water_sources.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
          </select>
        </Field>

        {/* Drainage */}
        <Field label="Field Drainage Condition">
          <select className="farm-input" value={farmData.drainage || 'unknown'} onChange={e => update('drainage', e.target.value)}>
            {refData.drainage_conditions.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </Field>

        {/* Previous crop */}
        <Field label="Previous Crop" hint="Optional">
          <select className="farm-input" value={farmData.previous_crop || ''} onChange={e => update('previous_crop', e.target.value)}>
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
