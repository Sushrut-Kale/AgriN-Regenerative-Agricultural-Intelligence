/**
 * FarmFriend AI — API Service
 * All API calls to the FastAPI backend.
 */

const BASE_URL = '/api';

async function apiCall(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    const error = data.detail || data.error || 'An error occurred';
    throw new Error(typeof error === 'string' ? error : JSON.stringify(error));
  }

  return data;
}

// ── Reference Data ─────────────────────────────────────────────────────────
export const getReferenceData = (state = null) =>
  apiCall(state ? `/reference-data?state=${encodeURIComponent(state)}` : '/reference-data');

export const getCrops = () =>
  apiCall('/crops');

export const getLiveWeather = (params = 'Parbhani') => {
  if (typeof params === 'object') {
    const q = new URLSearchParams();
    if (params.district) q.append('district', params.district);
    if (params.state) q.append('state', params.state);
    if (params.lat != null) q.append('lat', params.lat);
    if (params.lon != null) q.append('lon', params.lon);
    return apiCall(`/weather?${q.toString()}`);
  }
  return apiCall(`/weather?district=${encodeURIComponent(params)}`);
};


// ── Validation ──────────────────────────────────────────────────────────────
export const validateInputs = (payload) =>
  apiCall('/validate', { method: 'POST', body: JSON.stringify(payload) });

// ── Main Analysis ───────────────────────────────────────────────────────────
export const runAnalysis = (payload) =>
  apiCall('/analyze', { method: 'POST', body: JSON.stringify(payload) });

// ── Feasibility (I Want to Grow This) ──────────────────────────────────────
export const checkFeasibility = (payload) =>
  apiCall('/feasibility', { method: 'POST', body: JSON.stringify(payload) });

// ── What-If ─────────────────────────────────────────────────────────────────
export const runWhatIf = (payload) =>
  apiCall('/whatif', { method: 'POST', body: JSON.stringify(payload) });

// ── Explanation ─────────────────────────────────────────────────────────────
export const getExplanation = (cropResult, explanationType = 'crop_detail') =>
  apiCall('/explain', {
    method: 'POST',
    body: JSON.stringify({ crop_result: cropResult, explanation_type: explanationType })
  });

// ── Feedback ────────────────────────────────────────────────────────────────
export const submitFeedback = (payload) =>
  apiCall('/feedback', { method: 'POST', body: JSON.stringify(payload) });

export const getFeedbackSummary = () =>
  apiCall('/feedback/summary');

// ── Analytics ───────────────────────────────────────────────────────────────
export const getAnalytics = () =>
  apiCall('/analytics');

export const getModelInfo = () =>
  apiCall('/model-info');

// ── Phase 2.5 Intelligence & Hardening Endpoints ────────────────────────────
export const getRegenerativePractices = () =>
  apiCall('/regenerative/practices');

export const recommendRegenerative = (payload) =>
  apiCall('/regenerative/recommend', { method: 'POST', body: JSON.stringify(payload) });

export const getFarmHealth = (farmId, payload = null) =>
  apiCall(`/farms/${encodeURIComponent(farmId)}/health`, {
    method: 'POST',
    body: payload ? JSON.stringify(payload) : undefined
  });

export const getFarmAdvisories = (farmId, payload) =>
  apiCall(`/farms/${encodeURIComponent(farmId)}/advisories`, {
    method: 'POST',
    body: JSON.stringify(payload)
  });

export const submitAdvisoryFeedback = (payload) =>
  apiCall('/advisory/feedback', { method: 'POST', body: JSON.stringify(payload) });

export const getDataSources = () =>
  apiCall('/data-sources');

export const getCoverage = () =>
  apiCall('/coverage');
