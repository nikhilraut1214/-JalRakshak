export interface ApiError {
  code: string;
  message: string;
}

export interface ApiResponse<T> {
  data: T | null;
  error: ApiError | null;
}

export interface User {
  id: string;
  email: string;
  role: 'RESIDENT' | 'SOCIETY_MANAGER' | 'FARM_OPERATOR' | 'INSTITUTION_ADMIN' | 'ADMINISTRATOR';
  organization_id?: string;
  created_at: string;
}

export interface Meter {
  id: string;
  name: string;
  location_label: string;
  meter_type: string;
  owner_id?: string;
  organization_id?: string;
  created_at: string;
}

export interface Reading {
  id: string;
  meter_id: string;
  timestamp: string;
  reading_liters: number;
  raw_or_derived: string;
  created_at: string;
}

export interface EvidenceDetail {
  current_usage_liters: number;
  baseline_liters: number;
  deviation_pct: number;
  persistence_intervals: number;
  trend: 'increasing' | 'stable' | 'decreasing';
  estimated_excess_liters: number;
  risk_score: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  verification_required: boolean;
  robust_z?: number;
  mad?: number;
  deviation_score?: number;
  persistence_score?: number;
  trend_score?: number;
  loss_score?: number;
}

export interface AlertEvidence {
  id: string;
  alert_id: string;
  current_usage_liters: number;
  baseline_liters: number;
  deviation_pct: number;
  persistence_intervals: number;
  trend: string;
  estimated_excess_liters: number;
  risk_score: number;
  severity: string;
  verification_required: boolean;
  raw_evidence_json?: any;
  created_at: string;
}

export interface Alert {
  id: string;
  meter_id: string;
  status: 'DETECTED' | 'ACKNOWLEDGED' | 'VERIFYING' | 'INVESTIGATING' | 'CONFIRMED' | 'FALSE_ALARM' | 'RESOLVED';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_score: number;
  created_at: string;
  updated_at: string;
  evidence?: AlertEvidence;
}

export interface InsufficientHistoryDetail {
  status: 'INSUFFICIENT_HISTORY';
  message: string;
  readings_count: number;
  required_count: number;
}

export interface AnalyzeResult {
  meter_id: string;
  status: 'SUCCESS' | 'INSUFFICIENT_HISTORY';
  message?: string;
  evidence?: EvidenceDetail;
  alert?: Alert;
  insufficient_history?: InsufficientHistoryDetail;
}

export interface DashboardSummary {
  total_meters: number;
  active_alerts_count: number;
  critical_alerts_count: number;
  high_alerts_count: number;
  recent_consumption_liters: number;
  expected_baseline_liters: number;
  recent_trend: string;
  max_risk_score: number;
  overall_severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  insufficient_history_meters_count: number;
  next_verification_action?: string;
  evidence_highlights: EvidenceDetail[];
}

export interface ExplainResponse {
  alert_id: string;
  language: string;
  explanation: string;
  source: 'groq' | 'deterministic';
}

export interface DemoScenarioResult {
  scenario: string;
  seed: number;
  meter_id: string;
  readings_count: number;
  ground_truth: string;
  description: string;
}
