import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Wifi, WifiOff, AlertTriangle, Battery, BatteryLow,
  Thermometer, Droplets, FlaskConical, Zap, Leaf, RefreshCw,
  Signal, Clock, Cpu, Radio
} from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'
import SensorStatusBadge from '../components/SensorStatusBadge'
import { getDeviceStatus, getLatestTelemetry, getTelemetryHistory } from '../services/api'

// ── Demo seed data (used when API is unreachable or returns no data) ──────────
const DEMO_DEVICE = {
  device_id: 'agrisense-001',
  name: 'AgriSense-001',
  status: 'ONLINE',
  firmware_version: 'v2.3.1',
  battery_voltage: 3.84,
  battery_percent: 78,
  signal_rssi: -62,
  signal_quality: 'GOOD',
  last_seen_at: new Date(Date.now() - 4 * 60 * 1000).toISOString(),
}

const DEMO_MEASUREMENTS = [
  {
    sensor_type: 'SOIL_MOISTURE',
    parameter_name: 'Soil Moisture',
    calibrated_value: 42.3,
    unit: '%',
    data_source: 'SYNTHETIC',
    quality: 'GOOD',
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
  },
  {
    sensor_type: 'SOIL_TEMP',
    parameter_name: 'Soil Temperature',
    calibrated_value: 28.7,
    unit: '°C',
    data_source: 'SYNTHETIC',
    quality: 'GOOD',
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
  },
  {
    sensor_type: 'SOIL_PH',
    parameter_name: 'Soil pH',
    calibrated_value: 6.8,
    unit: 'pH',
    data_source: 'SYNTHETIC',
    quality: 'GOOD',
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
  },
  {
    sensor_type: 'SOIL_EC',
    parameter_name: 'Electrical Conductivity',
    calibrated_value: 0.42,
    unit: 'dS/m',
    data_source: 'SYNTHETIC',
    quality: 'DEGRADED',
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
  },
  {
    sensor_type: 'NITROGEN',
    parameter_name: 'Nitrogen (N)',
    calibrated_value: 185,
    unit: 'kg/ha',
    data_source: 'ESTIMATED',
    quality: 'GOOD',
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
  },
  {
    sensor_type: 'PHOSPHORUS',
    parameter_name: 'Phosphorus (P)',
    calibrated_value: 22,
    unit: 'kg/ha',
    data_source: 'ESTIMATED',
    quality: 'GOOD',
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
  },
  {
    sensor_type: 'POTASSIUM',
    parameter_name: 'Potassium (K)',
    calibrated_value: 148,
    unit: 'kg/ha',
    data_source: 'ESTIMATED',
    quality: 'GOOD',
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
  },
]

// Generate 24h demo trend for soil moisture
function generateMoistureTrend() {
  const data = []
  const now = Date.now()
  for (let i = 23; i >= 0; i--) {
    const t = new Date(now - i * 60 * 60 * 1000)
    data.push({
      time: t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      moisture: +(38 + Math.sin(i * 0.4) * 8 + Math.random() * 3).toFixed(1),
    })
  }
  return data
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function minutesAgo(isoStr) {
  if (!isoStr) return 'unknown'
  const diff = Math.floor((Date.now() - new Date(isoStr).getTime()) / 60000)
  if (diff < 1) return 'just now'
  if (diff === 1) return '1 minute ago'
  if (diff < 60) return `${diff} minutes ago`
  const h = Math.floor(diff / 60)
  return `${h} hour${h > 1 ? 's' : ''} ago`
}

function sensorIcon(type) {
  const map = {
    SOIL_MOISTURE: <Droplets size={18} />,
    SOIL_TEMP: <Thermometer size={18} />,
    SOIL_PH: <FlaskConical size={18} />,
    SOIL_EC: <Zap size={18} />,
    NITROGEN: <Leaf size={18} />,
    PHOSPHORUS: <Leaf size={18} />,
    POTASSIUM: <Leaf size={18} />,
    AMBIENT_TEMP: <Thermometer size={18} />,
    AMBIENT_HUMIDITY: <Droplets size={18} />,
  }
  return map[type] || <Cpu size={18} />
}

function signalBars(rssi) {
  // -50 dBm excellent, -70 good, -85 fair, worse poor
  if (rssi >= -55) return 4
  if (rssi >= -70) return 3
  if (rssi >= -85) return 2
  return 1
}

function SignalBarsIcon({ rssi }) {
  const bars = signalBars(rssi)
  return (
    <span style={{ display: 'inline-flex', alignItems: 'flex-end', gap: 2, height: 16 }}>
      {[1, 2, 3, 4].map(b => (
        <span key={b} style={{
          width: 4,
          height: 4 + b * 3,
          borderRadius: 2,
          background: b <= bars ? (bars >= 3 ? '#10B981' : bars === 2 ? '#F59E0B' : '#EF4444') : '#E5E7EB',
          display: 'inline-block',
        }} />
      ))}
    </span>
  )
}

function StatusPill({ status }) {
  const cfg = {
    ONLINE: { color: '#065F46', bg: '#D1FAE5', border: '#6EE7B7', label: 'ONLINE', pulse: true },
    OFFLINE: { color: '#6B7280', bg: '#F3F4F6', border: '#D1D5DB', label: 'OFFLINE', pulse: false },
    DEGRADED: { color: '#78350F', bg: '#FEF3C7', border: '#FCD34D', label: 'DEGRADED', pulse: false },
    UNREGISTERED: { color: '#374151', bg: '#F9FAFB', border: '#E5E7EB', label: 'UNREGISTERED', pulse: false },
  }
  const c = cfg[status] || cfg.OFFLINE
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '4px 12px', borderRadius: 999, fontWeight: 700, fontSize: '0.75rem',
      letterSpacing: '0.05em', background: c.bg, color: c.color, border: `1px solid ${c.border}`,
    }}>
      {c.pulse ? (
        <span style={{
          width: 7, height: 7, borderRadius: '50%', background: c.color,
          boxShadow: `0 0 0 0 ${c.color}66`,
          animation: 'pulse-ring 1.6s ease-in-out infinite',
          display: 'inline-block',
        }} />
      ) : (
        <span style={{ width: 7, height: 7, borderRadius: '50%', background: c.color, display: 'inline-block' }} />
      )}
      {c.label}
    </span>
  )
}

