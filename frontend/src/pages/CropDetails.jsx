import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { checkFeasibility } from '../services/api'
import { ArrowLeft, Sprout, Zap, Shield, CheckCircle, XCircle, AlertCircle, HelpCircle, Printer, FileText, Info } from 'lucide-react'
import SuitabilityMeter from '../components/SuitabilityMeter'

export default function CropDetails() {
  const { cropName } = useParams()
  const navigate = useNavigate()
  const { selectedCrop, analysisResult, farmData, soilData, envData, getApiPayload } = useApp()

  const [loading, setLoading] = useState(false)
  const [fetchedCrop, setFetchedCrop] = useState(null)
  const [fetchError, setFetchError] = useState(null)

  useEffect(() => {
    // If crop is not already in selectedCrop or analysisResult, fetch feasibility dynamically
    const existing = (selectedCrop && selectedCrop.crop === cropName)
      ? selectedCrop
      : analysisResult?.ranked_crops?.find(c => c.crop === cropName)

    if (!existing && cropName) {
      setLoading(true)
      setFetchError(null)
      const payload = getApiPayload()
      const farm_data = {
        state: payload.farm_data?.state || 'Maharashtra',
        district: payload.farm_data?.district || 'Parbhani',
        season: payload.farm_data?.season || 'kharif',
        soil_type: payload.farm_data?.soil_type || 'heavy_black',
        irrigation_available: payload.farm_data?.irrigation_available || 'no',
        drainage: payload.farm_data?.drainage || 'good',
        intent: payload.farm_data?.intent || 'seasonal_field_crop'
      }
      checkFeasibility({
        ...payload,
        farm_data,
        chosen_crop: cropName
      })
        .then(res => {
          if (res.success && res.result) {
            setFetchedCrop(res.result)
          } else {
            setFetchError('Could not load crop suitability details.')
          }
        })
        .catch(err => {
          setFetchError(err.message || 'Failed to load crop details.')
        })
        .finally(() => setLoading(false))
    }
  }, [cropName, selectedCrop, analysisResult])


  const crop = (selectedCrop && selectedCrop.crop === cropName ? selectedCrop : null)
    || analysisResult?.ranked_crops?.find(c => c.crop === cropName)
    || fetchedCrop

  const formattedCropName = crop?.common_name || (cropName ? (cropName.charAt(0).toUpperCase() + cropName.slice(1)) : 'Crop')

  if (loading) {
    return (
      <div className="page-bg" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
        <div className="ff-card" style={{ padding: 40, textAlign: 'center', maxWidth: 400, width: '100%' }}>
          <div className="pulse-icon" style={{ fontSize: 32, marginBottom: 16 }}>🌾</div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--ff-text)', marginBottom: 8 }}>
            Analyzing Crop Suitability for {formattedCropName}...
          </h2>
          <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.85rem' }}>
            Fetching soil compatibility and agricultural benchmarks...
          </p>
        </div>
      </div>
    )
  }

  if (!crop) {
    return (
      <div className="page-bg" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
        <div className="ff-card" style={{ padding: 36, textAlign: 'center', maxWidth: 420, width: '100%' }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>⚠️</div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--ff-text)', marginBottom: 8 }}>
            Crop Information Not Found
          </h2>
          <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.88rem', marginBottom: 20 }}>
            {fetchError || 'Please select a crop from your recommendations list or run a new farm analysis.'}
          </p>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
            <button className="btn-secondary" onClick={() => navigate('/recommendations')}>
              ← Back to Recommendations
            </button>
            <button className="btn-primary" onClick={() => navigate('/farm-details')}>
              Start New Analysis
            </button>
          </div>
        </div>
      </div>
    )
  }

  const supporting = crop.supporting_factors?.filter(f => f.status === 'suitable') || []
  const limiting   = crop.limiting_factors || []
  const moderate   = crop.moderate_factors || []
  const missing    = crop.missing_factors || []

  const score = crop.final_score || 50
  const scoreColor = score >= 90 ? '#138A4B' : score >= 70 ? '#20A65A' : score >= 50 ? '#D89B18' : score >= 30 ? '#E07B3A' : '#D94B4B'
  const scoreLabel = score >= 90 ? 'Highly Suitable' : score >= 70 ? 'Moderately Suitable' : score >= 50 ? 'Needs Attention' : 'Less Suitable'
  const scoreGrad = score >= 90 ? 'score-gradient-high' : score >= 70 ? 'score-gradient-medium' : score >= 50 ? 'score-gradient-amber' : 'score-gradient-low'

  const confColor = crop.data_confidence === 'high' ? 'var(--ff-primary)' : crop.data_confidence === 'medium' ? 'var(--ff-warning)' : 'var(--ff-error)'
  const reportDate = new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
  const district = farmData.district || 'Maharashtra District'
  const season = farmData.season || 'Kharif'

  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="page-bg" style={{ minHeight: '100vh' }}>

      {/* ── Top bar ──────────────────────────────────────────────── */}
      <div className="ff-nav px-6 py-4 flex items-center gap-3 no-print" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
        <button
          onClick={() => navigate('/recommendations')}
          style={{
            background: 'var(--ff-soft)', border: '1px solid var(--ff-border)',
            borderRadius: 10, padding: '6px 10px', cursor: 'pointer',
            display: 'flex', alignItems: 'center',
            color: 'var(--ff-text-secondary)',
          }}
        >
          <ArrowLeft size={18} />
        </button>
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--ff-text)' }}>{crop.common_name} — Detailed Analysis Report</h1>
          {crop.local_name && <p style={{ fontSize: '0.75rem', color: 'var(--ff-text-secondary)' }}>{crop.local_name}</p>}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            className="btn-secondary"
            onClick={handlePrint}
            style={{ padding: '8px 14px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: 6, borderColor: 'var(--ff-primary)', color: 'var(--ff-primary)' }}
          >
            <Printer size={15} /> Print / Export PDF
          </button>
          <button
            className="btn-secondary"
            onClick={() => navigate('/what-if')}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            <Zap size={14} /> What-If
          </button>
          <button
            className="btn-want"
            onClick={() => navigate('/i-want-to-grow')}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            <Sprout size={14} /> I Want to Grow This
          </button>
        </div>
      </div>

      <div className="ff-container-narrow" style={{ paddingTop: 24, paddingBottom: 48 }}>

        {/* ── Official Print Header ────────────────────────────────────── */}
        <div className="print-header print-only">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h1 style={{ fontSize: '18pt', fontWeight: 800, color: '#075C35', margin: 0 }}>FarmFriend AI</h1>
              <p style={{ fontSize: '10pt', fontWeight: 700, color: '#138A4B', margin: '2px 0 0 0' }}>
                Detailed Crop Suitability & Agronomic Advisory Report: {crop.common_name}
              </p>
            </div>
            <div style={{ textAlign: 'right', fontSize: '9pt', color: '#4B5563' }}>
              <div><strong>Date:</strong> {reportDate}</div>
              <div><strong>District:</strong> {district} ({season} season)</div>
            </div>
          </div>
        </div>

        {/* ── Score Hero Card ───────────────────────────────────── */}
        <div className="ff-card animate-fade-in" style={{
          padding: '32px 24px', marginBottom: 20, textAlign: 'center',
          borderTop: `4px solid ${scoreColor}`,
          background: 'linear-gradient(135deg, #FAFDF9, #FFFFFF)',
        }}>
          <SuitabilityMeter score={score} size="lg" showLabel={false} />

          <div style={{ fontSize: '2.8rem', fontWeight: 900, color: scoreColor, lineHeight: 1, marginTop: 14 }}>
            {Math.round(score)}
            <span style={{ fontSize: '1.2rem', color: 'var(--ff-text-muted)', fontWeight: 400 }}>/100</span>
          </div>

          <div style={{
            display: 'inline-block',
            background: `${scoreColor}18`,
            color: scoreColor, fontWeight: 700, fontSize: '0.95rem',
            padding: '6px 20px', borderRadius: 999,
            border: `1px solid ${scoreColor}30`,
            marginTop: 8, marginBottom: 16,
          }}>
            {scoreLabel}
          </div>

          {/* Score bar */}
          <div className="score-bar" style={{ maxWidth: 320, margin: '0 auto 16px' }}>
            <div className={`score-bar-fill ${scoreGrad}`} style={{ width: `${score}%` }} />
          </div>

          {/* Score composition */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: 24, fontSize: '0.78rem', color: 'var(--ff-text-secondary)' }}>
            <div>
              ML Model Score:{' '}
              <span style={{ color: 'var(--ff-info)', fontWeight: 700 }}>{crop.ml_score || Math.round(crop.ml_probability * 100 || score)}/100</span>{' '}
              <span style={{ color: 'var(--ff-text-muted)' }}>(50%)</span>
            </div>
            <div style={{ color: 'var(--ff-border)' }}>|</div>
            <div>
              Rule Engine Score:{' '}
              <span style={{ color: '#7C3AED', fontWeight: 700 }}>{crop.rule_score || score}/100</span>{' '}
              <span style={{ color: 'var(--ff-text-muted)' }}>(50%)</span>
            </div>
          </div>
          <div style={{ marginTop: 8, fontSize: '0.75rem', fontWeight: 600, color: confColor }}>
            Data Confidence: {(crop.data_confidence || 'Medium').toUpperCase()}
          </div>
        </div>

        {/* ── COMPREHENSIVE PARAMETER COMPARISON MATRIX TABLE ──────── */}
        <div className="ff-card" style={{ padding: 20, marginBottom: 20 }}>
          <h3 style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--ff-primary)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
            <FileText size={16} /> Detailed Soil Test vs. Crop Requirement Parameter Audit
          </h3>

          <table className="report-table">
            <thead>
              <tr>
                <th>Parameter / Nutrient</th>
                <th>Your Soil Test Value</th>
                <th>Evaluation / Status</th>
                <th>Agronomic Note & Corrective Action</th>
              </tr>
            </thead>
            <tbody>
              {renderParameterRow("pH (Soil Reaction)", soilData.ph ? `${soilData.ph} scale` : "Not provided", getFactorStatus(crop, "pH"))}
              {renderParameterRow("Nitrogen (N)", soilData.N ? `${soilData.N} kg/ha` : "Not provided", getFactorStatus(crop, "N"))}
              {renderParameterRow("Phosphorus (P)", soilData.P ? `${soilData.P} kg/ha` : "Not provided", getFactorStatus(crop, "P"))}
              {renderParameterRow("Potassium (K)", soilData.K ? `${soilData.K} kg/ha` : "Not provided", getFactorStatus(crop, "K"))}
              {renderParameterRow("Sulphur (S)", soilData.S ? `${soilData.S} ppm` : "Not provided", getFactorStatus(crop, "S"))}
              {renderParameterRow("Zinc (Zn)", soilData.Zn ? `${soilData.Zn} ppm` : "Not provided", getFactorStatus(crop, "Zn"))}
              {renderParameterRow("Iron (Fe)", soilData.Fe ? `${soilData.Fe} ppm` : "Not provided", getFactorStatus(crop, "Fe"))}
              {renderParameterRow("Boron (B)", soilData.B ? `${soilData.B} ppm` : "Not provided", getFactorStatus(crop, "B"))}
              {renderParameterRow("Seasonal Temperature", envData.temperature ? `${envData.temperature}°C` : "Not provided", getFactorStatus(crop, "Temperature"))}
              {renderParameterRow("Seasonal Rainfall", envData.rainfall ? `${envData.rainfall} mm` : "Not provided", getFactorStatus(crop, "Rainfall"))}
            </tbody>
          </table>
        </div>

        {/* ── Factor cards ─────────────────────────────────────── */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14, marginBottom: 20 }} className="factors-grid">
          {supporting.length > 0 && (
            <FactorSection
              title="Favourable Conditions"
              icon={<CheckCircle size={16} />}
              color="var(--ff-primary)"
              bg="var(--ff-success-bg)"
              border="rgba(19,138,75,0.25)"
              factors={supporting}
              factorIcon="✓"
            />
          )}
          {limiting.length > 0 && (
            <FactorSection
              title="Limiting Conditions"
              icon={<XCircle size={16} />}
              color="var(--ff-error)"
              bg="var(--ff-error-bg)"
              border="rgba(217,75,75,0.25)"
              factors={limiting}
              factorIcon="✗"
            />
          )}
          {moderate.length > 0 && (
            <FactorSection
              title="Needs Attention"
              icon={<AlertCircle size={16} />}
              color="var(--ff-warning)"
              bg="var(--ff-warning-bg)"
              border="rgba(216,155,24,0.25)"
              factors={moderate}
              factorIcon="⚠"
            />
          )}
          {missing.length > 0 && (
            <FactorSection
              title="Missing Information"
              icon={<HelpCircle size={16} />}
              color="var(--ff-text-muted)"
              bg="#F1F4F2"
              border="var(--ff-border)"
              factors={missing}
              factorIcon="?"
            />
          )}
        </div>

        {/* ── Actionable Remediation Advisory ───────────────────── */}
        <div className="ff-card" style={{ padding: 20, marginBottom: 20, background: 'linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)', border: '1px solid #FCD34D' }}>
          <h3 style={{ fontWeight: 700, fontSize: '0.95rem', color: '#92400E', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <Info size={16} /> Krishi Extension Advisory & Soil Remediation Action Plan
          </h3>
          <p style={{ fontSize: '0.82rem', color: '#78350F', lineHeight: 1.6 }}>
            {getDetailedAgronomicAdvisory(crop)}
          </p>
        </div>

        {/* ── Disclaimer ────────────────────────────────────────── */}
        <div style={{
          background: '#F6F8F7',
          border: '1px solid var(--ff-border)',
          borderRadius: 14, padding: '14px 16px',
          display: 'flex', alignItems: 'flex-start', gap: 10,
        }}>
          <Shield size={15} style={{ color: 'var(--ff-text-muted)', flexShrink: 0, marginTop: 2 }} />
          <p style={{ fontSize: '0.78rem', color: 'var(--ff-text-muted)', lineHeight: 1.6 }}>
            {crop.disclaimer || 'Suitability estimates are computed from supplied data using ML + agricultural rules.'}
          </p>
        </div>
      </div>

      <style>{`
        @media (max-width: 640px) { .factors-grid { grid-template-columns: 1fr !important; } }
      `}</style>
    </div>
  )
}

