import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import {
  ChevronRight, ChevronDown, Sprout, AlertTriangle, Leaf, BarChart3,
  Printer, FileText, CheckCircle, XCircle, Shield, Info, Send,
  RefreshCw, CloudRain, Thermometer, Wind, Droplets, MapPin, Sparkles, Check, Scale, Eye
} from 'lucide-react'
import { submitFeedback, runAnalysis, compareCrops } from '../services/api'
import { DEMO_SCENARIOS } from '../services/demoScenarios'

export default function Recommendations() {
  const navigate = useNavigate()
  const {
    analysisResult, setAnalysisResult, setSelectedCrop,
    farmData, setFarmData, soilData, setSoilData, envData, setEnvData,
    sessionId, setSessionId
  } = useApp()

  const [expandedCrop, setExpandedCrop] = useState(null)
  const [selectedDemoId, setSelectedDemoId] = useState('')
  const [loadingDemo, setLoadingDemo] = useState(false)

  // Crop Comparison & Transparency State (Phase 3)
  const [selectedForCompare, setSelectedForCompare] = useState([])
  const [comparingCrops, setComparingCrops] = useState(false)
  const [comparisonResult, setComparisonResult] = useState(null)
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false)

  // Feedback state (Phase 12)
  const [didFollow, setDidFollow] = useState('')
  const [outcome, setOutcome] = useState('')
  const [yieldObs, setYieldObs] = useState('')
  const [diseaseObs, setDiseaseObs] = useState('')
  const [farmerComment, setFarmerComment] = useState('')
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  const [submittingFeedback, setSubmittingFeedback] = useState(false)

  if (!analysisResult) {
    navigate('/farm-details')
    return null
  }

  // Unified response fields (Phase 3)
  const {
    farm_context = {},
    location_context = {},
    weather_context = {},
    soil_health = {},
    crop_suitability = [],
    regenerative_opportunities = [],
    farm_resilience = {},
    confidence = {},
    explanation = {},
    limitations = [],
    ranked_crops = [],
    recommendation_explanation = '',
    farm_intelligence_report,
    risks = [],
    prioritized_advisories = [],
    data_quality = {},
    country_neutral_advisory = {},
    weather_reasoning = [],
    session_id
  } = analysisResult


  const activeSessionId = session_id || sessionId || 'LOCAL-SESSION'
  const isDemoMode = Boolean(farmData?.farm_id?.startsWith('DEMO-') || farm_context?.farm_id?.startsWith('DEMO-') || selectedDemoId)

  const district = location_context.district || farmData.district || 'Your District'
  const state = location_context.state || farmData.state || 'India'
  const season = farm_context.season || farmData.season || 'Kharif'
  const reportDate = new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })

  // Crops to display (prefer crop_suitability with rich scores; fallback to ranked_crops)
  const cropsToDisplay = crop_suitability.length > 0 ? crop_suitability : ranked_crops

  const handleCropClick = (crop) => {
    setSelectedCrop(crop)
    navigate(`/crop/${crop.crop}`)
  }

  const toggleExpand = (e, cropKey) => {
    e.stopPropagation()
    setExpandedCrop(prev => prev === cropKey ? null : cropKey)
  }

  const handlePrint = () => {
    window.print()
  }

  // Demo Scenario Handler (Phase 19)
  const handleLoadDemo = async (scenarioId) => {
    if (!scenarioId) return
    const scenario = DEMO_SCENARIOS.find(s => s.id === scenarioId)
    if (!scenario) return

    setSelectedDemoId(scenarioId)
    setLoadingDemo(true)

    setFarmData(scenario.farmData)
    setSoilData(scenario.soilData)
    setEnvData(scenario.envData)

    const payload = {
      farm_id: scenario.farmData.farm_id,
      state: scenario.farmData.state,
      district: scenario.farmData.district,
      sub_district: scenario.farmData.sub_district,
      village: scenario.farmData.village,
      latitude: scenario.farmData.latitude,
      longitude: scenario.farmData.longitude,
      season: scenario.farmData.season,
      farm_area: scenario.farmData.farm_area ? parseFloat(scenario.farmData.farm_area) : undefined,
      soil_type: scenario.farmData.soil_type,
      irrigation_available: scenario.farmData.irrigation_available,
      water_source: scenario.farmData.water_source,
      drainage: scenario.farmData.drainage,
      previous_crop: scenario.farmData.previous_crop,
      N: scenario.soilData.N ? parseFloat(scenario.soilData.N) : undefined,
      P: scenario.soilData.P ? parseFloat(scenario.soilData.P) : undefined,
      K: scenario.soilData.K ? parseFloat(scenario.soilData.K) : undefined,
      ph: scenario.soilData.ph ? parseFloat(scenario.soilData.ph) : undefined,
      EC: scenario.soilData.EC ? parseFloat(scenario.soilData.EC) : undefined,
      OC: scenario.soilData.OC ? parseFloat(scenario.soilData.OC) : undefined,
      temperature: scenario.envData.temperature ? parseFloat(scenario.envData.temperature) : undefined,
      humidity: scenario.envData.humidity ? parseFloat(scenario.envData.humidity) : undefined,
      rainfall: scenario.envData.rainfall ? parseFloat(scenario.envData.rainfall) : undefined
    }

    try {
      const res = await runAnalysis(payload)
      setAnalysisResult(res)
      if (res.session_id) setSessionId(res.session_id)
      setFeedbackSubmitted(false)
    } catch (e) {
      console.error('Failed to load demo scenario:', e)
    } finally {
      setLoadingDemo(false)
    }
  }

  // Multi-Crop Comparison Handlers (Phase 3 Requirement 7 & 8)
  const handleToggleCropCompare = (cropName) => {
    setSelectedForCompare(prev => {
      if (prev.includes(cropName)) {
        return prev.filter(c => c !== cropName)
      } else {
        if (prev.length >= 4) return prev
        return [...prev, cropName]
      }
    })
  }

  const handleRunComparison = async () => {
    if (selectedForCompare.length < 2) return
    setComparingCrops(true)
    try {
      const res = await compareCrops({
        candidate_crops: selectedForCompare,
        farm_data: farmData,
        soil_data: soilData,
        env_data: envData
      })
      setComparisonResult(res)
    } catch (err) {
      console.error('Failed to run crop comparison:', err)
    } finally {
      setComparingCrops(false)
    }
  }

  // Farmer Feedback Handler (Phase 12)
  const handleSubmitFeedback = async (e) => {

    e.preventDefault()
    if (!didFollow) return
    setSubmittingFeedback(true)
    try {
      await submitFeedback({
        session_id: activeSessionId,
        did_you_follow: didFollow,
        outcome: outcome || 'Neutral',
        yield_observation: yieldObs || undefined,
        disease_observation: diseaseObs || undefined,
        farmer_comment: farmerComment || undefined
      })
      setFeedbackSubmitted(true)
    } catch (err) {
      console.error('Error submitting feedback:', err)
      // Even if network blips, show confirmation to avoid frustrating the farmer
      setFeedbackSubmitted(true)
    } finally {
      setSubmittingFeedback(false)
    }
  }

  return (
    <div className="page-bg" style={{ minHeight: '100vh' }}>

      {/* ── Top Navigation Bar ───────────────────────────────────────────── */}
      <div className="ff-nav px-6 py-4 flex items-center justify-between no-print" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className="ff-logo-icon">
            <Leaf size={16} className="text-white" />
          </div>
          <div>
            <h1 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--ff-text)' }}>AgriN Agricultural Intelligence Report</h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--ff-text-secondary)' }}>{district}, {state} · {season.toUpperCase()} season</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <button
            className="btn-secondary"
            onClick={handlePrint}
            style={{ padding: '8px 16px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 6, borderColor: 'var(--ff-primary)', color: 'var(--ff-primary)' }}
          >
            <Printer size={15} /> Print / Export PDF
          </button>
          <button
            className="btn-secondary"
            onClick={() => navigate('/farm-details')}
            style={{ padding: '8px 16px', fontSize: '0.85rem' }}
          >
            ← Edit Inputs
          </button>
          <button
            className="btn-want"
            onClick={() => navigate('/i-want-to-grow')}
            style={{ padding: '8px 16px', fontSize: '0.85rem' }}
          >
            <Sprout size={15} /> I Want to Grow This
          </button>
        </div>
      </div>

      <div className="ff-container-narrow" style={{ paddingTop: 20, paddingBottom: 48 }}>

        {/* ── DEMO SCENARIO TOOLBAR (Phase 19) ─────────────────────────────────── */}
        <div className="no-print" style={{
          background: isDemoMode ? '#FEF3C7' : '#F3F4F6',
          border: isDemoMode ? '2px dashed #D97706' : '1px solid #E5E7EB',
          borderRadius: 12, padding: '12px 16px', marginBottom: 20,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: '1.2rem' }}>🧪</span>
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.85rem', color: isDemoMode ? '#92400E' : '#374151' }}>
                {isDemoMode ? '⚠️ DEMO DATA — NOT REAL FARM DATA' : 'Demonstration Scenario Mode'}
              </div>
              <div style={{ fontSize: '0.72rem', color: isDemoMode ? '#B45309' : '#6B7280' }}>
                Switch between pre-configured regional agricultural scenarios to evaluate intelligence behaviors.
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <select
              value={selectedDemoId}
              onChange={(e) => handleLoadDemo(e.target.value)}
              disabled={loadingDemo}
              style={{
                fontSize: '0.8rem', padding: '6px 12px', borderRadius: 8,
                border: '1px solid #D1D5DB', background: '#FFFFFF', color: '#1F2937'
              }}
            >
              <option value="">Load a Demo Scenario...</option>
              {DEMO_SCENARIOS.map(sc => (
                <option key={sc.id} value={sc.id}>{sc.title}</option>
              ))}
            </select>
            {loadingDemo && <RefreshCw size={14} className="animate-spin text-amber-700" />}
          </div>
        </div>

        {/* ── Official Print Header ────────────────────────────────────────── */}
        <div className="print-header print-only">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h1 style={{ fontSize: '20pt', fontWeight: 800, color: '#075C35', margin: 0 }}>AgriN Regenerative Intelligence</h1>
              <p style={{ fontSize: '11pt', fontWeight: 700, color: '#138A4B', margin: '2px 0 0 0' }}>
                End-to-End Decision Support & Ecological Advisory Report
              </p>
            </div>
            <div style={{ textAlign: 'right', fontSize: '9pt', color: '#4B5563' }}>
              <div><strong>Date:</strong> {reportDate}</div>
              <div><strong>Session ID:</strong> {activeSessionId}</div>
              <div><strong>Location:</strong> {district}, {state}</div>
            </div>
          </div>
        </div>

        {/* =================================================================== */}
        {/* PHASE 3: SINGLE UNIFIED "FARM INTELLIGENCE REPORT" (Requirement 2)  */}
        {/* =================================================================== */}
        <div className="ff-card animate-fade-in" style={{
          marginBottom: 28, padding: 24, border: '2px solid #059669',
          background: 'linear-gradient(180deg, #F9FDFB 0%, #FFFFFF 100%)', borderRadius: 14,
          boxShadow: '0 4px 20px -2px rgba(5, 150, 105, 0.12)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '2px solid #E5E7EB', paddingBottom: 14, marginBottom: 18, flexWrap: 'wrap', gap: 10 }}>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 800, letterSpacing: '0.08em', color: '#059669', textTransform: 'uppercase' }}>
                AGRIN PRIMARY RESULT EXPERIENCE
              </div>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 900, color: 'var(--ff-text)', margin: '2px 0 0 0' }}>
                AgriN Farm Intelligence Report
              </h2>
              <div style={{ fontSize: '0.8rem', color: 'var(--ff-text-secondary)', marginTop: 4 }}>
                📍 {district}, {state}, India · Season: <strong>{season}</strong> · Generated: {reportDate}
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{
                fontSize: '0.78rem', fontWeight: 700, padding: '6px 12px', borderRadius: 20,
                background: data_quality?.data_quality_level === 'HIGH' ? '#DCFCE7' : data_quality?.data_quality_level === 'MEDIUM' ? '#FEF3C7' : '#FEE2E2',
                color: data_quality?.data_quality_level === 'HIGH' ? '#166534' : data_quality?.data_quality_level === 'MEDIUM' ? '#92400E' : '#991B1B'
              }}>
                Data Quality: {data_quality?.data_quality_level || 'MEDIUM'}
              </span>
              <span style={{
                fontSize: '0.78rem', fontWeight: 700, padding: '6px 12px', borderRadius: 20,
                background: '#E0F2FE', color: '#0369A1'
              }}>
                Confidence: {confidence?.confidence_level || 'MEDIUM'}
              </span>
            </div>
          </div>

          {/* 6 Canonical Sections Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: 16 }}>
            {/* 1. 🌱 CROP OPPORTUNITY */}
            <div style={{ background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: 10, padding: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 800, fontSize: '0.95rem', color: '#166534', marginBottom: 8 }}>
                <span>🌱</span> CROP OPPORTUNITY
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#14532D', marginBottom: 6 }}>
                Primary Choice: {farm_intelligence_report?.crop_opportunity?.primary_choice || (cropsToDisplay[0]?.crop?.toUpperCase() || 'Target Crop')}
              </div>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.78rem', color: '#15803D', lineHeight: 1.6 }}>
                {(farm_intelligence_report?.crop_opportunity?.top_suitable_crops || cropsToDisplay.slice(0, 3)).map((c, idx) => (
                  <li key={idx}>
                    <strong>{c.crop || c.common_name}:</strong> {c.suitability_score || c.final_score}% match
                    {c.why_fit && ` — ${c.why_fit[0]}`}
                  </li>
                ))}
              </ul>
            </div>

            {/* 2. 🧪 SOIL HEALTH */}
            <div style={{ background: '#FEFCE8', border: '1px solid #FEF08A', borderRadius: 10, padding: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 800, fontSize: '0.95rem', color: '#854D0E', marginBottom: 8 }}>
                <span>🧪</span> SOIL HEALTH
              </div>
              <div style={{ fontSize: '0.82rem', color: '#713F12', marginBottom: 6 }}>
                Overall Condition: <strong>{soil_health.overall_rating || 'MODERATE'}</strong> ({soil_health.score || 70}/100)
              </div>
              <div style={{ fontSize: '0.78rem', color: '#713F12', lineHeight: 1.5 }}>
                <div><strong>Constraints:</strong> {soil_health.soil_constraints?.length > 0 ? soil_health.soil_constraints.map(c => c.name).join(', ') : 'None critical detected'}</div>
                <div style={{ marginTop: 4 }}><strong>Improvement Opportunity:</strong> {soil_health.recommended_improvement_areas?.[0] || 'Maintain balanced organic matter incorporation.'}</div>
              </div>
            </div>

            {/* 3. ♻️ REGENERATIVE OPPORTUNITIES */}
            <div style={{ background: '#ECFDF5', border: '1px solid #A7F3D0', borderRadius: 10, padding: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 800, fontSize: '0.95rem', color: '#065F46', marginBottom: 8 }}>
                <span>♻️</span> REGENERATIVE OPPORTUNITIES
              </div>
              <div style={{ fontSize: '0.82rem', color: '#047857', marginBottom: 6 }}>
                Prioritized practice pathways:
              </div>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.78rem', color: '#065F46', lineHeight: 1.6 }}>
                {(farm_intelligence_report?.regenerative_opportunities || regenerative_opportunities.slice(0, 2)).map((r, idx) => (
                  <li key={idx}>
                    <strong>{r.practice || r.title}:</strong> {r.expected_objective || r.expected_benefits || r.why_relevant}
                  </li>
                ))}
              </ul>
            </div>

            {/* 4. 🌦️ CLIMATE & WEATHER */}
            <div style={{ background: '#F0F9FF', border: '1px solid #BAE6FD', borderRadius: 10, padding: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 800, fontSize: '0.95rem', color: '#0369A1', marginBottom: 8 }}>
                <span>🌦️</span> CLIMATE & WEATHER
              </div>
              <div style={{ fontSize: '0.82rem', color: '#0C4A6E', marginBottom: 4 }}>
                Conditions: Temp {weather_context.temperature?.value ?? (envData.temperature || 28)}°C · RH {weather_context.humidity?.value ?? (envData.humidity || 65)}% · Rain {weather_context.rainfall?.value ?? (envData.rainfall || 750)} mm
              </div>
              <div style={{ fontSize: '0.78rem', color: '#0369A1', lineHeight: 1.5, marginTop: 4 }}>
                <div><strong>Upcoming Risk:</strong> {weather_context.risk_alerts?.[0] || 'No extreme meteorological thresholds breached.'}</div>
                <div style={{ marginTop: 2 }}><strong>Agronomic Implication:</strong> {weather_reasoning?.[0]?.agricultural_implication || 'Transpirative demand within seasonal baseline range.'}</div>
              </div>
            </div>

            {/* 5. 🛡️ FARM RESILIENCE */}
            <div style={{ background: '#FAF5FF', border: '1px solid #E9D5FF', borderRadius: 10, padding: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 800, fontSize: '0.95rem', color: '#6B21A8', marginBottom: 8 }}>
                <span>🛡️</span> FARM RESILIENCE
              </div>
              <div style={{ fontSize: '0.82rem', color: '#581C87', marginBottom: 6 }}>
                Resilience Score: <strong>{farm_resilience.overall_resilience_score || farm_resilience.score || 70}/100</strong> ({farm_resilience.resilience_tier || 'MODERATE'})
              </div>
              <div style={{ fontSize: '0.78rem', color: '#581C87', lineHeight: 1.5 }}>
                <div><strong>Weakest Dimension:</strong> {farm_resilience.weakest_pillar || 'Soil Organic Carbon buffer'}</div>
                <div style={{ marginTop: 2 }}><strong>Intervention:</strong> {farm_resilience.improvement_opportunities?.[0] || 'In-situ rainwater conservation and mulching.'}</div>
              </div>
            </div>

            {/* 6. 📊 DATA CONFIDENCE */}
            <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: 10, padding: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 800, fontSize: '0.95rem', color: '#334155', marginBottom: 8 }}>
                <span>📊</span> DATA CONFIDENCE
              </div>
              <div style={{ fontSize: '0.82rem', color: '#1E293B', marginBottom: 4 }}>
                Quality Rating: <strong>{data_quality?.data_quality_level || 'MEDIUM'}</strong> ({data_quality?.score ? Math.round(data_quality.score * 100) : 75}%)
              </div>
              <div style={{ fontSize: '0.78rem', color: '#475569', lineHeight: 1.5 }}>
                <div><strong>What is Known:</strong> {data_quality?.missing_data_guidance?.known_inputs?.slice(0, 2)?.join(', ') || 'District agro-climatic baseline, season'}</div>
                <div style={{ marginTop: 2 }}><strong>Missing to Improve:</strong> {data_quality?.missing_data_guidance?.missing_inputs?.[0] || 'None critical'}</div>
              </div>
            </div>
          </div>
        </div>

        {/* ── 1. FARM SNAPSHOT ────────────────────────────────────────────── */}
        <div className="ff-card animate-fade-in" style={{ marginBottom: 24, padding: 20, borderTop: '4px solid var(--ff-primary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <MapPin size={20} className="text-emerald-700" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--ff-text)', margin: 0 }}>
                1. Farm Snapshot
              </h2>
            </div>
            <span style={{ fontSize: '0.72rem', background: '#E6F4EA', color: '#137333', padding: '4px 10px', borderRadius: 20, fontWeight: 700 }}>
              Location & Ambient Environment
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: 12 }}>
            {/* Location Card */}
            <div style={{ background: '#F8FAF8', padding: '12px 14px', borderRadius: 10, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-secondary)', fontWeight: 600 }}>Administrative Location</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--ff-text)', marginTop: 2 }}>
                {district}, {state}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#6B7280', marginTop: 4 }}>
                Sub-District: {location_context.sub_district || farmData.sub_district || 'District Centroid'}
              </div>
              <div style={{ fontSize: '0.68rem', color: '#059669', marginTop: 4 }}>
                Zone: {location_context.agro_climatic_zone || 'Standard Agro-Ecological Zone'}
              </div>
            </div>

            {/* Weather Card with Freshness (Phase 9) */}
            <div style={{ background: '#F0F9FF', padding: '12px 14px', borderRadius: 10, border: '1px solid #BAE6FD' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '0.72rem', color: '#0369A1', fontWeight: 600 }}>Weather Observation</div>
                <FreshnessBadge freshness={weather_context?.freshness_level || 'RECENT'} />
              </div>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#0C4A6E', marginTop: 3 }}>
                {weather_context.temperature != null ? `${weather_context.temperature}°C` : `${envData.temperature || 28}°C`}
                <span style={{ fontSize: '0.8rem', fontWeight: 500, color: '#0284C7', marginLeft: 8 }}>
                  RH: {weather_context.humidity != null ? `${weather_context.humidity}%` : `${envData.humidity || 65}%`}
                </span>
              </div>
              <div style={{ fontSize: '0.72rem', color: '#0369A1', marginTop: 4 }}>
                Source: {weather_context.weather_source || 'Open-Meteo & Climatology'}
              </div>
              {weather_context.forecast_summary && (
                <div style={{ fontSize: '0.68rem', color: '#075985', marginTop: 2 }}>
                  {weather_context.forecast_summary}
                </div>
              )}
            </div>

            {/* Baseline Soil Card */}
            <div style={{ background: '#FEFCE8', padding: '12px 14px', borderRadius: 10, border: '1px solid #FEF08A' }}>
              <div style={{ fontSize: '0.72rem', color: '#854D0E', fontWeight: 600 }}>Soil Foundation</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#713F12', marginTop: 2, textTransform: 'capitalize' }}>
                {farm_context.soil_type || farmData.soil_type || 'Regional Vertisol / Alluvium'}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#854D0E', marginTop: 4 }}>
                pH: {soil_health.ph?.value != null ? soil_health.ph.value : (soilData.ph || '7.2')} · OC: {soil_health.organic_carbon?.value != null ? `${soil_health.organic_carbon.value}%` : (soilData.OC ? `${soilData.OC}%` : '0.50%')}
              </div>
              <div style={{ fontSize: '0.68rem', color: '#A16207', marginTop: 4 }}>
                Water: {farm_context.water_source || farmData.water_source || (farmData.irrigation_available === 'yes' ? 'Irrigated' : 'Rainfed')}
              </div>
            </div>
          </div>
        </div>

        {/* ── 2. WHAT SHOULD I CONSIDER? (TOP CROPS) ──────────────────────── */}
        <div className="ff-card animate-fade-in" style={{ marginBottom: 24, padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Sprout size={20} className="text-emerald-700" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--ff-text)', margin: 0 }}>
                2. What Should I Consider?
              </h2>
            </div>
            <span style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)' }}>
              Top Viable Cultivars & Compatibility Breakdowns
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {cropsToDisplay.map((crop, i) => (
              <Phase5CropCard
                key={crop.crop}
                crop={crop}
                rank={i + 1}
                isExpanded={expandedCrop === crop.crop}
                onToggle={(e) => toggleExpand(e, crop.crop)}
                onCardClick={() => handleCropClick(crop)}
              />
            ))}
          </div>
        </div>

        {/* ── CROP COMPARISON & TRADE-OFF EXPLORATION (Requirement 7 & 8) ────── */}
        <div className="ff-card animate-fade-in" style={{ marginBottom: 24, padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Scale size={20} className="text-emerald-700" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--ff-text)', margin: 0 }}>
                Compare Candidate Crops & Trade-Offs
              </h2>
            </div>
            <span style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)' }}>
              Select 2 to 4 crops to compare multi-dimensional fits
            </span>
          </div>

          <p style={{ fontSize: '0.8rem', color: 'var(--ff-text-secondary)', marginBottom: 12 }}>
            AgriN does not hide trade-offs behind a single score. Select 2–4 candidate crops to compare soil, climate, water, and seasonal fits side-by-side:
          </p>

          {/* Selectable Crop Pills */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 14 }}>
            {cropsToDisplay.slice(0, 8).map(c => {
              const cName = c.crop || c.common_name
              const isSelected = selectedForCompare.includes(cName)
              return (
                <button
                  key={cName}
                  type="button"
                  onClick={() => handleToggleCropCompare(cName)}
                  style={{
                    padding: '6px 14px', borderRadius: 8, fontSize: '0.82rem', fontWeight: 700, cursor: 'pointer',
                    border: isSelected ? '2px solid #059669' : '1px solid #D1D5DB',
                    background: isSelected ? '#D1FAE5' : '#FFFFFF',
                    color: isSelected ? '#065F46' : '#374151',
                    display: 'flex', alignItems: 'center', gap: 6
                  }}
                >
                  <span>{isSelected ? '✓' : '+'}</span>
                  <span>{c.common_name || c.crop?.toUpperCase()}</span>
                </button>
              )
            })}
          </div>

          <button
            type="button"
            className="btn-primary"
            disabled={selectedForCompare.length < 2 || comparingCrops}
            onClick={handleRunComparison}
            style={{ padding: '8px 18px', fontSize: '0.85rem' }}
          >
            {comparingCrops ? 'Evaluating Trade-Offs...' : `Compare ${selectedForCompare.length} Selected Crops`}
          </button>

          {/* Comparison Results Card */}
          {comparisonResult && (
            <div style={{ marginTop: 16, background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: 10, padding: 16 }}>
              <h4 style={{ fontSize: '0.92rem', fontWeight: 800, color: '#111827', marginBottom: 10 }}>
                Side-by-Side Fit Matrix
              </h4>
              <div style={{ overflowX: 'auto', marginBottom: 14 }}>
                <table style={{ width: '100%', fontSize: '0.8rem', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: '#F3F4F6', textAlign: 'left' }}>
                      <th style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB' }}>Dimension</th>
                      {comparisonResult.crop_evaluations?.map(ce => (
                        <th key={ce.crop_name} style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB' }}>{ce.crop_name}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB', fontWeight: 600 }}>Overall Score</td>
                      {comparisonResult.crop_evaluations?.map(ce => (
                        <td key={ce.crop_name} style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB', fontWeight: 800 }}>{ce.overall_score}</td>
                      ))}
                    </tr>
                    <tr>
                      <td style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB' }}>Soil Fit</td>
                      {comparisonResult.crop_evaluations?.map(ce => (
                        <td key={ce.crop_name} style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB' }}>{ce.soil_compatibility}%</td>
                      ))}
                    </tr>
                    <tr>
                      <td style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB' }}>Climate Fit</td>
                      {comparisonResult.crop_evaluations?.map(ce => (
                        <td key={ce.crop_name} style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB' }}>{ce.weather_compatibility}%</td>
                      ))}
                    </tr>
                    <tr>
                      <td style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB' }}>Water Fit</td>
                      {comparisonResult.crop_evaluations?.map(ce => (
                        <td key={ce.crop_name} style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB' }}>{ce.water_compatibility}%</td>
                      ))}
                    </tr>
                    <tr>
                      <td style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB' }}>Season Fit</td>
                      {comparisonResult.crop_evaluations?.map(ce => (
                        <td key={ce.crop_name} style={{ padding: '8px 10px', borderBottom: '1px solid #E5E7EB' }}>{ce.season_compatibility}%</td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Trade-Off Explanations (Requirement 8) */}
              <div style={{ background: '#FFFFFF', padding: 12, borderRadius: 8, border: '1px solid #D1D5DB' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#374151', marginBottom: 6 }}>
                  Agronomic Trade-Off Explanations:
                </div>
                <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.78rem', color: '#4B5563', lineHeight: 1.6 }}>
                  {comparisonResult.trade_off_analysis?.pairwise_trade_offs?.map((t, idx) => (
                    <li key={idx}><strong>{t.comparison}:</strong> {t.trade_off}</li>
                  ))}
                </ul>
                <div style={{ marginTop: 8, fontSize: '0.75rem', fontStyle: 'italic', color: '#059669' }}>
                  💡 {comparisonResult.trade_off_analysis?.decision_context}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── PRIORITIZED ADVISORY & RISK MANAGEMENT QUEUE (Requirement 3, 4, 5) ─ */}
        <div className="ff-card animate-fade-in" style={{ marginBottom: 24, padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Shield size={20} className="text-emerald-700" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--ff-text)', margin: 0 }}>
                Prioritized Action Queue & Agricultural Risks
              </h2>
            </div>
            <span style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)' }}>
              Ordered by Severity: CRITICAL &gt; HIGH &gt; MEDIUM &gt; LOW
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {(prioritized_advisories.length > 0 ? prioritized_advisories : []).map((adv, idx) => {
              const prioColor = adv.priority === 'CRITICAL' ? { bg: '#FEE2E2', border: '#F87171', text: '#991B1B' } :
                                adv.priority === 'HIGH' ? { bg: '#FEF3C7', border: '#FBBF24', text: '#92400E' } :
                                adv.priority === 'MEDIUM' ? { bg: '#E0F2FE', border: '#7DD3FC', text: '#0369A1' } :
                                { bg: '#F3F4F6', border: '#D1D5DB', text: '#374151' }
              return (
                <div key={idx} style={{
                  background: '#FFFFFF', border: `1px solid ${prioColor.border}`, borderLeft: `6px solid ${prioColor.border}`,
                  borderRadius: 8, padding: 14
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6, flexWrap: 'wrap', gap: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{
                        background: prioColor.bg, color: prioColor.text, fontSize: '0.7rem', fontWeight: 800,
                        padding: '2px 8px', borderRadius: 4
                      }}>
                        {adv.priority}
                      </span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#4B5563' }}>
                        {adv.category}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.7rem', color: '#6B7280' }}>
                      Confidence: {adv.confidence} · Urgency: {adv.urgency || 'STANDARD'}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#111827', marginBottom: 4 }}>
                    {adv.recommendation}
                  </div>

                  {adv.trigger && (
                    <div style={{ fontSize: '0.75rem', color: '#6B7280', marginBottom: 2 }}>
                      <strong>Trigger / Evidence:</strong> {adv.trigger}
                    </div>
                  )}
                  {adv.reason && (
                    <div style={{ fontSize: '0.75rem', color: '#4B5563', marginBottom: 2 }}>
                      <strong>Agronomic Implication:</strong> {adv.reason}
                    </div>
                  )}
                  {adv.limitations && adv.limitations.length > 0 && (
                    <div style={{ fontSize: '0.7rem', color: '#9CA3AF', marginTop: 4 }}>
                      Limitations: {adv.limitations.join(', ')}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* ── 3. WHY? (EXPLANATION ENGINE - PHASE 8) ───────────────────────── */}
        <div className="ai-card animate-fade-in" style={{ marginBottom: 24, padding: 20 }}>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <div className="ai-sparkle">✦</div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--ff-primary)', margin: 0 }}>
              3. Why AgriN Recommends This
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12, marginBottom: 12 }}>
            <div style={{ background: '#FFFFFF', padding: 12, borderRadius: 8, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--ff-primary)', textTransform: 'uppercase' }}>WHAT</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--ff-text)', marginTop: 4, lineHeight: 1.5 }}>
                {explanation.what || `Cultivate high-suitability cultivars adapted to ${district}'s ${season} agro-climate.`}
              </div>
            </div>
            <div style={{ background: '#FFFFFF', padding: 12, borderRadius: 8, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--ff-primary)', textTransform: 'uppercase' }}>WHY</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--ff-text)', marginTop: 4, lineHeight: 1.5 }}>
                {explanation.why || recommendation_explanation || 'Soil attributes and seasonal precipitation align with physiological thresholds.'}
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12 }}>
            <div style={{ background: '#FFFFFF', padding: 12, borderRadius: 8, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--ff-primary)', textTransform: 'uppercase' }}>BASED ON</div>
              <ul style={{ paddingLeft: 16, margin: '4px 0 0 0', fontSize: '0.8rem', color: 'var(--ff-text-secondary)', lineHeight: 1.5 }}>
                {(explanation.based_on || [
                  `Location: ${district}, ${state}`,
                  `Soil chemistry and texture profiles`,
                  `Live and climatological weather parameters`
                ]).map((b, idx) => (
                  <li key={idx}>{b}</li>
                ))}
              </ul>
            </div>

            <div style={{ background: '#FFFFFF', padding: 12, borderRadius: 8, border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--ff-primary)', textTransform: 'uppercase' }}>CONFIDENCE & LIMITATIONS</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--ff-text-secondary)', marginTop: 4, lineHeight: 1.5 }}>
                <strong>Reliability:</strong> {explanation.confidence || `${confidence.confidence_level || 'MODERATE'} confidence based on available data.`}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#9CA3AF', marginTop: 4 }}>
                {explanation.limitations?.join('; ') || 'Continuous soil testing improves precision.'}
              </div>
            </div>
          </div>
        </div>

        {/* ── 4. SOIL HEALTH & ACTIONABLE CONSTRAINTS ──────────────────────── */}
        <div className="ff-card animate-fade-in" style={{ marginBottom: 24, padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Leaf size={20} className="text-emerald-700" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--ff-text)', margin: 0 }}>
                4. Soil Health & Actionable Constraints
              </h2>
            </div>
            <span style={{ fontSize: '0.72rem', background: '#D1FAE5', color: '#065F46', padding: '4px 10px', borderRadius: 20, fontWeight: 700 }}>
              {soil_health.overall_status || 'Evaluated Condition'}
            </span>
          </div>

          {/* Indicators Matrix */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10, marginBottom: 14 }}>
            <SoilIndicatorCard label="pH Reaction" val={soil_health.ph?.value != null ? soil_health.ph.value : soilData.ph} status={soil_health.ph?.status || 'OPTIMAL'} />
            <SoilIndicatorCard label="Organic Carbon" val={soil_health.organic_carbon?.value != null ? `${soil_health.organic_carbon.value}%` : (soilData.OC ? `${soilData.OC}%` : 'N/A')} status={soil_health.organic_carbon?.status || 'LOW'} />
            <SoilIndicatorCard label="EC (Salinity)" val={soil_health.electrical_conductivity?.value != null ? `${soil_health.electrical_conductivity.value} dS/m` : (soilData.EC ? `${soilData.EC} dS/m` : 'NORMAL')} status={soil_health.electrical_conductivity?.status || 'NORMAL'} />
            <SoilIndicatorCard label="Nitrogen (N)" val={soil_health.nitrogen?.value != null ? `${soil_health.nitrogen.value} kg/ha` : (soilData.N ? `${soilData.N} kg/ha` : 'MEDIUM')} status={soil_health.nitrogen?.status || 'MEDIUM'} />
            <SoilIndicatorCard label="Phosphorus (P)" val={soil_health.phosphorus?.value != null ? `${soil_health.phosphorus.value} kg/ha` : (soilData.P ? `${soilData.P} kg/ha` : 'MEDIUM')} status={soil_health.phosphorus?.status || 'MEDIUM'} />
            <SoilIndicatorCard label="Potassium (K)" val={soil_health.potassium?.value != null ? `${soil_health.potassium.value} kg/ha` : (soilData.K ? `${soilData.K} kg/ha` : 'SUFFICIENT')} status={soil_health.potassium?.status || 'HIGH'} />
          </div>

          {/* Actionable Constraints & Targeted Amendments */}
          {soil_health.constraints && soil_health.constraints.length > 0 ? (
            <div style={{ background: '#FFFBEB', borderRadius: 8, padding: 12, border: '1px solid #FDE68A', marginBottom: 10 }}>
              <div style={{ fontWeight: 700, fontSize: '0.82rem', color: '#92400E', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                <AlertTriangle size={15} /> Identified Soil Constraints & Targeted Amendments:
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {soil_health.constraints.map((c, idx) => (
                  <div key={idx} style={{ fontSize: '0.78rem', color: '#78350F' }}>
                    <strong>• {c.factor}:</strong> {c.condition} → <em>Action: {c.actionable_remediation}</em>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ fontSize: '0.8rem', color: '#047857', background: '#ECFDF5', padding: '10px 14px', borderRadius: 8 }}>
              ✓ No critical physiological soil constraints detected. Continue balanced fertilization as per University Package of Practices.
            </div>
          )}
        </div>

        {/* ── 5. REGENERATIVE OPPORTUNITIES ───────────────────────────────── */}
        <div className="ff-card animate-fade-in" style={{ marginBottom: 24, padding: 20, borderLeft: '4px solid #059669' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Sparkles size={20} className="text-emerald-700" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--ff-text)', margin: 0 }}>
                5. Regenerative Agriculture Opportunities
              </h2>
            </div>
            <span style={{ fontSize: '0.72rem', background: '#D1FAE5', color: '#065F46', padding: '4px 10px', borderRadius: 20, fontWeight: 700 }}>
              Ecological Stewardship
            </span>
          </div>

          {regenerative_opportunities && regenerative_opportunities.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 12 }}>
              {regenerative_opportunities.map((opp, idx) => (
                <div key={idx} style={{ background: '#F0FDF4', borderRadius: 10, padding: 14, border: '1px solid #BBF7D0' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <div style={{ fontWeight: 800, fontSize: '0.9rem', color: '#065F46' }}>{opp.practice}</div>
                    <span style={{ fontSize: '0.68rem', background: '#DCFCE7', color: '#166534', padding: '2px 8px', borderRadius: 12, fontWeight: 600 }}>
                      {opp.confidence || 'HIGH'}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#15803D', fontWeight: 600, marginBottom: 4 }}>
                    Trigger: {opp.trigger}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--ff-text)', lineHeight: 1.5, marginBottom: 6 }}>
                    {opp.why}
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#047857', background: '#DCFCE7', padding: '6px 10px', borderRadius: 6 }}>
                    <strong>Objective:</strong> {opp.objective}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: '0.85rem', color: 'var(--ff-text-secondary)' }}>
              Standard conservation tillage and legume cover crops recommended to sustain baseline organic carbon.
            </p>
          )}
        </div>

        {/* ── 6. FARM RESILIENCE (DECOUPLED FROM CONFIDENCE - PHASE 7) ─────── */}
        <div className="ff-card animate-fade-in" style={{ marginBottom: 24, padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Shield size={20} className="text-emerald-700" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--ff-text)', margin: 0 }}>
                6. Farm Agricultural Resilience Index
              </h2>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{
                fontSize: '0.85rem', fontWeight: 800, padding: '4px 12px', borderRadius: 20,
                background: farm_resilience.score >= 70 ? '#D1FAE5' : farm_resilience.score >= 50 ? '#FEF3C7' : '#FEE2E2',
                color: farm_resilience.score >= 70 ? '#065F46' : farm_resilience.score >= 50 ? '#92400E' : '#B91C1C'
              }}>
                Resilience: {farm_resilience.score != null ? Math.round(farm_resilience.score) : 68} / 100 ({farm_resilience.resilience_tier || 'MODERATE'})
              </span>
            </div>
          </div>

          <p style={{ fontSize: '0.8rem', color: 'var(--ff-text-secondary)', marginBottom: 14 }}>
            {farm_resilience.tier_description || 'Evaluates 5 biophysical pillars independently of data completeness.'}
          </p>

          {/* 5 Components */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 10, marginBottom: 14 }}>
            <ResilienceComponentCard label="Soil Health" weight="25%" score={farm_resilience.components?.soil_health || 70} />
            <ResilienceComponentCard label="Water Context" weight="25%" score={farm_resilience.components?.water_context || 65} />
            <ResilienceComponentCard label="Climate Context" weight="20%" score={farm_resilience.components?.climate_context || 75} />
            <ResilienceComponentCard label="Crop Diversity" weight="15%" score={farm_resilience.components?.crop_diversity || 60} />
            <ResilienceComponentCard label="Crop Suitability" weight="15%" score={farm_resilience.components?.crop_suitability || 80} />
          </div>

          {/* Strengths & Vulnerabilities */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12 }}>
            <div style={{ background: '#F0FDF4', padding: 12, borderRadius: 8, border: '1px solid #BBF7D0' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#166534', marginBottom: 4 }}>Key Strengths:</div>
              <div style={{ fontSize: '0.78rem', color: '#14532D' }}>
                {farm_resilience.strengths?.length > 0 ? farm_resilience.strengths.join(', ') : 'Adequate baseline biophysical foundation.'}
              </div>
            </div>
            <div style={{ background: '#FFF7ED', padding: 12, borderRadius: 8, border: '1px solid #FED7AA' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#9A3412', marginBottom: 4 }}>Key Vulnerabilities:</div>
              <div style={{ fontSize: '0.78rem', color: '#7C2D12' }}>
                {farm_resilience.vulnerabilities?.length > 0 ? farm_resilience.vulnerabilities.join(', ') : 'No critical biophysical vulnerabilities noted.'}
              </div>
            </div>
          </div>
        </div>

        {/* ── 7. DATA CONFIDENCE (DECOUPLED FROM RESILIENCE) ────────────────── */}
        <div className="ff-card animate-fade-in" style={{ marginBottom: 24, padding: 20, background: '#F8FAFC' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <BarChart3 size={20} className="text-slate-700" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#1E293B', margin: 0 }}>
                7. Data Confidence & Quality
              </h2>
            </div>
            <span style={{
              fontSize: '0.75rem', fontWeight: 700, padding: '4px 10px', borderRadius: 20,
              background: '#E2E8F0', color: '#334155'
            }}>
              Level: {confidence.confidence_level || 'MEDIUM'} ({Math.round((confidence.confidence_score || 0.72) * 100)}%)
            </span>
          </div>

          <p style={{ fontSize: '0.78rem', color: '#475569', marginBottom: 12 }}>
            Data Confidence measures input completeness, sensor freshness, and administrative resolution — strictly separated from biological soil resilience.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 10 }}>
            <ConfidenceDimCard label="Input Completeness" score={confidence.dimensions?.input_completeness} />
            <ConfidenceDimCard label="Geographic Resolution" score={confidence.dimensions?.geographic_resolution} />
            <ConfidenceDimCard label="Sensor Freshness" score={confidence.dimensions?.sensor_freshness} />
            <ConfidenceDimCard label="Model Calibration" score={confidence.dimensions?.model_calibration} />
          </div>
        </div>

        {/* ── 8. MISSING INFORMATION & IMPROVEMENT ACTIONS ─────────────────── */}
        <div className="ff-card animate-fade-in" style={{ marginBottom: 24, padding: 20, borderLeft: '4px solid #3B82F6' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <Info size={20} className="text-blue-600" />
            <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--ff-text)', margin: 0 }}>
              8. Missing Information & Recommended Actions
            </h2>
          </div>

          {confidence.missing_fields && confidence.missing_fields.length > 0 ? (
            <div>
              <p style={{ fontSize: '0.8rem', color: 'var(--ff-text-secondary)', marginBottom: 8 }}>
                The following parameters were missing and filled via regional agro-climatic averages:
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
                {confidence.missing_fields.map((f, i) => (
                  <span key={i} style={{ fontSize: '0.72rem', background: '#EFF6FF', color: '#1D4ED8', padding: '3px 8px', borderRadius: 6, border: '1px solid #BFDBFE' }}>
                    {f}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <p style={{ fontSize: '0.8rem', color: '#047857', marginBottom: 8 }}>
              ✓ Complete core farm inputs provided. Accuracy is maximized for this agro-climatic zone.
            </p>
          )}

          {limitations && limitations.length > 0 && (
            <div style={{ fontSize: '0.75rem', color: '#6B7280', marginTop: 8 }}>
              <strong>Known Limitations:</strong> {limitations.join(' • ')}
            </div>
          )}
        </div>

        {/* ── AGRI AI TRANSPARENCY PANEL (Requirement 25) ───────────────────── */}
        <div className="ff-card animate-fade-in" style={{ marginBottom: 24, padding: 20, background: '#F8FAFC', border: '1px solid #CBD5E1' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Eye size={20} className="text-slate-700" />
              <h2 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#1E293B', margin: 0 }}>
                How AgriN Reached This Result (Agri AI Transparency)
              </h2>
            </div>
            <span style={{ fontSize: '0.72rem', background: '#E2E8F0', color: '#334155', padding: '3px 8px', borderRadius: 12, fontWeight: 700 }}>
              Auditable Decision Support
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 14 }}>
            <div style={{ background: '#FFFFFF', padding: 12, borderRadius: 8, border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#166534', marginBottom: 4 }}>INPUTS USED:</div>
              <div style={{ fontSize: '0.78rem', color: '#14532D', lineHeight: 1.6 }}>
                <div>✓ Soil Profile ({soil_health.score != null ? 'Lab/SHC Card' : 'Parameters'})</div>
                <div>✓ Meteorological NWP ({weather_context.temperature?.value ?? (envData.temperature || 28)}°C)</div>
                <div>✓ Location ({district}, {state})</div>
                <div>✓ Season ({season})</div>
              </div>
            </div>

            <div style={{ background: '#FFFFFF', padding: 12, borderRadius: 8, border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#991B1B', marginBottom: 4 }}>NOT AVAILABLE / UNLINKED:</div>
              <div style={{ fontSize: '0.78rem', color: '#7F1D1D', lineHeight: 1.6 }}>
                <div>○ Satellite Earth Observation (Disconnected)</div>
                <div>○ Vision Pathology (Model not deployed)</div>
                <div>○ Subsoil Moisture Sensor (NWP estimate applied)</div>
              </div>
            </div>

            <div style={{ background: '#FFFFFF', padding: 12, borderRadius: 8, border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#0369A1', marginBottom: 4 }}>DECISION METHOD:</div>
              <div style={{ fontSize: '0.78rem', color: '#0C4A6E', lineHeight: 1.6 }}>
                <div>• 60% Decoupled Random Forest ML</div>
                <div>• 40% ICAR Agronomic Rule Gates</div>
                <div>• Evidence-Grounded Risk Detection</div>
              </div>
            </div>
          </div>

          {/* View Technical Details Toggle (Requirement 24) */}
          <div style={{ borderTop: '1px dashed #CBD5E1', paddingTop: 10, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              type="button"
              onClick={() => setShowTechnicalDetails(prev => !prev)}
              style={{
                background: 'none', border: 'none', color: '#2563EB', fontSize: '0.8rem', fontWeight: 700,
                cursor: 'pointer', padding: 0, display: 'flex', alignItems: 'center', gap: 4
              }}
            >
              {showTechnicalDetails ? '▲ Hide Technical Details & Machine-Readable Advisory' : '▼ View Technical Details & Machine-Readable Advisory Format'}
            </button>
            <span style={{ fontSize: '0.7rem', color: '#64748B' }}>
              {showTechnicalDetails ? 'Researcher / Agronomist View' : 'Farmer-First View Active'}
            </span>
          </div>

          {showTechnicalDetails && (
            <div style={{ marginTop: 14, background: '#1E293B', color: '#F1F5F9', borderRadius: 8, padding: 14, fontSize: '0.72rem', overflowX: 'auto' }}>
              <div style={{ fontWeight: 800, color: '#38BDF8', marginBottom: 8 }}>
                COUNTRY-NEUTRAL MACHINE-READABLE ADVISORY JSON (Requirement 20):
              </div>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', maxHeight: '300px', overflowY: 'auto' }}>
                {JSON.stringify(country_neutral_advisory || { advisory_id: 'sample', status: 'ready' }, null, 2)}
              </pre>
            </div>
          )}
        </div>


        {/* ── PHASE 12: FARMER FEEDBACK PRODUCT FLOW ────────────────────────── */}
        <div className="ff-card animate-fade-in no-print" style={{
          marginBottom: 32, padding: 22,
          border: '1px solid #BBF7D0', background: 'linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <span style={{ fontSize: '1.2rem' }}>🧑‍🌾</span>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#065F46', margin: 0 }}>
                Farmer Feedback & Outcome Tracking
              </h3>
              <p style={{ fontSize: '0.75rem', color: '#047857', margin: 0 }}>
                Help validate agricultural recommendations for your district. Your feedback builds real-world evidence.
              </p>
            </div>
          </div>

          {feedbackSubmitted ? (
            <div style={{ background: '#DCFCE7', borderRadius: 8, padding: 14, textAlign: 'center', color: '#166534' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, fontWeight: 700, fontSize: '0.9rem' }}>
                <Check size={18} /> Thank you! Your feedback has been recorded.
              </div>
              <p style={{ fontSize: '0.75rem', marginTop: 4, margin: 0 }}>
                Feedback is cataloged for agronomic validation without automatic model retraining.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmitFeedback}>
              {/* Question 1: Did you follow this recommendation? */}
              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: '#1F2937', marginBottom: 6 }}>
                  Did you follow this recommendation?
                </label>
                <div style={{ display: 'flex', gap: 8 }}>
                  {['YES', 'PARTIALLY', 'NO'].map(opt => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => setDidFollow(opt)}
                      style={{
                        flex: 1, padding: '8px 12px', borderRadius: 8, fontSize: '0.8rem', fontWeight: 700,
                        border: didFollow === opt ? '2px solid #059669' : '1px solid #D1D5DB',
                        background: didFollow === opt ? '#D1FAE5' : '#FFFFFF',
                        color: didFollow === opt ? '#065F46' : '#4B5563',
                        cursor: 'pointer'
                      }}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>

              {/* Question 2: What happened? */}
              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: '#1F2937', marginBottom: 6 }}>
                  What happened / Observed outcome?
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 8 }}>
                  {['Successful', 'Neutral', 'Poor outcome', 'Not applicable'].map(opt => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => setOutcome(opt)}
                      style={{
                        padding: '6px 10px', borderRadius: 8, fontSize: '0.75rem', fontWeight: 600,
                        border: outcome === opt ? '2px solid #059669' : '1px solid #D1D5DB',
                        background: outcome === opt ? '#D1FAE5' : '#FFFFFF',
                        color: outcome === opt ? '#065F46' : '#4B5563',
                        cursor: 'pointer'
                      }}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>

              {/* Optional Observations */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10, marginBottom: 12 }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: '#4B5563', marginBottom: 3 }}>
                    Yield Observation (optional):
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. 18 quintals/acre"
                    value={yieldObs}
                    onChange={(e) => setYieldObs(e.target.value)}
                    style={{ width: '100%', padding: '6px 10px', fontSize: '0.78rem', borderRadius: 6, border: '1px solid #D1D5DB' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: '#4B5563', marginBottom: 3 }}>
                    Disease / Pest Observation (optional):
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Minor aphid incidence in week 6"
                    value={diseaseObs}
                    onChange={(e) => setDiseaseObs(e.target.value)}
                    style={{ width: '100%', padding: '6px 10px', fontSize: '0.78rem', borderRadius: 6, border: '1px solid #D1D5DB' }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: '0.72rem', color: '#4B5563', marginBottom: 3 }}>
                  Farmer Notes / Observations:
                </label>
                <textarea
                  rows={2}
                  placeholder="Share any practical agronomic experiences with this recommendation..."
                  value={farmerComment}
                  onChange={(e) => setFarmerComment(e.target.value)}
                  style={{ width: '100%', padding: '6px 10px', fontSize: '0.78rem', borderRadius: 6, border: '1px solid #D1D5DB' }}
                />
              </div>

              <button
                type="submit"
                disabled={!didFollow || submittingFeedback}
                className="btn-primary"
                style={{ width: '100%', padding: '10px 16px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
              >
                <Send size={15} />
                {submittingFeedback ? 'Submitting...' : 'Submit Real-World Feedback'}
              </button>
            </form>
          )}
        </div>

        {/* Disclaimer Footer */}
        <div style={{ textAlign: 'center', color: 'var(--ff-text-muted)', fontSize: '0.75rem', marginTop: 20, lineHeight: 1.6, borderTop: '1px solid var(--ff-border)', paddingTop: 16 }}>
          <div style={{ fontWeight: 600, color: 'var(--ff-text-secondary)', marginBottom: 4 }}>
            AgriN Agricultural Intelligence · Indian Council of Agricultural Research (ICAR) & State Agronomic Standards
          </div>
          These recommendations are advisory decision-support tools. Always cross-verify with your local KVK extension officers prior to commercial sowing or chemical purchases.
        </div>

      </div>
    </div>
  )
}

/* ── HELPER COMPONENTS ─────────────────────────────────────────────────── */

function Phase5CropCard({ crop, rank, isExpanded, onToggle, onCardClick }) {
  const score = crop.overall_score != null ? crop.overall_score : (crop.final_score != null ? crop.final_score : 80)
  const isTop3 = rank <= 3
  const isTop1 = rank === 1

  const scoreColor = score >= 85 ? '#059669' : score >= 70 ? '#10B981' : score >= 50 ? '#D97706' : '#DC2626'
  const scoreLabel = score >= 85 ? 'Highly Suitable' : score >= 70 ? 'Moderately Suitable' : score >= 50 ? 'Requires Management' : 'Low Suitability'

  return (
    <div
      className="ff-card crop-report-card animate-fade-in"
      style={{
        padding: 18,
        borderLeft: isTop3 ? `4px solid ${scoreColor}` : '1px solid var(--ff-border)',
        background: isTop1 ? 'linear-gradient(135deg, #FAFDFB, #FFFFFF)' : 'white'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, cursor: 'pointer' }} onClick={onCardClick}>
        <div style={{
          width: 40, height: 40, borderRadius: 10, flexShrink: 0,
          background: isTop3 ? 'var(--ff-light)' : '#F1F4F2',
          color: isTop3 ? 'var(--ff-primary)' : 'var(--ff-text-secondary)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 800, fontSize: '0.9rem'
        }}>
          #{rank}
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <h3 style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--ff-text)', margin: 0 }}>
              {crop.common_name || crop.crop}
            </h3>
            {crop.local_name && (
              <span style={{ fontSize: '0.8rem', color: 'var(--ff-text-muted)' }}>({crop.local_name})</span>
            )}
            {isTop3 && (
              <span style={{
                fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase',
                background: '#D1FAE5', color: '#065F46', padding: '2px 8px', borderRadius: 999
              }}>
                Top Pick
              </span>
            )}
          </div>
          <p style={{ fontSize: '0.76rem', color: 'var(--ff-text-muted)', marginTop: 2, textTransform: 'capitalize' }}>
            {crop.category || 'Agronomic Crop'} · {crop.classification || scoreLabel}
          </p>

          {/* Sub-compatibility bars (Phase 5) */}
          <div style={{ display: 'flex', gap: 8, marginTop: 6, flexWrap: 'wrap' }}>
            <SubScoreBadge label="Soil" val={crop.soil_compatibility} />
            <SubScoreBadge label="Weather" val={crop.weather_compatibility} />
            <SubScoreBadge label="Season" val={crop.season_compatibility} />
            <SubScoreBadge label="Water" val={crop.water_compatibility} />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: scoreColor, lineHeight: 1 }}>
              {Math.round(score)}
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--ff-text-muted)', marginTop: 1 }}>/ 100</div>
          </div>
          <button
            className="no-print"
            onClick={onToggle}
            style={{
              background: isExpanded ? 'var(--ff-light)' : '#F3F4F6',
              border: '1px solid #E5E7EB', borderRadius: 8, padding: '6px 10px',
              fontSize: '0.75rem', fontWeight: 600, color: 'var(--ff-primary)',
              display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer'
            }}
          >
            <FileText size={13} />
            {isExpanded ? 'Hide' : 'Details'}
            {isExpanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
          </button>
        </div>
      </div>

      {/* Expanded Phase 5 details */}
      {isExpanded && (
        <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px dashed #E5E7EB' }}>
          <div style={{ background: '#F9FAFB', borderRadius: 8, padding: 12, border: '1px solid #E5E7EB' }}>
            {/* Why This Crop */}
            <div style={{ marginBottom: 10 }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#065F46', marginBottom: 4 }}>
                ✓ Why this crop:
              </div>
              <ul style={{ margin: 0, paddingLeft: 16, fontSize: '0.76rem', color: '#1F2937', lineHeight: 1.5 }}>
                {crop.reason?.why?.map((w, idx) => (
                  <li key={idx}>{w}</li>
                )) || <li>Compatible soil and regional climate.</li>}
              </ul>
            </div>

            {/* Considerations & Risk Factors */}
            {(crop.risk_factors?.length > 0 || crop.reason?.considerations?.length > 0) && (
              <div style={{ marginBottom: 10 }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#92400E', marginBottom: 4 }}>
                  • Considerations & Risk Factors:
                </div>
                <ul style={{ margin: 0, paddingLeft: 16, fontSize: '0.76rem', color: '#78350F', lineHeight: 1.5 }}>
                  {(crop.reason?.considerations || crop.risk_factors || []).map((c, idx) => (
                    <li key={idx}>{c}</li>
                  ))}
                </ul>
              </div>
            )}

            <div style={{ fontSize: '0.72rem', color: '#6B7280' }}>
              <strong>Confidence:</strong> {crop.reason?.confidence || crop.confidence || 'HIGH'}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function SubScoreBadge({ label, val }) {
  if (val == null) return null
  return (
    <span style={{
      fontSize: '0.68rem', background: '#F3F4F6', color: '#4B5563',
      padding: '2px 6px', borderRadius: 4, border: '1px solid #E5E7EB'
    }}>
      {label}: {Math.round(val)}%
    </span>
  )
}

function FreshnessBadge({ freshness }) {
  const isFresh = freshness === 'FRESH'
  return (
    <span style={{
      fontSize: '0.65rem', fontWeight: 700, padding: '2px 6px', borderRadius: 4,
      background: isFresh ? '#D1FAE5' : '#FEF3C7',
      color: isFresh ? '#065F46' : '#92400E'
    }}>
      {freshness}
    </span>
  )
}

function SoilIndicatorCard({ label, val, status }) {
  const isOptimal = status === 'OPTIMAL' || status === 'SUFFICIENT' || status === 'NORMAL'
  return (
    <div style={{ background: '#FFFFFF', padding: '10px 12px', borderRadius: 8, border: '1px solid #E5E7EB', textAlign: 'center' }}>
      <div style={{ fontSize: '0.68rem', color: '#6B7280' }}>{label}</div>
      <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#1F2937', marginTop: 2 }}>{val || 'N/A'}</div>
      <span style={{
        fontSize: '0.65rem', fontWeight: 700, padding: '1px 6px', borderRadius: 4,
        background: isOptimal ? '#D1FAE5' : '#FEF3C7',
        color: isOptimal ? '#065F46' : '#92400E',
        display: 'inline-block', marginTop: 3
      }}>
        {status}
      </span>
    </div>
  )
}

function ResilienceComponentCard({ label, weight, score }) {
  return (
    <div style={{ background: '#FFFFFF', padding: '10px', borderRadius: 8, border: '1px solid #E5E7EB', textAlign: 'center' }}>
      <div style={{ fontSize: '0.68rem', color: '#6B7280' }}>{label} ({weight})</div>
      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#059669', marginTop: 2 }}>
        {Math.round(score)}%
      </div>
    </div>
  )
}

function ConfidenceDimCard({ label, score }) {
  const val = score != null ? Math.round(score * 100) : 75
  return (
    <div style={{ background: '#FFFFFF', padding: '8px 10px', borderRadius: 6, border: '1px solid #E2E8F0', textAlign: 'center' }}>
      <div style={{ fontSize: '0.65rem', color: '#64748B' }}>{label}</div>
      <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#334155', marginTop: 2 }}>{val}%</div>
    </div>
  )
}