function BatteryBar({ percent, voltage }) {
  const color = percent >= 60 ? '#10B981' : percent >= 30 ? '#F59E0B' : '#EF4444'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{ position: 'relative', width: 32, height: 16 }}>
        {/* battery body */}
        <div style={{
          width: 28, height: 16, border: `2px solid ${color}`,
          borderRadius: 4, overflow: 'hidden', position: 'relative',
        }}>
          <div style={{
            position: 'absolute', left: 0, top: 0, bottom: 0,
            width: `${percent}%`, background: color,
            transition: 'width 0.5s ease',
          }} />
        </div>
        {/* battery cap */}
        <div style={{
          position: 'absolute', right: -4, top: '25%', width: 4, height: '50%',
          background: color, borderRadius: '0 2px 2px 0',
        }} />
      </div>
      <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--ff-text)' }}>
        {percent}%
      </span>
      <span style={{ fontSize: '0.75rem', color: 'var(--ff-text-muted)' }}>
        ({voltage?.toFixed(2)}V)
      </span>
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────
export default function DeviceMonitor() {
  const navigate = useNavigate()
  const [selectedDevice] = useState('agrisense-001')
  const [device, setDevice] = useState(null)
  const [measurements, setMeasurements] = useState([])
  const [trendData, setTrendData] = useState(generateMoistureTrend())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastRefresh, setLastRefresh] = useState(new Date())
  const [isDemo, setIsDemo] = useState(false)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [deviceRes, telemetryRes] = await Promise.all([
        getDeviceStatus(selectedDevice),
        getLatestTelemetry(selectedDevice),
      ])
      setDevice(deviceRes)
      setMeasurements(telemetryRes?.measurements || [])
      setIsDemo(false)

      // Also try history for chart
      try {
        const histRes = await getTelemetryHistory(selectedDevice, { hours: 24, limit: 24 })
        if (histRes?.records?.length > 0) {
          const trend = histRes.records.map(r => ({
            time: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            moisture: r.measurements?.find(m => m.sensor_type === 'SOIL_MOISTURE')?.calibrated_value ?? null,
          })).filter(d => d.moisture !== null)
          if (trend.length > 0) setTrendData(trend)
        }
      } catch (_) { /* chart stays on demo data */ }

    } catch (_) {
      // API not yet available — fall back to demo data
      setDevice(DEMO_DEVICE)
      setMeasurements(DEMO_MEASUREMENTS)
      setIsDemo(true)
    } finally {
      setLoading(false)
      setLastRefresh(new Date())
    }
  }, [selectedDevice])

  useEffect(() => { fetchData() }, [fetchData])

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(fetchData, 30_000)
    return () => clearInterval(interval)
  }, [fetchData])

  const hasSynthetic = measurements.some(m => m.data_source === 'SYNTHETIC')

  if (loading && !device) return (
    <div className="page-bg" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div className="loader" style={{ margin: '0 auto 16px' }} />
        <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.9rem' }}>Connecting to device…</p>
      </div>
    </div>
  )

  return (
    <div className="page-bg" style={{ minHeight: '100vh' }}>

      {/* ── Top Bar ─────────────────────────────────────────────────────── */}
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
          <Radio size={20} style={{ color: 'var(--ff-primary)' }} />
          <h1 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--ff-text)' }}>Live Sensor Monitor</h1>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--ff-text-muted)' }}>
            Refreshed {minutesAgo(lastRefresh.toISOString())}
          </span>
          <button
            onClick={fetchData}
            style={{
              background: 'var(--ff-soft)', border: '1px solid var(--ff-border)',
              borderRadius: 8, padding: '5px 10px', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 5,
              color: 'var(--ff-text-secondary)', fontSize: '0.78rem',
            }}
          >
            <RefreshCw size={14} style={loading ? { animation: 'spin 1s linear infinite' } : {}} />
            Refresh
          </button>
          <button
            onClick={() => navigate('/devices/register')}
            style={{
              background: 'var(--ff-primary)', color: 'white', border: 'none',
              borderRadius: 8, padding: '6px 14px', cursor: 'pointer',
              fontSize: '0.8rem', fontWeight: 600,
            }}
          >
            + Register Device
          </button>
        </div>
      </div>

      <div className="ff-container" style={{ paddingTop: 24, paddingBottom: 48 }}>

        {/* ── SIMULATION MODE banner ─────────────────────────────────────── */}
        {(hasSynthetic || isDemo) && (
          <div style={{
            background: '#FFF7ED',
            border: '2px solid #F59E0B',
            borderRadius: 12,
            padding: '14px 20px',
            marginBottom: 20,
            display: 'flex',
            alignItems: 'center',
            gap: 12,
          }}>
            <AlertTriangle size={22} style={{ color: '#D97706', flexShrink: 0 }} />
            <div>
              <div style={{ fontWeight: 700, color: '#78350F', fontSize: '0.9rem', marginBottom: 2 }}>
                ⚠️ SIMULATION MODE — These are not real sensor readings
              </div>
              <div style={{ fontSize: '0.78rem', color: '#92400E', lineHeight: 1.5 }}>
                {isDemo
                  ? 'The IoT backend API is not reachable. Showing demo data. Deploy the backend and register a real AgriSense device to see live readings.'
                  : 'Some or all measurements are marked SYNTHETIC — generated by the backend in simulation mode, not from physical sensors.'}
              </div>
            </div>
          </div>
        )}

        {/* ── Device Selector + Status ───────────────────────────────────── */}
        <div className="ff-card" style={{ padding: 24, marginBottom: 20 }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, alignItems: 'flex-start', justifyContent: 'space-between' }}>

            {/* Device selector */}
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--ff-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: 6 }}>
                Active Device
              </label>
              <select
                value={selectedDevice}
                onChange={() => {}}
                style={{
                  padding: '8px 12px', borderRadius: 8, border: '1px solid var(--ff-border)',
                  fontSize: '0.9rem', fontWeight: 600, color: 'var(--ff-text)',
                  background: 'white', cursor: 'pointer', minWidth: 200,
                }}
              >
                <option value="agrisense-001">AgriSense-001</option>
              </select>
              <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', marginTop: 4 }}>
                Multi-device selector coming soon
              </div>
            </div>

            {/* Status + diagnostics */}
            {device && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', marginBottom: 4 }}>Connection</div>
                  <StatusPill status={device.status} />
                </div>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', marginBottom: 4 }}>Battery</div>
                  <BatteryBar percent={device.battery_percent ?? 78} voltage={device.battery_voltage ?? 3.84} />
                </div>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', marginBottom: 4 }}>Signal</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <SignalBarsIcon rssi={device.signal_rssi ?? -62} />
                    <span style={{ fontSize: '0.8rem', color: 'var(--ff-text)', fontWeight: 600 }}>
                      {device.signal_rssi ?? -62} dBm
                    </span>
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', marginBottom: 4 }}>Last Seen</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <Clock size={13} style={{ color: 'var(--ff-text-muted)' }} />
                    <span style={{ fontSize: '0.8rem', color: 'var(--ff-text)' }}>
                      {minutesAgo(device.last_seen_at)}
                    </span>
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)', marginBottom: 4 }}>Firmware</div>
                  <span style={{
                    fontSize: '0.78rem', fontWeight: 600, fontFamily: 'monospace',
                    color: 'var(--ff-text)', background: 'var(--ff-soft)',
                    padding: '2px 8px', borderRadius: 6,
                  }}>
                    {device.firmware_version ?? 'v?.?.?'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ── Sensor Measurement Cards ────────────────────────────────────── */}
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--ff-text)', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Cpu size={16} style={{ color: 'var(--ff-primary)' }} />
            Sensor Readings
          </h2>

          {measurements.length === 0 ? (
            <div style={{ padding: '32px', textAlign: 'center', background: 'white', borderRadius: 14, border: '1px solid var(--ff-border)' }}>
              <Wifi size={32} style={{ color: 'var(--ff-text-muted)', margin: '0 auto 12px' }} />
              <p style={{ color: 'var(--ff-text-secondary)', fontSize: '0.9rem' }}>No sensor data available yet.</p>
              <p style={{ color: 'var(--ff-text-muted)', fontSize: '0.78rem', marginTop: 4 }}>
                Register a device and wait for the first telemetry payload.
              </p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 14 }}>
              {measurements.map((m, i) => (
                <SensorCard key={i} measurement={m} />
              ))}
            </div>
          )}
        </div>

        {/* ── Soil Moisture 24h Trend Chart ───────────────────────────────── */}
        <div className="ff-card" style={{ padding: 24, marginBottom: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Droplets size={18} style={{ color: '#3978B8' }} />
              <h2 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--ff-text)' }}>
                Soil Moisture — 24h Trend
              </h2>
            </div>
            {isDemo && (
              <span style={{
                fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.04em',
                background: '#EDE9FE', color: '#4C1D95', padding: '2px 8px',
                borderRadius: 999, border: '1px solid #C4B5FD',
              }}>
                🟣 SIMULATED
              </span>
            )}
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis
                dataKey="time"
                tick={{ fill: 'var(--ff-text-muted)', fontSize: 11 }}
                axisLine={false} tickLine={false}
                interval={3}
              />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fill: 'var(--ff-text-muted)', fontSize: 11 }}
                axisLine={false} tickLine={false}
                tickFormatter={v => `${v}%`}
              />
              <Tooltip
                contentStyle={{
                  background: 'white', border: '1px solid var(--ff-border)',
                  borderRadius: 10, fontSize: '0.82rem', color: 'var(--ff-text)',
                  boxShadow: '0 4px 20px rgba(20,50,30,0.10)',
                }}
                formatter={v => [`${v}%`, 'Moisture']}
              />
              <Line
                type="monotone" dataKey="moisture"
                stroke="#3978B8" strokeWidth={2} dot={false}
                activeDot={{ r: 4, fill: '#3978B8' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* ── Legend ──────────────────────────────────────────────────────── */}
        <div className="ff-card" style={{ padding: 18 }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--ff-text-secondary)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Data Source Legend
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            {[
              { source: 'SENSOR_MEASURED', desc: 'Physical sensor on device' },
              { source: 'ESTIMATED', desc: 'ML / calculated estimate' },
              { source: 'EXTERNAL', desc: 'Third-party data source' },
              { source: 'SYNTHETIC', desc: 'Simulation / test data — NOT real' },
              { source: 'UNAVAILABLE', desc: 'Sensor offline or error' },
            ].map(({ source, desc }) => (
              <div key={source} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <SensorStatusBadge source={source} quality="GOOD" />
                <span style={{ fontSize: '0.72rem', color: 'var(--ff-text-muted)' }}>{desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse-ring {
          0%   { box-shadow: 0 0 0 0 rgba(16,185,129,0.6); }
          70%  { box-shadow: 0 0 0 7px rgba(16,185,129,0); }
          100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        @media (max-width: 768px) {
          .ff-container { padding-left: 16px !important; padding-right: 16px !important; }
        }
      `}</style>
    </div>
  )
}

function SensorCard({ measurement: m }) {
  return (
    <div
      className="ff-card"
      style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 10,
        borderTop: m.data_source === 'SYNTHETIC' ? '3px solid #8B5CF6' :
                   m.data_source === 'SENSOR_MEASURED' ? '3px solid #10B981' :
                   m.data_source === 'ESTIMATED' ? '3px solid #F59E0B' :
                   m.data_source === 'UNAVAILABLE' ? '3px solid #EF4444' : '3px solid #60A5FA',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{
          width: 34, height: 34, borderRadius: 9,
          background: 'var(--ff-soft)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--ff-primary)', flexShrink: 0,
        }}>
          {sensorIcon(m.sensor_type)}
        </div>
        <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--ff-text)' }}>
          {m.parameter_name}
        </div>
      </div>

      {/* Value */}
      <div>
        {m.data_source === 'UNAVAILABLE' ? (
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#EF4444' }}>—</div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
            <span style={{ fontSize: '1.6rem', fontWeight: 900, color: 'var(--ff-text)', lineHeight: 1 }}>
              {m.calibrated_value != null ? m.calibrated_value : '—'}
            </span>
            <span style={{ fontSize: '0.78rem', color: 'var(--ff-text-muted)', fontWeight: 500 }}>
              {m.unit}
            </span>
          </div>
        )}
      </div>

      {/* Badge */}
      <SensorStatusBadge source={m.data_source} quality={m.quality} />

      {/* Timestamp */}
      {m.timestamp && (
        <div style={{ fontSize: '0.68rem', color: 'var(--ff-text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
          <Clock size={10} />
          {minutesAgo(m.timestamp)}
        </div>
      )}
    </div>
  )
}
