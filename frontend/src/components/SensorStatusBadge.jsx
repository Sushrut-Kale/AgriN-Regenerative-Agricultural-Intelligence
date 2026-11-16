/**
 * SensorStatusBadge — reusable data-source / quality pill
 * Props:
 *   source  — 'SENSOR_MEASURED' | 'SYNTHETIC' | 'EXTERNAL' | 'UNAVAILABLE' | 'ESTIMATED'
 *   quality — 'GOOD' | 'DEGRADED' | 'INVALID'
 */
export default function SensorStatusBadge({ source, quality }) {
  const sourceConfig = {
    SENSOR_MEASURED: {
      label: 'LIVE SENSOR',
      dot: '🟢',
      color: '#065F46',
      bg: '#D1FAE5',
      border: '#6EE7B7',
    },
    ESTIMATED: {
      label: 'ESTIMATED',
      dot: '🟡',
      color: '#78350F',
      bg: '#FEF3C7',
      border: '#FCD34D',
    },
    EXTERNAL: {
      label: 'EXTERNAL',
      dot: '🔵',
      color: '#1E3A8A',
      bg: '#DBEAFE',
      border: '#93C5FD',
    },
    UNAVAILABLE: {
      label: 'UNAVAILABLE',
      dot: '🔴',
      color: '#7F1D1D',
      bg: '#FEE2E2',
      border: '#FCA5A5',
    },
    SYNTHETIC: {
      label: 'SYNTHETIC',
      dot: '🟣',
      color: '#4C1D95',
      bg: '#EDE9FE',
      border: '#C4B5FD',
    },
  }

  const qualityConfig = {
    GOOD: { label: 'GOOD', color: '#065F46' },
    DEGRADED: { label: 'DEGRADED', color: '#92400E' },
    INVALID: { label: 'INVALID', color: '#7F1D1D' },
  }

  const src = sourceConfig[source] || sourceConfig.UNAVAILABLE
  const qual = qualityConfig[quality] || qualityConfig.GOOD

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
      {/* Source pill */}
      <span style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 4,
        padding: '2px 8px',
        borderRadius: 999,
        fontSize: '0.68rem',
        fontWeight: 700,
        letterSpacing: '0.04em',
        background: src.bg,
        color: src.color,
        border: `1px solid ${src.border}`,
        userSelect: 'none',
      }}>
        <span style={{ fontSize: '0.6rem' }}>{src.dot}</span>
        {src.label}
      </span>

      {/* Quality pill (shown only when degraded/invalid) */}
      {quality && quality !== 'GOOD' && (
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          padding: '2px 7px',
          borderRadius: 999,
          fontSize: '0.65rem',
          fontWeight: 700,
          letterSpacing: '0.04em',
          background: '#FFF7ED',
          color: qual.color,
          border: `1px solid ${qual.color}44`,
          userSelect: 'none',
        }}>
          {qual.label}
        </span>
      )}
    </span>
  )
}
