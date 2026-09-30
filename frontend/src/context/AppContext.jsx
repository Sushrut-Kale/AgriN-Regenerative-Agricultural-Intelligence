import { createContext, useContext, useState, useEffect } from 'react'

const AppContext = createContext(null)

const loadSaved = (key, fallback) => {
  try {
    const saved = sessionStorage.getItem(`ff_${key}`)
    return saved ? JSON.parse(saved) : fallback
  } catch (e) {
    return fallback
  }
}

const saveState = (key, value) => {
  try {
    if (value === null || value === undefined) {
      sessionStorage.removeItem(`ff_${key}`)
    } else {
      sessionStorage.setItem(`ff_${key}`, JSON.stringify(value))
    }
  } catch (e) {}
}

export function AppProvider({ children }) {
  const [farmData, setFarmDataState] = useState(() => loadSaved('farmData', {
    country: 'India',
    state: 'Maharashtra',
    district: '',
    sub_district: '',
    village: '',
    latitude: null,
    longitude: null,
    agro_climatic_zone: '',
    season: '',
    farm_area: '',
    soil_type: '',
    irrigation_available: 'no',
    water_source: '',
    drainage: 'unknown',
    previous_crop: '',
  }))

  const [soilData, setSoilDataState] = useState(() => loadSaved('soilData', {
    N: '', P: '', K: '', S: '',
    Zn: '', Fe: '', Cu: '', Mn: '', B: '',
    ph: '', EC: '', OC: ''
  }))

  const [envData, setEnvDataState] = useState(() => loadSaved('envData', {
    temperature: '', humidity: '', rainfall: ''
  }))

  const [analysisResult, setAnalysisResultState] = useState(() => loadSaved('analysisResult', null))
  const [sessionId, setSessionIdState] = useState(() => loadSaved('sessionId', null))
  const [selectedCrop, setSelectedCropState] = useState(() => loadSaved('selectedCrop', null))
  const [feasibilityResult, setFeasibilityResultState] = useState(() => loadSaved('feasibilityResult', null))
  const [whatIfResult, setWhatIfResultState] = useState(() => loadSaved('whatIfResult', null))

  const setFarmData = val => setFarmDataState(prev => {
    const next = typeof val === 'function' ? val(prev) : val
    saveState('farmData', next)
    return next
  })

  const setSoilData = val => setSoilDataState(prev => {
    const next = typeof val === 'function' ? val(prev) : val
    saveState('soilData', next)
    return next
  })

  const setEnvData = val => setEnvDataState(prev => {
    const next = typeof val === 'function' ? val(prev) : val
    saveState('envData', next)
    return next
  })

  const setAnalysisResult = val => {
    saveState('analysisResult', val)
    setAnalysisResultState(val)
  }

  const setSessionId = val => {
    saveState('sessionId', val)
    setSessionIdState(val)
  }

  const setSelectedCrop = val => {
    saveState('selectedCrop', val)
    setSelectedCropState(val)
  }

  const setFeasibilityResult = val => {
    saveState('feasibilityResult', val)
    setFeasibilityResultState(val)
  }

  const setWhatIfResult = val => {
    saveState('whatIfResult', val)
    setWhatIfResultState(val)
  }

  // Helper to convert empty strings to null for API
  const prepareForApi = (obj) => {
    const out = {}
    for (const [k, v] of Object.entries(obj || {})) {
      out[k] = (v === '' || v === null || v === undefined) ? null : v
    }
    return out
  }

  const getApiPayload = () => ({
    farm_data: prepareForApi(farmData),
    soil_data: prepareForApi(soilData),
    env_data: prepareForApi(envData),
    session_id: sessionId
  })

  return (
    <AppContext.Provider value={{
      farmData, setFarmData,
      soilData, setSoilData,
      envData, setEnvData,
      analysisResult, setAnalysisResult,
      sessionId, setSessionId,
      selectedCrop, setSelectedCrop,
      feasibilityResult, setFeasibilityResult,
      whatIfResult, setWhatIfResult,
      getApiPayload,
      prepareForApi
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}
