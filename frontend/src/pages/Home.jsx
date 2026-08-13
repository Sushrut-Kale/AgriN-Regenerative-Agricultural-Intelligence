import { useNavigate } from 'react-router-dom'
import { Leaf, FlaskConical, BarChart3, Zap, ChevronRight, Shield, Sprout, ArrowRight } from 'lucide-react'

export default function Home() {
  const navigate = useNavigate()

  return (
    <div className="hero-bg" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

      {/* ── Navigation ────────────────────────────────────────────── */}
      <nav className="ff-nav px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="ff-logo-icon">
            <Leaf size={18} className="text-white" />
          </div>
          <div>
            <span className="font-bold" style={{ fontSize: '1rem', color: 'var(--ff-text)' }}>FarmFriend AI</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-secondary text-sm"
            style={{ padding: '8px 18px', fontSize: '0.85rem' }}
          >
            Analytics Dashboard
          </button>
        </div>
      </nav>

      {/* ── Hero Section ──────────────────────────────────────────── */}
      <main style={{ flex: 1 }}>
        {/* Badge */}
        <div style={{ textAlign: 'center', paddingTop: 64, paddingBottom: 16 }}>
          <div className="hero-badge" style={{ display: 'inline-flex' }}>
            <span className="pulse-dot" />
            AI-POWERED FARMING ASSISTANT
          </div>
        </div>

        {/* Two-column hero layout */}
        <div className="ff-container" style={{ paddingTop: 20, paddingBottom: 60 }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(0,1.1fr) minmax(0,0.9fr)',
            gap: 48,
            alignItems: 'center',
          }} className="hero-grid">

            {/* LEFT — Text content */}
            <div className="animate-fade-in">
              <h1
                style={{
                  fontSize: 'clamp(2.2rem, 4.5vw, 3.5rem)',
                  fontWeight: 900,
                  lineHeight: 1.12,
                  color: 'var(--ff-text)',
                  marginBottom: 20,
                }}
              >
                Understand Your Soil.{' '}
                <span style={{ color: 'var(--ff-primary)' }}>
                  Choose Your Crop Smarter.
                </span>
              </h1>

              <p style={{
                fontSize: '1.1rem',
                color: 'var(--ff-text-secondary)',
                lineHeight: 1.7,
                marginBottom: 32,
                maxWidth: 480,
              }}>
                Enter your soil-test results and farm conditions. FarmFriend AI analyses 22 crops using ML + agricultural rules and shows you which ones fit your land best.
              </p>

              {/* CTAs */}
              <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginBottom: 20 }}>
                <button
                  id="start-analysis-btn"
                  className="btn-primary"
                  onClick={() => navigate('/farm-details')}
                  style={{ fontSize: '1rem', padding: '14px 32px' }}
                >
                  <Sprout size={20} />
                  Start Soil Analysis
                  <ChevronRight size={18} />
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                  style={{ fontSize: '0.95rem', padding: '13px 24px' }}
                >
                  How It Works
                </button>
              </div>

              <p style={{ fontSize: '0.8rem', color: 'var(--ff-text-muted)' }}>
                No account required · Free · Based on ICAR/TNAU agricultural guidelines
              </p>
            </div>

            {/* RIGHT — Visual hero card */}
            <div className="animate-float" style={{ position: 'relative' }}>
              <div style={{
                background: 'white',
                borderRadius: 28,
                padding: 28,
                boxShadow: '0 20px 60px rgba(20, 50, 30, 0.10)',
                border: '1px solid var(--ff-border)',
                position: 'relative',
                overflow: 'hidden',
              }}>
                {/* Green accent top */}
                <div style={{
                  position: 'absolute', top: 0, left: 0, right: 0, height: 4,
                  background: 'linear-gradient(90deg, #138A4B, #20A65A)',
                }} />

                {/* Mock result display */}
                <div style={{ marginBottom: 20 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                    <div style={{
                      width: 40, height: 40, borderRadius: 10,
                      background: 'var(--ff-light)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <Leaf size={20} style={{ color: 'var(--ff-primary)' }} />
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--ff-text)' }}>Your Soil Analysis</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--ff-text-secondary)' }}>Nashik · Kharif 2025</div>
                    </div>
                    <div style={{ marginLeft: 'auto' }}>
                      <span style={{
                        fontSize: '0.7rem', fontWeight: 600,
                        background: 'var(--ff-light)', color: 'var(--ff-primary)',
                        padding: '4px 10px', borderRadius: 999,
                        border: '1px solid rgba(19,138,75,0.2)',
                      }}>Ready</span>
                    </div>
                  </div>

                  <div style={{ fontSize: '0.8rem', color: 'var(--ff-text-secondary)', marginBottom: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Top Crop Recommendations
                  </div>

                  {[
                    { name: 'Soybean', local: 'सोयाबीन', score: 92, color: '#138A4B' },
                    { name: 'Cotton',  local: 'कपास',    score: 78, color: '#20A65A' },
                    { name: 'Maize',   local: 'मक्का',   score: 65, color: '#D89B18' },
                  ].map((crop, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'center', gap: 12,
                      padding: '10px 12px',
                      background: i === 0 ? 'var(--ff-soft)' : 'transparent',
                      borderRadius: 10, marginBottom: 6,
                      border: i === 0 ? '1px solid rgba(19,138,75,0.15)' : 'none',
                    }}>
                      <div style={{
                        width: 28, height: 28, borderRadius: 6,
                        background: i === 0 ? 'var(--ff-light)' : '#F1F4F2',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.9rem', fontWeight: 700, color: crop.color,
                      }}>#{i + 1}</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--ff-text)' }}>{crop.name} <span style={{ color: 'var(--ff-text-muted)', fontWeight: 400, fontSize: '0.75rem' }}>({crop.local})</span></div>
                        <div style={{ height: 5, borderRadius: 3, background: '#E8EFE9', marginTop: 4 }}>
                          <div style={{ width: `${crop.score}%`, height: '100%', borderRadius: 3, background: crop.color }} />
                        </div>
                      </div>
                      <div style={{ fontWeight: 800, fontSize: '0.9rem', color: crop.color }}>{crop.score}</div>
                    </div>
                  ))}
                </div>

                <div style={{
                  background: 'var(--ff-soft)',
                  borderRadius: 12, padding: '10px 14px',
                  border: '1px solid rgba(19,138,75,0.12)',
                }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--ff-primary)', fontWeight: 600, marginBottom: 3 }}>
                    ✦ FarmFriend AI Explains
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--ff-text-secondary)', lineHeight: 1.5 }}>
                    Soybean is highly suitable for your soil. Nitrogen and pH are in the optimal range.
                  </div>
                </div>
              </div>

              {/* Floating decorative elements */}
              <div style={{
                position: 'absolute', top: -14, right: -14,
                width: 52, height: 52, borderRadius: 14,
                background: 'linear-gradient(135deg, #138A4B, #20A65A)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 16px rgba(19,138,75,0.35)',
              }}>
                <span style={{ fontSize: 24 }}>🌱</span>
              </div>
              <div style={{
                position: 'absolute', bottom: -10, left: -14,
                width: 44, height: 44, borderRadius: 12,
                background: 'var(--ff-warning-bg)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(216,155,24,0.2)',
                border: '1px solid rgba(216,155,24,0.2)',
              }}>
                <span style={{ fontSize: 20 }}>🧪</span>
              </div>
            </div>
          </div>
        </div>

        {/* ── Feature Cards ──────────────────────────────────────────── */}
        <div style={{ background: 'white', borderTop: '1px solid var(--ff-border)', paddingTop: 64, paddingBottom: 64 }}>
          <div className="ff-container">
            <div style={{ textAlign: 'center', marginBottom: 40 }}>
              <h2 style={{ fontSize: '1.7rem', fontWeight: 800, color: 'var(--ff-text)', marginBottom: 10 }}>
                Everything You Need to Make Better Crop Decisions
              </h2>
              <p style={{ color: 'var(--ff-text-secondary)', fontSize: '1rem', maxWidth: 520, margin: '0 auto' }}>
                Built on ICAR/TNAU agricultural science, powered by machine learning.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }} className="feature-grid">
              <FeatureCard
                emoji="🌱"
                icon={<FlaskConical size={22} style={{ color: 'var(--ff-primary)' }} />}
                title="12 Soil Parameters"
                desc="Enter all Soil Health Card values — Macronutrients, micronutrients, pH, EC, Organic Carbon."
                accent="var(--ff-primary)"
                bg="var(--ff-soft)"
              />
              <FeatureCard
                emoji="🤖"
                icon={<BarChart3 size={22} style={{ color: 'var(--ff-info)' }} />}
                title="ML + Rule Engine"
                desc="92.6% accuracy Logistic Regression model combined with ICAR/TNAU agricultural rules."
                accent="var(--ff-info)"
                bg="#EDF4FF"
              />
              <FeatureCard
                emoji="⚡"
                icon={<Zap size={22} style={{ color: 'var(--ff-warning)' }} />}
                title="What-If Simulator"
                desc="Change any condition and instantly see how crop suitability scores respond."
                accent="var(--ff-warning)"
                bg="var(--ff-warning-bg)"
              />
            </div>
          </div>
        </div>

        {/* ── How It Works ───────────────────────────────────────────── */}
        <div id="how-it-works" style={{ paddingTop: 64, paddingBottom: 64 }}>
          <div className="ff-container">
            <div style={{ textAlign: 'center', marginBottom: 48 }}>
              <h2 style={{ fontSize: '1.7rem', fontWeight: 800, color: 'var(--ff-text)', marginBottom: 10 }}>
                How It Works
              </h2>
              <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.95rem' }}>
                Four simple steps from soil data to crop decisions
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 0, justifyContent: 'center', flexWrap: 'wrap', gap: 12 }}>
              {[
                { step: 1, label: 'Farm Details',       desc: 'Location, season, soil type, irrigation', emoji: '📍' },
                { step: 2, label: 'Soil Test Values',   desc: 'Enter 12 Soil Health Card parameters',     emoji: '🧪' },
                { step: 3, label: 'AI Analysis',        desc: 'ML model + agricultural rules engine',      emoji: '🤖' },
                { step: 4, label: 'Explore Results',    desc: 'Rankings, feasibility + what-if',           emoji: '📊' },
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div
                    className="ff-card"
                    style={{ width: 170, textAlign: 'center', padding: '20px 16px' }}
                  >
                    <div style={{
                      width: 48, height: 48, borderRadius: 14,
                      background: 'var(--ff-soft)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      margin: '0 auto 12px',
                      border: '1px solid rgba(19,138,75,0.15)',
                    }}>
                      <span style={{ fontSize: 22 }}>{item.emoji}</span>
                    </div>
                    <div style={{
                      width: 22, height: 22, borderRadius: '50%',
                      background: 'var(--ff-primary)',
                      color: 'white',
                      fontSize: '0.7rem', fontWeight: 700,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      margin: '0 auto 8px',
                    }}>
                      {item.step}
                    </div>
                    <p style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--ff-text)', marginBottom: 4 }}>{item.label}</p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--ff-text-secondary)', lineHeight: 1.4 }}>{item.desc}</p>
                  </div>
                  {i < 3 && (
                    <ArrowRight size={20} style={{ color: 'var(--ff-primary)', opacity: 0.5, flexShrink: 0 }} />
                  )}
                </div>
              ))}
            </div>

            <div style={{ textAlign: 'center', marginTop: 40 }}>
              <button
                className="btn-primary"
                onClick={() => navigate('/farm-details')}
                style={{ fontSize: '1rem', padding: '14px 36px' }}
              >
                <Sprout size={20} />
                Get Started — It's Free
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* ── Footer ──────────────────────────────────────────────────── */}
      <footer style={{
        borderTop: '1px solid var(--ff-border)',
        padding: '20px 24px',
        background: 'white',
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center', justifyContent: 'center' }}>
          <Shield size={13} style={{ color: 'var(--ff-text-muted)' }} />
          <span style={{ fontSize: '0.78rem', color: 'var(--ff-text-muted)', textAlign: 'center' }}>
            FarmFriend AI provides data-driven decision support. It does not replace professional agricultural advice or local Krishi Vigyan Kendra (KVK) recommendations.
          </span>
        </div>
        <p style={{ textAlign: 'center', fontSize: '0.72rem', color: '#C0CCC4', marginTop: 6 }}>
          ML Model: Logistic Regression · Accuracy: 92.6% · F1: 0.924 · Trained on ICAR/TNAU/FAO sourced data · Maharashtra pilot
        </p>
      </footer>

      {/* ── Responsive styles ────────────────────────────────────────── */}
      <style>{`
        @media (max-width: 768px) {
          .hero-grid { grid-template-columns: 1fr !important; }
          .feature-grid { grid-template-columns: 1fr !important; }
        }
        @media (max-width: 640px) {
          .feature-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  )
}

function FeatureCard({ emoji, icon, title, desc, accent, bg }) {
  return (
    <div className="ff-card" style={{ padding: 24, borderTop: `3px solid ${accent}`, transition: 'transform 0.2s ease, box-shadow 0.2s ease' }}
      onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 12px 40px rgba(20,50,30,0.12)'; }}
      onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}
    >
      <div style={{
        width: 44, height: 44, borderRadius: 12,
        background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center',
        marginBottom: 14, border: `1px solid ${accent}22`,
      }}>
        {icon}
      </div>
      <h3 style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--ff-text)', marginBottom: 8 }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.875rem', color: 'var(--ff-text-secondary)', lineHeight: 1.6 }}>
        {desc}
      </p>
    </div>
  )
}