function renderParameterRow(label, userValue, factorObj) {
  const status = factorObj?.status || 'suitable'
  const note = factorObj?.note || 'Within reference range for crop growth'
  
  const statusColor = status === 'suitable' ? '#138A4B' : status === 'limiting' ? '#D94B4B' : status === 'moderate' ? '#D89B18' : '#9CA3AF'
  const statusBadge = status === 'suitable' ? '✓ Adequate' : status === 'limiting' ? '✗ Deficient / Limiting' : status === 'moderate' ? '⚠ Moderate' : '? Unknown'

  return (
    <tr>
      <td style={{ fontWeight: 600 }}>{label}</td>
      <td>{userValue}</td>
      <td>
        <span style={{ color: statusColor, fontWeight: 700, fontSize: '8pt' }}>
          {statusBadge}
        </span>
      </td>
      <td style={{ color: '#4B5563' }}>{note}</td>
    </tr>
  )
}

function getFactorStatus(crop, key) {
  if (!crop) return null
  const all = [...(crop.supporting_factors || []), ...(crop.limiting_factors || []), ...(crop.moderate_factors || [])]
  return all.find(f => f && f.factor && (f.factor.toLowerCase() === key.toLowerCase() || f.factor.toLowerCase().includes(key.toLowerCase())))
}

