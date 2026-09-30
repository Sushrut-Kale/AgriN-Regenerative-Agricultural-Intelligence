import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { ChevronRight, ChevronDown, Sprout, AlertTriangle, Leaf, BarChart3, Printer, FileText, CheckCircle, XCircle, Shield, Info } from 'lucide-react'

export default function Recommendations() {
  const navigate = useNavigate()
  const { analysisResult, setSelectedCrop, farmData, soilData, envData } = useApp()
  const [expandedCrop, setExpandedCrop] = useState(null)

  if (!analysisResult) {
    navigate('/farm-details')
    return null
  }

  const { ranked_crops, recommendation_explanation, data_completeness, model_info, session_id } = analysisResult
  const district = farmData.district || 'Your District'
  const season = farmData.season || 'Kharif'
  const reportDate = new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })

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

  return (
    <div className="page-bg" style={{ minHeight: '100vh' }}>

      {/* ── Page Header ───────────────────────────────────────────── */}
      <div className="ff-nav px-6 py-4 flex items-center justify-between no-print" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className="ff-logo-icon">
            <Leaf size={16} className="text-white" />
          </div>
          <div>
            <h1 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--ff-text)' }}>Crop Suitability & Analysis Report</h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--ff-text-secondary)' }}>{district} · {season} season</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            className="btn-secondary"
            onClick={handlePrint}
            style={{ padding: '8px 16px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 6, borderColor: 'var(--ff-primary)', color: 'var(--ff-primary)' }}
          >
            <Printer size={15} />
            Print / Export PDF Report
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
            <Sprout size={15} />
            I Want to Grow This
          </button>
        </div>
      </div>

      <div className="ff-container-narrow" style={{ paddingTop: 28, paddingBottom: 48 }}>

        {/* ── Official Print Report Header (Visible on Print) ───────────────────── */}
        <div className="print-header print-only">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h1 style={{ fontSize: '20pt', fontWeight: 800, color: '#075C35', margin: 0 }}>FarmFriend AI</h1>
              <p style={{ fontSize: '11pt', fontWeight: 700, color: '#138A4B', margin: '2px 0 0 0' }}>
                Comprehensive Soil Health & Crop Suitability Decision-Support Report
              </p>
            </div>
            <div style={{ textAlign: 'right', fontSize: '9pt', color: '#4B5563' }}>
              <div><strong>Date:</strong> {reportDate}</div>
              <div><strong>Session ID:</strong> {session_id || 'LOCAL-SESSION'}</div>
              <div><strong>Location:</strong> {district}, {farmData.state || 'India'}</div>
            </div>
          </div>

          <div style={{ marginTop: 12, padding: '10px 12px', background: '#F3FAF5', border: '1px solid #BBF7D0', borderRadius: 6, fontSize: '8.5pt' }}>
            <strong>Farm Vector Summary:</strong> Season: {season.toUpperCase()} | Soil Type: {farmData.soil_type || 'Vertisol'} | Irrigation: {farmData.irrigation_available || 'No (Rainfed)'} | Drainage: {farmData.drainage || 'Good'}
            <br />
            <strong>Soil Test Inputs:</strong> N={soilData.N || '-'} kg/ha, P={soilData.P || '-'} kg/ha, K={soilData.K || '-'} kg/ha, pH={soilData.ph || '-'}, S={soilData.S || '-'} ppm, Zn={soilData.Zn || '-'} ppm, Fe={soilData.Fe || '-'} ppm, B={soilData.B || '-'} ppm | Temp={envData.temperature || '-'}°C, Humidity={envData.humidity || '-'}%, Rainfall={envData.rainfall || '-'} mm
          </div>
        </div>

        {/* Data completeness warning */}
        {data_completeness?.n_missing_soil > 6 && (
          <div className="ff-alert-warning animate-fade-in no-print" style={{ marginBottom: 20, display: 'flex', alignItems: 'flex-start', gap: 10 }}>
            <AlertTriangle size={17} style={{ flexShrink: 0, marginTop: 1 }} />
            <div>
              <p style={{ fontWeight: 600, marginBottom: 2 }}>Limited data provided</p>
              <p style={{ fontSize: '0.82rem', opacity: 0.85 }}>
                {data_completeness.n_missing_soil} of 12 soil parameters are missing. Providing complete soil test values improves accuracy.
              </p>
            </div>
          </div>
        )}

        {/* Page title header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 24 }}>
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--ff-text)', marginBottom: 4 }}>
              Your Soil & Crop Analysis Report ✅
            </h2>
            <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.9rem' }}>
              {ranked_crops?.length || 0} crops evaluated with detailed agronomic suitability breakdowns
            </p>
          </div>
          <button
            className="btn-secondary no-print"
            onClick={handlePrint}
            style={{ padding: '8px 16px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 6, background: '#E9F7EF', color: '#138A4B', border: '1px solid #BBF7D0' }}
          >
            <Printer size={16} /> Print Report
          </button>
        </div>

        {/* AI Executive Summary Explanation */}
        <div className="ai-card animate-fade-in" style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
            <div className="ai-sparkle">✦</div>
            <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--ff-primary)' }}>
              Executive Agronomic Advisory & Explanation
            </span>
          </div>
          <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.9rem', lineHeight: 1.7, whiteSpace: 'pre-line' }}>
            {recommendation_explanation}
          </p>
        </div>

        {/* ── Track 4: Farm Resilience & Regenerative Intelligence Insights ── */}
        <div className="ff-card animate-fade-in no-print" style={{ marginBottom: 24, padding: 18, border: '1px solid #10B98140', background: 'linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '1.2rem' }}>🌾</span>
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#065F46', margin: 0 }}>
                  AgriN Farm Resilience Index — prototype
                </h3>
                <p style={{ fontSize: '0.75rem', color: '#047857', margin: 0 }}>
                  Transparent 5-component resilience breakdown & long-term regenerative pathways
                </p>
              </div>
            </div>
            <span style={{ fontSize: '0.72rem', background: '#D1FAE5', color: '#065F46', padding: '4px 10px', borderRadius: 20, fontWeight: 700 }}>
              Track 4 Regenerative Intelligence
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 10, marginBottom: 12 }}>
            <div style={{ background: '#FFFFFF', padding: '10px', borderRadius: 8, border: '1px solid #E5E7EB', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-secondary)' }}>Soil Health</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#059669' }}>
                {soilData?.ph && Number(soilData.ph) >= 6.0 && Number(soilData.ph) <= 7.5 ? 'Balanced' : 'Monitor'}
              </div>
              <div style={{ fontSize: '0.68rem', color: '#6B7280' }}>pH: {soilData?.ph || 'N/A'}</div>
            </div>
            <div style={{ background: '#FFFFFF', padding: '10px', borderRadius: 8, border: '1px solid #E5E7EB', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-secondary)' }}>Water Context</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: farmData?.irrigation_available === 'yes' ? '#2563EB' : '#D97706' }}>
                {farmData?.irrigation_available === 'yes' ? 'Irrigated' : 'Rainfed'}
              </div>
              <div style={{ fontSize: '0.68rem', color: '#6B7280' }}>Rain: {envData?.rainfall || 'Normal'} mm</div>
            </div>
            <div style={{ background: '#FFFFFF', padding: '10px', borderRadius: 8, border: '1px solid #E5E7EB', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-secondary)' }}>Crop Rotation</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#7C3AED' }}>Active</div>
              <div style={{ fontSize: '0.68rem', color: '#6B7280' }}>Legume intercropping</div>
            </div>
            <div style={{ background: '#FFFFFF', padding: '10px', borderRadius: 8, border: '1px solid #E5E7EB', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-secondary)' }}>Satellite State</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#6B7280' }}>Ready</div>
              <div style={{ fontSize: '0.68rem', color: '#9CA3AF' }}>Not connected</div>
            </div>
            <div style={{ background: '#FFFFFF', padding: '10px', borderRadius: 8, border: '1px solid #E5E7EB', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-secondary)' }}>Disease Triage</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#6B7280' }}>Ready</div>
              <div style={{ fontSize: '0.68rem', color: '#9CA3AF' }}>Model not deployed</div>
            </div>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#065F46', background: '#ECFDF5', padding: '8px 12px', borderRadius: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>🌱</span>
            <span><strong>Regenerative Pathway:</strong> Incorporate pulses or green manure post-{season} to restore biological nitrogen and rebuild soil organic carbon.</span>
          </div>
        </div>

        {/* Model & System Performance Info Badges */}
        {model_info?.metrics && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 24 }}>
            <ModelBadge label="Model Architecture" value={model_info.model_type} icon="🤖" />
            <ModelBadge label="Cross-Val Accuracy" value={`${(model_info.metrics.accuracy * 100).toFixed(1)}%`} icon="🎯" />
            <ModelBadge label="Weighted F1-Score" value={model_info.metrics.f1_weighted?.toFixed(3)} icon="📊" />
            <ModelBadge label="Evaluated Crops" value={model_info.n_classes} icon="🌾" />
          </div>
        )}

        {/* Top Recommendations heading */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <BarChart3 size={18} style={{ color: 'var(--ff-primary)' }} />
          <h3 style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--ff-text)' }}>
            Ranked Crop Recommendations & Detailed Suitability Reports
          </h3>
        </div>

        {/* Ranked crop cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {ranked_crops.map((crop, i) => (
            <DetailedCropCard
              key={crop.crop}
              crop={crop}
              rank={i + 1}
              isExpanded={expandedCrop === crop.crop}
              onToggle={(e) => toggleExpand(e, crop.crop)}
              onCardClick={() => handleCropClick(crop)}
              soilData={soilData}
              envData={envData}
              farmData={farmData}
            />
          ))}
        </div>

        {/* "I Want to Grow This" CTA block */}
        <div
          className="ff-card no-print"
          style={{
            marginTop: 32, padding: 28, textAlign: 'center',
            borderTop: '3px solid var(--ff-warning)',
            background: 'linear-gradient(135deg, #FFFBF0, #FFF7E1)',
          }}
        >
          <div style={{ fontSize: 36, marginBottom: 12 }}>🌱</div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--ff-text)', marginBottom: 8 }}>
            Have another crop in mind?
          </h3>
          <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.88rem', marginBottom: 18 }}>
            Choose a specific crop you wish to cultivate and we will analyze its exact feasibility on your land.
          </p>
          <button className="btn-want" onClick={() => navigate('/i-want-to-grow')}>
            I Want to Grow This →
          </button>
        </div>

        {/* Official Report Footer & Disclaimer */}
        <div style={{ textAlign: 'center', color: 'var(--ff-text-muted)', fontSize: '0.75rem', marginTop: 28, lineHeight: 1.6, borderTop: '1px solid var(--ff-border)', paddingTop: 16 }}>
          <div style={{ fontWeight: 600, color: 'var(--ff-text-secondary)', marginBottom: 4 }}>
            FarmFriend AI Decision-Support System · Soil Health Card Standards (GoI ICAR / VNMKV)
          </div>
          These rankings and detailed reports are computed from supplied soil tests and environmental parameters.
          Always consult your district Krishi Vigyan Kendra (KVK) officer or Agricultural Extension Specialist before purchasing seeds or fertilizers.
        </div>
      </div>
    </div>
  )
}

