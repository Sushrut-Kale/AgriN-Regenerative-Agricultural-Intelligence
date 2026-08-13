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
export const getReferenceData = () =>
  apiCall('/reference-data');

export const getCrops = () =>
  apiCall('/crops');

export const getLiveWeather = (district = 'Parbhani') =>
  apiCall(`/weather?district=${encodeURIComponent(district)}`);


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