function FactorSection({ title, icon, color, bg, border, factors, factorIcon }) {
  return (
    <div style={{
      background: bg, borderRadius: 16,
      border: `1px solid ${border}`, padding: 18,
    }}>
      <h3 style={{
        fontWeight: 700, fontSize: '0.85rem',
        color, display: 'flex', alignItems: 'center', gap: 7, marginBottom: 12,
      }}>
        <span>{icon}</span> {title}
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {factors.map((f, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color, flexShrink: 0, marginTop: 2 }}>{factorIcon}</span>
            <div>
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--ff-text)' }}>{f.factor}</span>
              {f.note && <p style={{ fontSize: '0.75rem', color: 'var(--ff-text-secondary)', marginTop: 2, lineHeight: 1.4 }}>{f.note}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function getDetailedAgronomicAdvisory(crop) {
  const limiting = crop.limiting_factors?.map(f => f.factor) || []
  let advice = []

  if (limiting.includes('Zn')) advice.push('Apply Zinc Sulfate (ZnSO₄) @ 25 kg/ha basal or foliar application of 0.5% ZnSO₄.')
  if (limiting.includes('B')) advice.push('Apply Borax @ 10 kg/ha soil application or foliar spray of Solubor (0.2%) during peak vegetative phase.')
  if (limiting.includes('Rainfall') || limiting.includes('water')) advice.push('Integrate micro-irrigation (drip / sprinkler) to meet critical moisture requirements during flowering and pod development.')
  if (limiting.includes('pH')) advice.push('Apply agricultural lime (acidic soils) or gypsum (alkaline soils) to optimize soil pH.')
  if (limiting.includes('N') || limiting.includes('P') || limiting.includes('K')) advice.push('Follow site-specific nutrient management (SSNM) recommendations from your local Krishi Vigyan Kendra (KVK).')

  if (advice.length === 0) {
    return `Soil health parameters for ${crop.common_name} are optimal. Follow standard agricultural practices (PoP) recommended by state agricultural universities.`
  }

  return advice.join(' ')
}
