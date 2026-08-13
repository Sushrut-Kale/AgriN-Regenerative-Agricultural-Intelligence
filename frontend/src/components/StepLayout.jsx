/**
 * StepLayout — shared layout for multi-step form pages
 * Light theme with visible step progress indicator
 */
import { useNavigate } from 'react-router-dom'
import { Leaf } from 'lucide-react'

const STEPS = [
  { num: 1, label: 'Farm Details' },
  { num: 2, label: 'Soil Test' },
  { num: 3, label: 'Environment' },
  { num: 4, label: 'Analysis' },
]

export default function StepLayout({ step, title, subtitle, children }) {
  const navigate = useNavigate()

  return (
    <div className="page-bg flex flex-col" style={{ minHeight: '100vh' }}>
      {/* Top Navigation Bar */}
      <div className="ff-nav sticky top-0 z-10 px-6 py-3 flex items-center gap-4">
        {/* Logo */}
        <div
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => navigate('/')}
        >
          <div className="ff-logo-icon">
            <Leaf size={17} className="text-white" />
          </div>
          <span className="font-bold text-ff-text hidden sm:block" style={{ fontSize: '0.95rem', color: 'var(--ff-text)' }}>
            FarmFriend AI
          </span>
        </div>

        {/* Step Progress Indicator */}
        <div className="flex items-center gap-0 mx-auto">
          {STEPS.map((s, i) => (
            <div key={s.num} className="flex items-center">
              <div className="flex flex-col items-center" style={{ minWidth: 60 }}>
                <div className={`step-circle ${step === s.num ? 'active' : step > s.num ? 'completed' : ''}`}>
                  {step > s.num ? '✓' : s.num}
                </div>
                <span
                  className="step-label mt-1 hidden sm:block text-center"
                  style={{ ...(step === s.num ? { color: 'var(--ff-primary)', fontWeight: 600 } : {}) }}
                >
                  {s.label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div
                  className="step-connector hidden sm:block"
                  style={{ ...(step > s.num + 1 || (step === s.num + 1) ? { background: 'var(--ff-primary)' } : {}) }}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step label (mobile) */}
        <div className="text-xs sm:hidden" style={{ color: 'var(--ff-text-secondary)', whiteSpace: 'nowrap' }}>
          {step}/{STEPS.length}
        </div>
      </div>

      {/* Page Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="ff-container-narrow py-8">
          {/* Page Header */}
          <div className="mb-7">
            <h1 className="font-bold" style={{ fontSize: '1.6rem', color: 'var(--ff-text)' }}>
              {title}
            </h1>
            {subtitle && (
              <p className="mt-1" style={{ fontSize: '0.9rem', color: 'var(--ff-text-secondary)' }}>
                {subtitle}
              </p>
            )}
          </div>

          {children}
        </div>
      </div>
    </div>
  )
}
