/**
 * SuitabilityMeter — circular gauge component
 * Updated for light theme — visible on white background
 */

const COLORS = {
  high:   { stroke: '#138A4B', text: '#138A4B', label: 'Highly Suitable' },
  medium: { stroke: '#20A65A', text: '#20A65A', label: 'Moderately Suitable' },
  amber:  { stroke: '#D89B18', text: '#D89B18', label: 'Needs Attention' },
  low:    { stroke: '#E07B3A', text: '#E07B3A', label: 'Low Suitability' },
  none:   { stroke: '#D94B4B', text: '#D94B4B', label: 'Not Suitable' },
}

function getColor(score) {
  if (score >= 90) return COLORS.high
  if (score >= 70) return COLORS.medium
  if (score >= 50) return COLORS.amber
  if (score >= 30) return COLORS.low
  return COLORS.none
}

const SIZES = {
  sm:  { r: 20, stroke: 4, size: 52,  fontSize: '0.72rem' },
  md:  { r: 30, stroke: 5, size: 76,  fontSize: '0.95rem' },
  lg:  { r: 44, stroke: 7, size: 108, fontSize: '1.3rem' },
}

export default function SuitabilityMeter({ score = 0, size = 'md', showLabel = false }) {
  const { r, stroke, size: sz, fontSize } = SIZES[size] || SIZES.md
  const color = getColor(score)
  const circumference = 2 * Math.PI * r
  const progress = (score / 100) * circumference
  const center = sz / 2

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative flex-shrink-0" style={{ width: sz, height: sz }}>
        <svg width={sz} height={sz} className="meter-ring">
          {/* Background track */}
          <circle
            cx={center} cy={center} r={r}
            fill="none"
            stroke="#E8EFE9"
            strokeWidth={stroke}
          />
          {/* Progress arc */}
          <circle
            cx={center} cy={center} r={r}
            fill="none"
            stroke={color.stroke}
            strokeWidth={stroke}
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.9s ease-out' }}
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-black animate-score" style={{ fontSize, color: color.text }}>
            {Math.round(score)}
          </span>
        </div>
      </div>
      {showLabel && (
        <span className="text-xs font-semibold" style={{ color: color.text }}>
          {color.label}
        </span>
      )}
    </div>
  )
}