function DetailedCropCard({ crop, rank, isExpanded, onToggle, onCardClick, soilData, envData, farmData }) {
  const score = crop.final_score
  const isTop3 = rank <= 3
  const isTop1 = rank === 1

  const scoreColor = score >= 90 ? '#138A4B' : score >= 70 ? '#20A65A' : score >= 50 ? '#D89B18' : score >= 30 ? '#E07B3A' : '#D94B4B'
  const scoreGrad = score >= 90 ? 'score-gradient-high' : score >= 70 ? 'score-gradient-medium' : score >= 50 ? 'score-gradient-amber' : score >= 30 ? 'score-gradient-low' : 'score-gradient-none'
  const scoreLabel = score >= 90 ? 'Highly Suitable' : score >= 70 ? 'Moderately Suitable' : score >= 50 ? 'Needs Attention' : score >= 30 ? 'Low Suitability' : 'Not Suitable'

  const limitingCount = crop.limiting_factors?.length || 0
  const supportingCount = crop.supporting_factors?.filter(f => f.status === 'suitable').length || 0
  const gates = crop.prediction_trace?.eligibility_gates || {}

  return (
    <div
      className="ff-card crop-report-card animate-fade-in"
      style={{
        padding: 20,
        borderLeft: isTop3 ? `4px solid ${scoreColor}` : '1px solid var(--ff-border)',
        borderLeftWidth: isTop3 ? 4 : 1,
        background: isTop1 ? 'linear-gradient(135deg, #FAFDFB, #FFFFFF)' : 'white',
      }}
    >
      {/* Main card header summary */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, cursor: 'pointer' }} onClick={onCardClick}>
        {/* Rank badge */}
        <div style={{
          width: 42, height: 42, borderRadius: 12, flexShrink: 0,
          background: isTop3 ? 'var(--ff-light)' : '#F1F4F2',
          color: isTop3 ? 'var(--ff-primary)' : 'var(--ff-text-secondary)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 800, fontSize: '0.9rem',
          border: isTop3 ? '1px solid rgba(19,138,75,0.25)' : 'none',
        }}>
          #{rank}
        </div>

        {/* Crop info */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <h3 style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--ff-text)' }}>
              {crop.common_name}
            </h3>
            {crop.local_name && (
              <span style={{ fontSize: '0.8rem', color: 'var(--ff-text-muted)' }}>({crop.local_name})</span>
            )}
            {isTop3 && (
              <span style={{
                fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em',
                background: 'var(--ff-light)', color: 'var(--ff-primary)',
                padding: '2px 8px', borderRadius: 999,
                border: '1px solid rgba(19,138,75,0.2)',
              }}>
                Top Choice
              </span>
            )}
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--ff-text-muted)', marginTop: 2, textTransform: 'capitalize' }}>
            {crop.category} · {crop.classification}
          </p>
          <div style={{ display: 'flex', gap: 12, marginTop: 6, flexWrap: 'wrap' }}>
            {supportingCount > 0 && (
              <span style={{ fontSize: '0.75rem', color: 'var(--ff-primary)', fontWeight: 500 }}>✓ {supportingCount} favourable</span>
            )}
            {limitingCount > 0 && (
              <span style={{ fontSize: '0.75rem', color: 'var(--ff-error)', fontWeight: 500 }}>✗ {limitingCount} limiting factors</span>
            )}
          </div>
        </div>

        {/* Score display & Toggle Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexShrink: 0 }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 900, color: scoreColor, lineHeight: 1 }}>
              {Math.round(score)}
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--ff-text-muted)', marginTop: 2 }}>/ 100</div>
            <div style={{ fontSize: '0.7rem', color: scoreColor, fontWeight: 600, marginTop: 1 }}>{scoreLabel}</div>
          </div>
          <button
            className="no-print"
            onClick={onToggle}
            style={{
              background: isExpanded ? 'var(--ff-light)' : 'var(--ff-soft)',
              border: '1px solid var(--ff-border)',
              borderRadius: 10, padding: '8px 12px', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 4,
              fontSize: '0.78rem', fontWeight: 600, color: 'var(--ff-primary)',
            }}
          >
            <FileText size={14} />
            {isExpanded ? 'Hide Detailed Report' : 'Detailed Report'}
            {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </button>
        </div>
      </div>

      {/* Progress Score Bar */}
      <div className="score-bar" style={{ marginTop: 14 }}>
        <div className={`score-bar-fill ${scoreGrad}`} style={{ width: `${score}%` }} />
      </div>

      {/* ── EXPANDABLE DETAILED CROP ANALYSIS REPORT ─────────────────────────── */}
      {(isExpanded || window.matchMedia('print').matches) && (
        <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px dashed var(--ff-border)' }}>
          <div style={{ background: '#F8FAF8', borderRadius: 12, padding: 16, border: '1px solid var(--ff-border)' }}>
            
            <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--ff-primary)', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
              <FileText size={16} /> Detailed Agronomic Evaluation & Suitability Report for {crop.common_name}
            </div>

            {/* Score Composition Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 14 }}>
              <ReportMetricBox label="ML Evidence Score (50%)" value={`${crop.ml_score || Math.round(crop.ml_probability * 100)} / 100`} sub="Trained Model Evidence" color="var(--ff-info)" />
              <ReportMetricBox label="Agronomic Rule Score (50%)" value={`${crop.rule_score || '-'} / 100`} sub="ICAR Standard Evaluation" color="#7C3AED" />
              <ReportMetricBox label="Gate Multiplier" value={`${gates.combined_gate_multiplier || crop.hard_gate_multiplier || 1.0}x`} sub="Season/Water/pH Gates" color="var(--ff-primary)" />
            </div>

            {/* Favourable & Limiting Factors Lists */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12, marginBottom: 14 }}>
              {/* Supporting Factors */}
              <div style={{ background: 'white', borderRadius: 10, padding: 12, border: '1px solid #BBF7D0' }}>
                <div style={{ fontWeight: 600, fontSize: '0.8rem', color: 'var(--ff-primary)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
                  <CheckCircle size={14} /> Favourable Conditions ({crop.supporting_factors?.length || 0})
                </div>
                <ul style={{ paddingLeft: 16, fontSize: '0.76rem', color: 'var(--ff-text-secondary)', lineHeight: 1.5 }}>
                  {crop.supporting_factors?.slice(0, 5).map((f, idx) => (
                    <li key={idx}><strong>{f.factor}:</strong> {f.note || 'Optimal condition'}</li>
                  ))}
                </ul>
              </div>

              {/* Limiting Factors */}
              <div style={{ background: 'white', borderRadius: 10, padding: 12, border: '1px solid #FECDD3' }}>
                <div style={{ fontWeight: 600, fontSize: '0.8rem', color: 'var(--ff-error)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
                  <XCircle size={14} /> Limiting Factors & Advisory ({crop.limiting_factors?.length || 0})
                </div>
                {crop.limiting_factors?.length > 0 ? (
                  <ul style={{ paddingLeft: 16, fontSize: '0.76rem', color: 'var(--ff-error)', lineHeight: 1.5 }}>
                    {crop.limiting_factors.map((f, idx) => (
                      <li key={idx}><strong>{f.factor}:</strong> {f.note}</li>
                    ))}
                  </ul>
                ) : (
                  <div style={{ fontSize: '0.76rem', color: 'var(--ff-text-muted)' }}>No severe limiting factors detected.</div>
                )}
              </div>
            </div>

            {/* Actionable Corrective Advisory Box */}
            <div style={{ background: 'linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)', borderRadius: 10, padding: 12, border: '1px solid #FCD34D' }}>
              <div style={{ fontWeight: 700, fontSize: '0.82rem', color: '#92400E', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                <Info size={15} /> Krishi Advisory & Soil Remediation Action Plan:
              </div>
              <p style={{ fontSize: '0.78rem', color: '#78350F', lineHeight: 1.5 }}>
                {getAgronomicAdvisory(crop)}
              </p>
            </div>

          </div>
        </div>
      )}
    </div>
  )
}

function ReportMetricBox({ label, value, sub, color }) {
  return (
    <div style={{ background: 'white', border: '1px solid var(--ff-border)', borderRadius: 10, padding: '10px 12px' }}>
      <div style={{ fontSize: '0.7rem', color: 'var(--ff-text-secondary)', fontWeight: 500 }}>{label}</div>
      <div style={{ fontSize: '1.1rem', fontWeight: 800, color, marginTop: 2 }}>{value}</div>
      <div style={{ fontSize: '0.65rem', color: 'var(--ff-text-muted)', marginTop: 1 }}>{sub}</div>
    </div>
  )
}

function ModelBadge({ label, value, icon }) {
  return (
    <div style={{
      background: 'white',
      border: '1px solid var(--ff-border)',
      borderRadius: 10, padding: '6px 12px',
      display: 'flex', alignItems: 'center', gap: 6,
      boxShadow: 'var(--ff-shadow-sm)',
    }}>
      <span style={{ fontSize: '0.85rem' }}>{icon}</span>
      <span style={{ fontSize: '0.75rem', color: 'var(--ff-text-secondary)' }}>{label}:</span>
      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--ff-primary)' }}>{value}</span>
    </div>
  )
}

function getAgronomicAdvisory(crop) {
  const limiting = crop.limiting_factors?.map(f => f.factor) || []
  let advice = []

  if (limiting.includes('Zn')) advice.push('Apply Zinc Sulfate (ZnSO₄) @ 25 kg/ha or basal soil application to correct Zinc deficiency.')
  if (limiting.includes('B')) advice.push('Apply Borax @ 10 kg/ha or foliar spray of solubor (0.2%) during flowering stage.')
  if (limiting.includes('Rainfall') || limiting.includes('water')) advice.push('Ensure supplemental drip or furrow irrigation during critical crop growth stages.')
  if (limiting.includes('pH')) advice.push('Incorporate agricultural lime or organic compost to normalize soil pH balance.')
  if (limiting.includes('N') || limiting.includes('P') || limiting.includes('K')) advice.push('Apply recommended dosage of NPK fertilizers based on target yield equations.')

  if (advice.length === 0) {
    return `Soil parameters for ${crop.common_name} are well-balanced. Follow standard package of practices recommended by VNMKV/MPKV agricultural universities.`
  }

  return advice.join(' ')
}
