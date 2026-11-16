import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Cpu, Key, Copy, Check, CheckCircle2,
  AlertCircle, ShieldCheck, Wifi, MapPin
} from 'lucide-react'
import { registerDevice } from '../services/api'

export default function DeviceRegistration() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    name: 'AgriSense-Field-01',
    farm_id: 'farm-parbhani-01',
    field_id: 'field-cotton-north',
    hardware_profile: 'ESP32-DevKit-V1-Standard',
    firmware_version: '1.0.0',
    wifi_ssid: 'AgriNet-Farm-WiFi',
  })

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [copiedId, setCopiedId] = useState(false)
  const [copiedKey, setCopiedKey] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const resp = await registerDevice(formData)
      setResult(resp.data || resp)
    } catch (err) {
      console.error('Registration error:', err)
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Registration failed. Ensure backend API is operational.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text)
    if (type === 'id') {
      setCopiedId(true)
      setTimeout(() => setCopiedId(false), 2000)
    } else {
      setCopiedKey(true)
      setTimeout(() => setCopiedKey(false), 2000)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <button
          onClick={() => navigate('/devices')}
          className="flex items-center gap-2 text-sm text-emerald-400 hover:text-emerald-300 mb-6 transition-colors"
        >
          <ArrowLeft size={16} /> Back to Device Monitor
        </button>

        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Cpu size={22} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Register AgriSense IoT Node</h1>
            <p className="text-slate-400 text-sm">Provision cryptographic credentials and bind to agricultural plot</p>
          </div>
        </div>

        {error && (
          <div className="my-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm flex items-center gap-3">
            <AlertCircle size={18} className="shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {!result ? (
          <form onSubmit={handleSubmit} className="mt-8 space-y-6 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur-sm">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Device Node Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="e.g. AgriSense-South-Plot"
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Farm ID
                </label>
                <input
                  type="text"
                  name="farm_id"
                  value={formData.farm_id}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Field / Plot Identifier
                </label>
                <input
                  type="text"
                  name="field_id"
                  value={formData.field_id}
                  onChange={handleChange}
                  placeholder="Optional field ID"
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Hardware Profile
                </label>
                <select
                  name="hardware_profile"
                  value={formData.hardware_profile}
                  onChange={handleChange}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-emerald-500 transition-colors"
                >
                  <option value="ESP32-DevKit-V1-Standard">ESP32 DevKit V1 (Standard Sensor BOM)</option>
                  <option value="ESP32-S3-Cellular">ESP32-S3 + SIM7080G (Cellular / NB-IoT)</option>
                  <option value="ESP32-LoRaWAN">ESP32 + SX1262 (LoRaWAN 868/915 MHz)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Firmware Version
                </label>
                <input
                  type="text"
                  name="firmware_version"
                  value={formData.firmware_version}
                  onChange={handleChange}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Wi-Fi SSID (Optional)
                </label>
                <input
                  type="text"
                  name="wifi_ssid"
                  value={formData.wifi_ssid}
                  onChange={handleChange}
                  placeholder="e.g. FarmNet_2G"
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex justify-end">
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition-all shadow-lg shadow-emerald-900/30 disabled:opacity-50"
              >
                {submitting ? 'Registering Node...' : 'Register Device'}
              </button>
            </div>
          </form>
        ) : (
          <div className="mt-8 bg-slate-900/80 border border-emerald-500/30 rounded-2xl p-6 md:p-8 backdrop-blur-sm">
            <div className="flex items-center gap-3 text-emerald-400 mb-6">
              <CheckCircle2 size={28} />
              <div>
                <h2 className="text-xl font-bold text-white">Device Registered Successfully!</h2>
                <p className="text-slate-400 text-xs">Configure your ESP32 firmware with the credentials below.</p>
              </div>
            </div>

            <div className="space-y-4 mb-6">
              <div className="p-4 rounded-xl bg-slate-850 border border-slate-800">
                <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                  <span>DEVICE ID (UUID)</span>
                  <button
                    onClick={() => copyToClipboard(result.device_id, 'id')}
                    className="flex items-center gap-1 text-emerald-400 hover:text-emerald-300"
                  >
                    {copiedId ? <Check size={14} /> : <Copy size={14} />} {copiedId ? 'Copied' : 'Copy'}
                  </button>
                </div>
                <code className="text-sm font-mono text-emerald-300 break-all">{result.device_id}</code>
              </div>

              {result.api_key && (
                <div className="p-4 rounded-xl bg-slate-850 border border-amber-500/30">
                  <div className="flex items-center justify-between text-xs text-amber-400 mb-1">
                    <span className="flex items-center gap-1"><Key size={14} /> DEVICE API KEY (Save Now — Shown Once)</span>
                    <button
                      onClick={() => copyToClipboard(result.api_key, 'key')}
                      className="flex items-center gap-1 text-amber-300 hover:text-amber-200"
                    >
                      {copiedKey ? <Check size={14} /> : <Copy size={14} />} {copiedKey ? 'Copied' : 'Copy'}
                    </button>
                  </div>
                  <code className="text-sm font-mono text-amber-200 break-all">{result.api_key}</code>
                </div>
              )}
            </div>

            <div className="p-4 rounded-xl bg-slate-850 border border-slate-800 mb-6 text-xs text-slate-300 space-y-2">
              <div className="font-semibold text-slate-200 flex items-center gap-1.5">
                <ShieldCheck size={15} className="text-emerald-400" /> Firmware Configuration Step:
              </div>
              <p>Add these credentials into your ESP32 <code className="text-emerald-400">hardware_profile.json</code>:</p>
              <pre className="p-3 rounded-lg bg-slate-950 font-mono text-slate-400 text-[11px] overflow-x-auto">
{`"backend": {
  "device_id": "${result.device_id}",
  "api_base_url": "http://YOUR_SERVER_IP:8000",
  "telemetry_endpoint": "/api/telemetry/ingest"
}`}
              </pre>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => navigate('/devices')}
                className="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition-all text-center"
              >
                Go to Device Monitor
              </button>
              <button
                onClick={() => setResult(null)}
                className="px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition-all"
              >
                Register Another Node
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
