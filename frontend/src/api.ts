import {
  ApiResponse, Meter, Reading, Alert, AnalyzeResult,
  DashboardSummary, ExplainResponse, DemoScenarioResult
} from './types';

let currentAuthToken: string = '';

export function setAuthToken(token: string) {
  currentAuthToken = token;
}

export function getAuthToken(): string {
  return currentAuthToken;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set('Content-Type', 'application/json');
  if (currentAuthToken) {
    headers.set('Authorization', `Bearer ${currentAuthToken}`);
  }

  const response = await fetch(endpoint, {
    ...options,
    headers,
  });

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
};
