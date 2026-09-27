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
  robust_z?: number;
  mad?: number;
  deviation_score?: number;
  persistence_score?: number;
  trend_score?: number;
  loss_score?: number;
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
  meter_type?: string;
  operational_schedule?: string;
  scenario_category?: string;
}

export interface ScenarioEvaluationItem {
  scenario: string;
  description: string;
  ground_truth: string;
  expected_alert?: boolean | null;
  actual_alert: boolean;
  classification: string;
  scenario_category?: string;
  status: string;
  risk_score: number;
  severity: string;
  estimated_excess_liters: number;
  persistence_intervals: number;
  processing_latency_ms: number;
  mae?: number | null;
  passed: boolean;
}

export interface ConfusionMatrix {
  true_positives: number;
  false_positives: number;
  true_negatives: number;
  false_negatives: number;
}

export interface ClassificationMetrics {
  precision: number | null;
  recall: number | null;
  f1: number | null;
  false_alert_rate: number | null;
  confusion_matrix: ConfusionMatrix;
}

export interface NumericalAccuracyMetrics {
  benchmark_mae: number | null;
  field_telemetry_mae_status: string;
}

export interface LatencyMetrics {
  avg_processing_latency_ms: number;
  min_processing_latency_ms: number;
  max_processing_latency_ms: number;
  measurement_scope: string;
}

export interface AiEvaluationMetrics {
  groq_configured: boolean;
  structured_output_success_rate: number | null;
  structured_output_status: string;
  fallback_coverage_rate: number;
  fallback_supported_languages: string[];
  numerical_authority_preserved: boolean;
}

export interface WorkflowMetrics {
  workflow_tested: boolean;
  steps_total: number;
  steps_completed: number;
  completion_rate: number;
  lifecycle_states_exercised: string[];
}

export interface EvaluationBenchmarkResult {
  scenarios_tested: number;
  classification: ClassificationMetrics;
  numerical_accuracy: NumericalAccuracyMetrics;
  latency: LatencyMetrics;
  ai_metrics: AiEvaluationMetrics;
  workflow: WorkflowMetrics;
  items: ScenarioEvaluationItem[];
}

export interface WaterImpactItem {
  meter_id: string;
  meter_code: string;
  meter_type: string;
  location_label?: string | null;
  alert_id: string;
  severity: string;
  risk_score: number;
  current_usage_liters: number;
  baseline_liters: number;
  estimated_excess_liters: number;
  potential_savings_liters: number;
  is_contextual_agricultural: boolean;
  verification_required: boolean;
}

export interface WaterImpactSummaryResponse {
  total_estimated_excess_liters: number;
  potential_savings_liters: number;
  avoided_fraction_assumed: number;
  active_anomalies_count: number;
  contextual_agricultural_meters_count: number;
  contextual_agricultural_excess_liters: number;
  assumption_note: string;
  items: WaterImpactItem[];
}

export interface UserProfile {
  id: string;
  email: string;
  role: string;
  organization_id?: string | null;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export interface DemoAccount {
  email: string;
  role: string;
  label: string;
}
