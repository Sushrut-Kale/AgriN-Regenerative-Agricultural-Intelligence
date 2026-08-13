/**
 * FactorBadges — displays factor lists with colour-coded status
 * Updated for light theme
 */
export default function FactorBadges({ factors = [], maxVisible = 4 }) {
  const visible = factors.slice(0, maxVisible)
  const rest = factors.length - maxVisible

  const styleMap = {
    suitable: {
      bg: '#EAF8EF',
      color: '#138A4B',
      border: 'rgba(19,138,75,0.25)',
    },
    moderate: {
      bg: '#FFF7E1',
      color: '#D89B18',
      border: 'rgba(216,155,24,0.3)',
    },
    limiting: {
      bg: '#FFF0F0',
      color: '#D94B4B',
      border: 'rgba(217,75,75,0.25)',
    },
    missing: {
      bg: '#F1F4F2',
      color: '#9BAA9E',
      border: '#E2E9E4',
    },
  }

  const iconMap = {
    suitable: '✓',
    moderate: '⚠',
    limiting: '✗',
    missing:  '?',
  }

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
      {visible.map((f, i) => {
        const s = styleMap[f.status] || styleMap.missing
        return (
          <span
            key={i}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 4,
              fontSize: '0.75rem',
              padding: '3px 10px',
              borderRadius: 9999,
              background: s.bg,
              color: s.color,
              border: `1px solid ${s.border}`,
              fontWeight: 500,
            }}
          >
            {iconMap[f.status] || '?'} {f.factor}
          </span>
        )
      })}
      {rest > 0 && (
        <span style={{ fontSize: '0.75rem', color: 'var(--ff-text-muted)', alignSelf: 'center' }}>
          +{rest} more
        </span>
      )}
    </div>
  )
}
