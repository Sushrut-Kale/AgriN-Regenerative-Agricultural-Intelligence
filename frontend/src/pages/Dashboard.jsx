import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getAnalytics, getModelInfo } from '../services/api'
import { ArrowLeft, BarChart2, BookOpen, Layers, TrendingUp, Sprout, Zap } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function Dashboard() {
  const navigate = useNavigate()
  const [analytics, setAnalytics] = useState(null)
  const [modelInfo, setModelInfo] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getAnalytics(), getModelInfo()])
      .then(([a, m]) => { setAnalytics(a); setModelInfo(m.model_info) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="page-bg" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div className="loader" style={{ margin: '0 auto 16px' }} />
        <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.9rem' }}>Loading analytics...</p>
      </div>
    </div>
  )

  const scoreData = analytics?.score_distribution
    ? Object.entries(analytics.score_distribution).map(([range, count]) => ({ range, count }))
    : []

  const allModels = modelInfo?.all_models || []

  const metrics = [
    { label: 'Analyses Run',         value: analytics?.total_analyses || 0,           icon: <BarChart2 size={22} />, color: 'var(--ff-primary)', bg: 'var(--ff-soft)' },
    { label: 'Feasibility Checks',   value: analytics?.total_feasibility_checks || 0,  icon: <Sprout size={22} />,   color: '#3978B8',           bg: '#EDF4FF' },
    { label: 'What-If Simulations',  value: analytics?.total_whatif_runs || 0,         icon: <Zap size={22} />,      color: '#D89B18',           bg: '#FFF7E1' },
  ]

  return (
    <div className="page-bg" style={{ minHeight: '100vh' }}>

      {/* ── Top bar ───────────────────────────────────────────── */}
      <div className="ff-nav px-6 py-4 flex items-center gap-3" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
        <button
          onClick={() => navigate('/')}
          style={{
            background: 'var(--ff-soft)', border: '1px solid var(--ff-border)',
            borderRadius: 10, padding: '6px 10px', cursor: 'pointer',
            display: 'flex', alignItems: 'center', color: 'var(--ff-text-secondary)',
          }}
        >
          <ArrowLeft size={18} />
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <BarChart2 size={20} style={{ color: 'var(--ff-primary)' }} />
          <h1 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--ff-text)' }}>Analytics Dashboard</h1>
        </div>
      </div>

      <div className="ff-container" style={{ paddingTop: 28, paddingBottom: 48 }}>

        {/* ── Usage stats ───────────────────────────────────────── */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 24 }} className="metrics-grid">
          {metrics.map(m => (
            <div key={m.label} className="metric-card" style={{ textAlign: 'center' }}>
              <div style={{
                width: 50, height: 50, borderRadius: 14,
                background: m.bg, display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 12px', color: m.color,
              }}>
                {m.icon}
              </div>
              <div style={{ fontSize: '2.4rem', fontWeight: 900, color: 'var(--ff-text)', lineHeight: 1 }}>{m.value}</div>
              <div style={{ fontSize: '0.82rem', color: 'var(--ff-text-secondary)', marginTop: 6 }}>{m.label}</div>
            </div>
          ))}
        </div>

        {/* ── ML Model performance ──────────────────────────────── */}
        {modelInfo && (
          <div className="ff-card" style={{ padding: 24, marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
              <BookOpen size={18} style={{ color: 'var(--ff-primary)' }} />
              <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--ff-text)' }}>ML Model Performance</h2>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--ff-text-muted)', marginBottom: 20 }}>
              {modelInfo.model_type} · Trained: {modelInfo.training_date?.split('T')[0]} ·
              {modelInfo.n_classes} crops · Synthetic/augmented dataset (ICAR/TNAU sourced)
            </p>

            {/* Key metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }} className="model-metrics-grid">
              {[
                { label: 'Accuracy',  value: `${((modelInfo.metrics?.accuracy || 0) * 100).toFixed(1)}%`,       color: 'var(--ff-primary)', bg: 'var(--ff-soft)' },
                { label: 'Precision', value: `${((modelInfo.metrics?.precision_weighted || 0) * 100).toFixed(1)}%`, color: '#3978B8',           bg: '#EDF4FF' },
                { label: 'Recall',    value: `${((modelInfo.metrics?.recall_weighted || 0) * 100).toFixed(1)}%`,  color: '#7C3AED',           bg: '#F5F0FF' },
                { label: 'F1-Score',  value: (modelInfo.metrics?.f1_weighted || 0).toFixed(3),                    color: '#D89B18',           bg: '#FFF7E1' },
              ].map(m => (
                <div key={m.label} style={{
                  background: m.bg, borderRadius: 14, padding: '16px 12px', textAlign: 'center',
                  border: `1px solid ${m.color}22`,
                }}>
                  <div style={{ fontSize: '1.6rem', fontWeight: 900, color: m.color, lineHeight: 1 }}>{m.value}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--ff-text-secondary)', marginTop: 6 }}>{m.label}</div>
                </div>
              ))}
            </div>

            {/* Model comparison bars */}
            {allModels.length > 0 && (
              <div>
                <h3 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--ff-text-secondary)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <TrendingUp size={14} /> Model Comparison (Training Run)
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {allModels.map(m => {
                    const score = m.f1_weighted ?? m.f1 ?? m.accuracy ?? 0
                    return (
                      <div key={m.name} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{ width: 140, fontSize: '0.78rem', color: 'var(--ff-text-secondary)', textAlign: 'right', flexShrink: 0 }}>
                          {m.name}
                        </div>
                        <div className="score-bar" style={{ flex: 1 }}>
                          <div
                            className="score-bar-fill"
                            style={{
                              width: `${score * 100}%`,
                              background: score >= 0.78 ? 'var(--ff-primary)' : score >= 0.70 ? 'var(--ff-warning)' : '#C0CCC4',
                            }}
                          />
                        </div>
                        <div style={{ width: 52, fontSize: '0.78rem', textAlign: 'right', fontWeight: 700, color: 'var(--ff-text)', flexShrink: 0 }}>
                          {(score * 100).toFixed(1)}%
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Score distribution chart ──────────────────────────── */}
        {scoreData.some(d => d.count > 0) && (
          <div className="ff-card" style={{ padding: 24, marginBottom: 20 }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--ff-text)', marginBottom: 20 }}>
              📊 Score Distribution
            </h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={scoreData} barSize={32}>
                <XAxis dataKey="range" tick={{ fill: 'var(--ff-text-secondary)', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--ff-text-secondary)', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: 'white', border: '1px solid var(--ff-border)',
                    borderRadius: 10, fontSize: '0.85rem', color: 'var(--ff-text)',
                    boxShadow: '0 4px 20px rgba(20,50,30,0.10)',
                  }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {scoreData.map((entry, i) => (
                    <Cell key={i} fill="var(--ff-primary)" opacity={0.75 + (i / scoreData.length) * 0.25} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* ── System architecture ───────────────────────────────── */}
        <div className="ff-card" style={{ padding: 24, marginBottom: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
            <Layers size={18} style={{ color: '#3978B8' }} />
            <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--ff-text)' }}>System Architecture</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }} className="arch-grid">
            {[
              {
                title: 'ML Layer (60%)', color: 'var(--ff-primary)', bg: 'var(--ff-soft)',
                items: ['Logistic Regression', '92.6% accuracy', '22 crops', '7 features', 'Synthetic/augmented training data'],
              },
              {
                title: 'Rule Layer (40%)', color: '#3978B8', bg: '#EDF4FF',
                items: ['ICAR/TNAU thresholds', '12 SHC parameters', 'pH, NPK, micronutrients', 'Temperature & rainfall', 'Season/soil/irrigation'],
              },
              {
                title: 'NLG Explainer', color: '#7C3AED', bg: '#F5F0FF',
                items: ['Rule-based templates', 'No external LLM API', 'Grounded in model outputs', 'Farmer-friendly language', 'Always includes disclaimer'],
              },
            ].map(col => (
              <div key={col.title} style={{ background: col.bg, borderRadius: 14, padding: 18, border: `1px solid ${col.color}20` }}>
                <h3 style={{ fontWeight: 700, fontSize: '0.85rem', color: col.color, marginBottom: 10 }}>{col.title}</h3>
                <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {col.items.map(item => (
                    <li key={item} style={{ fontSize: '0.8rem', color: 'var(--ff-text-secondary)', display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                      <span style={{ color: col.color, flexShrink: 0, marginTop: 2 }}>•</span> {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <p style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--ff-text-muted)' }}>
          FarmFriend AI · Maharashtra Pilot · ML model trained on synthetic/augmented data (ICAR/TNAU/FAO sourced) · Results are decision support estimates only
        </p>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .metrics-grid { grid-template-columns: 1fr !important; }
          .model-metrics-grid { grid-template-columns: repeat(2, 1fr) !important; }
          .arch-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  )
}
