import {
  ApiResponse, Meter, Reading, Alert, AnalyzeResult,
  DashboardSummary, ExplainResponse, DemoScenarioResult, EvaluationBenchmarkResult,
  WaterImpactSummaryResponse, UserProfile, LoginResponse, DemoAccount
} from './types';

const TOKEN_STORAGE_KEY = 'jalrakshak_auth_token';

let currentAuthToken: string = typeof window !== 'undefined' ? (sessionStorage.getItem(TOKEN_STORAGE_KEY) || '') : '';
let unauthorizedHandler: (() => void) | null = null;

export function setAuthToken(token: string) {
  currentAuthToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
    } else {
      sessionStorage.removeItem(TOKEN_STORAGE_KEY);
    }
  }
}

export function clearAuthToken() {
  currentAuthToken = '';
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

export function getAuthToken(): string {
  if (!currentAuthToken && typeof window !== 'undefined') {
    currentAuthToken = sessionStorage.getItem(TOKEN_STORAGE_KEY) || '';
  }
  return currentAuthToken;
}

export function onUnauthorized(handler: () => void) {
  unauthorizedHandler = handler;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set('Content-Type', 'application/json');
  const token = getAuthToken();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(endpoint, {
    ...options,
    headers,
  });

  if (response.status === 401 && endpoint !== '/api/auth/login') {
    clearAuthToken();
    if (unauthorizedHandler) {
      unauthorizedHandler();
    }
  }

  const payload: ApiResponse<T> = await response.json();

  if (!response.ok || payload.error) {
    const errorMsg = payload.error ? payload.error.message : `HTTP error ${response.status}`;
    throw new Error(errorMsg);
  }

  return payload.data as T;
}

export const api = {
  getHealth: () => request<{ status: string }>('/api/health'),

  // Meters
  getMeters: () => request<Meter[]>('/api/meters'),
  createMeter: (data: { name: string; location_label: string; meter_type?: string }) =>
    request<Meter>('/api/meters', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getMeterReadings: (meterId: string, limit: number = 100) =>
    request<Reading[]>(`/api/meters/${meterId}/readings?limit=${limit}`),

  // Readings
  submitReading: (data: { meter_id: string; timestamp: string; reading_liters: number }) =>
    request<Reading>('/api/readings', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  uploadCsv: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const headers = new Headers();
    if (currentAuthToken) {
      headers.set('Authorization', `Bearer ${currentAuthToken}`);
    }
    const response = await fetch('/api/readings/upload', {
      method: 'POST',
      headers,
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok || payload.error) {
      throw new Error(payload.error ? payload.error.message : 'CSV upload failed');
    }
    return payload.data;
  },

  // Analytics
  analyzeMeter: (meterId: string) =>
    request<AnalyzeResult>(`/api/analyze/${meterId}`, {
      method: 'POST',
    }),

  // Alerts
  getAlerts: (params: { meter_id?: string; severity?: string; status?: string } = {}) => {
    const query = new URLSearchParams();
    if (params.meter_id) query.set('meter_id', params.meter_id);
    if (params.severity) query.set('severity', params.severity);
    if (params.status) query.set('status', params.status);
    const qs = query.toString();
    return request<Alert[]>(`/api/alerts${qs ? `?${qs}` : ''}`);
  },
  getAlertDetail: (alertId: string) => request<Alert>(`/api/alerts/${alertId}`),
  acknowledgeAlert: (alertId: string, note?: string) =>
    request<Alert>(`/api/alerts/${alertId}/acknowledge${note ? `?note=${encodeURIComponent(note)}` : ''}`, {
      method: 'POST',
    }),
  resolveAlert: (alertId: string, resolution: string, note?: string) =>
    request<Alert>(`/api/alerts/${alertId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution, note }),
    }),

  // Explanation
  explainAlert: (alertId: string, language: string = 'en-IN') =>
    request<ExplainResponse>('/api/explain', {
      method: 'POST',
      body: JSON.stringify({ alert_id: alertId, language }),
    }),

  // Demo Scenarios
  runDemoScenario: (scenario: string, seed: number = 42) =>
    request<DemoScenarioResult>('/api/demo/scenario', {
      method: 'POST',
      body: JSON.stringify({ scenario, seed }),
    }),

  // Dashboard
  getDashboardSummary: () => request<DashboardSummary>('/api/dashboard/summary'),

  // Evaluation Benchmark
  runEvaluation: (seed: number = 42) =>
    request<EvaluationBenchmarkResult>('/api/evaluation/run', {
      method: 'POST',
      body: JSON.stringify({ seed }),
    }),
  getEvaluationBenchmark: (seed: number = 42) =>
    request<EvaluationBenchmarkResult>(`/api/evaluation/benchmark?seed=${seed}`),

  // Water Impact
  getWaterImpact: (avoidedFraction: number = 0.70, meterId?: string) => {
    const params = new URLSearchParams();
    params.set('avoided_fraction', avoidedFraction.toString());
    if (meterId) {
      params.set('meter_id', meterId);
    }
    return request<WaterImpactSummaryResponse>(`/api/dashboard/water-impact?${params.toString()}`);
  },

  // Auth
  login: (email: string, password?: string) =>
    request<LoginResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  getMe: () => request<UserProfile>('/api/auth/me'),
  logout: () => request<{ message: string }>('/api/auth/logout', { method: 'POST' }),
  getDemoAccounts: () => request<DemoAccount[]>('/api/auth/demo-accounts'),
};
