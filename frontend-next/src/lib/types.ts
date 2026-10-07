/**
 * Shared TypeScript types for the Asthma Monitoring Dashboard.
 * These mirror the existing FastAPI response contracts exactly.
 */

export type RiskLevel = "low" | "moderate" | "high";

export interface HealthStatus {
  status: string;
  api_version?: string;
}

export interface DeviceInfo {
  id: string;
  device_code: string;
  device_name: string | null;
  is_active: boolean;
  last_seen_at: string | null;
}

/** A single sensor value as returned by the backend readings endpoints.
 *  `valid` reflects the stored sensor validity flag; false means the
 *  sensor failed and the numeric value must not be displayed as data. */
export interface SensorValue {
  value: number | null;
  unit: string;
  timestamp: string;
  valid?: boolean;
}

export type SensorKey =
  | "heart_rate"
  | "spo2"
  | "temperature_c"
  | "humidity_percent"
  | "dust_indicator";

/** GET /measurement-sessions/current/latest-readings (active session) */
export interface SessionReadingsResponse {
  session_id: string;
  status: "ACTIVE";
  latest: Partial<Record<SensorKey, SensorValue>>;
}

/** GET /readings/latest (fallback: most recent reading for the user, no session wrapper) */
export type LatestReadingsFallback = Partial<Record<SensorKey, SensorValue>>;

export type CurrentSessionResponse =
  | { status: "ACTIVE"; session_id: string; device_id: string; started_at: string }
  | { status: "NO_ACTIVE_SESSION" };

export interface PefReading {
  id: string;
  pef_l_min: number;
  personal_best_l_min: number | null;
  recorded_at: string;
}

export interface PredictionSummary {
  prediction_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  model_version: string;
  prediction_time: string;
}

export interface ShapFactor {
  feature: string;
  shap_value: number;
}

export interface PredictionExplanation {
  prediction_id: string;
  risk_score: number | null;
  risk_level: RiskLevel | null;
  model_version: string;
  prediction_time: string;
  explanation: {
    top_increasing: ShapFactor[];
    top_decreasing: ShapFactor[];
  } | null;
  data_quality: string | null;
}

export interface DataQualityState {
  pefr: string;
  hr: string;
  overall: string;
}

/** POST /reports/personalized — full report shape. */
export interface PersonalizedReport {
  title: string;
  user_id: string;
  generated_at: string;
  current_measurements: {
    current_pef: number | null;
    personal_best_pef: number | null;
    pef_pct_best: number | null;
  };
  recent_trend: { recent_pef: number[] };
  symptoms_recent: { timestamp: string; cough: number; wheezing: number }[];
  reliever_note: string;
  model_prediction: {
    risk_probability: number;
    risk_level: string;
    horizon_days: number;
    target: string;
    model_version: string;
    clinical_validation_status: string;
  };
  explanation: {
    increasing_risk: ShapFactor[];
    decreasing_risk: ShapFactor[];
    note: string;
  };
  data_quality: DataQualityState;
  safety: string;
}

/** POST /reports/personalized — insufficient-data shape (no inference possible). */
export interface ReportInsufficientData {
  user_id: string;
  data_quality: DataQualityState;
  risk: null;
  message: string;
}

export type ReportResponse = PersonalizedReport | ReportInsufficientData;

export function isFullReport(r: ReportResponse): r is PersonalizedReport {
  return "model_prediction" in r && r.model_prediction !== undefined;
}

export interface AuthSession {
  accessToken: string;
  refreshToken: string;
  expiresAt: number; // epoch seconds
  userId: string;
  email: string;
}
