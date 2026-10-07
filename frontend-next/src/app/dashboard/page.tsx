"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/lib/auth";
import { api, errorMessage } from "@/lib/api";
import { POLL_INTERVAL_MS } from "@/lib/env";
import type {
  CurrentSessionResponse,
  DeviceInfo,
  HealthStatus,
  LatestReadingsFallback,
  PefReading,
  PredictionExplanation,
  PredictionSummary,
  ReportResponse,
  SensorKey,
} from "@/lib/types";
import { isFullReport } from "@/lib/types";
import SignInForm from "@/components/SignInForm";
import Header from "@/components/dashboard/Header";
import SensorCards from "@/components/dashboard/SensorCards";
import PefSection from "@/components/dashboard/PefSection";
import RiskCard from "@/components/dashboard/RiskCard";
import ShapSection from "@/components/dashboard/ShapSection";
import DataQualitySection from "@/components/dashboard/DataQualitySection";
import PredictionHistory from "@/components/dashboard/PredictionHistory";
import SessionPanel from "@/components/dashboard/SessionPanel";
import Disclaimer from "@/components/dashboard/Disclaimer";

type ReadingsState = "loading" | "error" | "ready" | "empty";

const SENSOR_KEYS: SensorKey[] = [
  "heart_rate",
  "spo2",
  "temperature_c",
  "humidity_percent",
  "dust_indicator",
];

export default function DashboardPage() {
  const { session, loading, signOut } = useAuth();

  if (loading) {
    return (
      <main className="mx-auto max-w-7xl p-4 sm:p-6">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Loading session…
        </p>
      </main>
    );
  }

  if (!session) {
    return (
      <main className="mx-auto max-w-7xl p-4 sm:p-6">
        <SignInForm />
      </main>
    );
  }

  return (
    <DashboardView
      email={session.email}
      onSignOut={() => {
        void signOut();
      }}
    />
  );
}

function DashboardView({
  email,
  onSignOut,
}: {
  email: string;
  onSignOut: () => void;
}) {
  // ---- live (polled) state ----
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [backendUnreachable, setBackendUnreachable] = useState(false);
  const [sessionInfo, setSessionInfo] =
    useState<CurrentSessionResponse | null>(null);
  const [sessionError, setSessionError] = useState<string | null>(null);
  const [readings, setReadings] = useState<LatestReadingsFallback | null>(
    null
  );
  const [readingsState, setReadingsState] =
    useState<ReadingsState>("loading");
  const [readingsError, setReadingsError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  // ---- on-demand state ----
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [reportState, setReportState] =
    useState<ReadingsState>("loading");
  const [reportError, setReportError] = useState<string | null>(null);
  const [history, setHistory] = useState<PredictionSummary[] | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [explanation, setExplanation] =
    useState<PredictionExplanation | null>(null);
  const [explanationState, setExplanationState] =
    useState<ReadingsState>("loading");
  const [explanationError, setExplanationError] = useState<string | null>(
    null
  );
  const [pefHistory, setPefHistory] = useState<PefReading[] | null>(null);

  const mountedRef = useRef(true);
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  /** Generate a personalized report (creates a prediction, then refresh
   *  history, explanation and PEF history so every section stays in sync). */
  const generateReport = useCallback(async () => {
    setReportState("loading");
    setReportError(null);
    try {
      const r = await api.post<ReportResponse>("/reports/personalized");
      if (!mountedRef.current) return;
      setReport(r);
      setReportState("ready");
      try {
        const h = await api.get<PredictionSummary[]>("/predictions/history");
        if (!mountedRef.current) return;
        setHistory(h);
        setHistoryError(null);
        const latest = h[0];
        if (latest) {
          try {
            const ex = await api.get<PredictionExplanation>(
              `/predictions/${latest.prediction_id}/explanation`
            );
            if (!mountedRef.current) return;
            setExplanation(ex);
            setExplanationState("ready");
            setExplanationError(null);
          } catch (err) {
            if (!mountedRef.current) return;
            setExplanationState("error");
            setExplanationError(errorMessage(err));
          }
        } else {
          setExplanation(null);
          setExplanationState("empty");
          setExplanationError(null);
        }
      } catch (err) {
        if (!mountedRef.current) return;
        setHistoryError(errorMessage(err));
        setExplanationState("error");
        setExplanationError("Prediction history unavailable");
      }
      try {
        const p = await api.get<PefReading[]>("/pefr");
        if (mountedRef.current) setPefHistory(p);
      } catch {
        // PEF history is optional for the report view
      }
    } catch (err) {
      if (!mountedRef.current) return;
      setReportState("error");
      setReportError(errorMessage(err));
    }
  }, []);

  // ---- initial load ----
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const h = await api.get<HealthStatus>("/health");
        if (!cancelled) {
          setHealth(h);
          setBackendUnreachable(false);
        }
      } catch {
        if (!cancelled) setBackendUnreachable(true);
      }
      try {
        const d = await api.get<DeviceInfo[]>("/devices");
        if (!cancelled) setDevices(d);
      } catch {
        // device list is only needed for session actions
      }
      try {
        const p = await api.get<PefReading[]>("/pefr");
        if (!cancelled) setPefHistory(p);
      } catch {
        // PEF section will show its own empty state
      }
      try {
        const h = await api.get<PredictionSummary[]>("/predictions/history");
        if (!cancelled) setHistory(h);
        const latest = h[0];
        if (latest) {
          try {
            const ex = await api.get<PredictionExplanation>(
              `/predictions/${latest.prediction_id}/explanation`
            );
            if (!cancelled) {
              setExplanation(ex);
              setExplanationState("ready");
            }
          } catch (err) {
            if (!cancelled) {
              setExplanationState("error");
              setExplanationError(errorMessage(err));
            }
          }
        } else if (!cancelled) {
          setExplanationState("empty");
        }
      } catch (err) {
        if (!cancelled) {
          setHistoryError(errorMessage(err));
          setExplanationState("error");
          setExplanationError("Prediction history unavailable");
        }
      }
      await generateReport();
    })();
    return () => {
      cancelled = true;
    };
  }, [generateReport]);

  // ---- live polling (sensors + session) ----
  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const [s, r] = await Promise.all([
          api.get<CurrentSessionResponse>("/measurement-sessions/current"),
          api.get<
            | { session_id: string; status: "ACTIVE"; latest: LatestReadingsFallback }
            | { status: "NO_ACTIVE_SESSION" }
          >("/measurement-sessions/current/latest-readings"),
        ]);
        if (cancelled) return;
        setSessionInfo(s);
        setSessionError(null);

        let latest: LatestReadingsFallback = {};
        if (r.status === "ACTIVE") {
          latest = r.latest;
        } else {
          // No active session: fall back to the user's most recent
          // stored readings so the cards still show real data.
          try {
            const fb = await api.get<LatestReadingsFallback>("/readings/latest");
            if (!cancelled) latest = fb;
          } catch {
            latest = {};
          }
        }

        let timestamp: string | null = null;
        for (const key of SENSOR_KEYS) {
          const v = latest[key];
          if (v?.timestamp) {
            timestamp = v.timestamp;
            break;
          }
        }
        setReadings(latest);
        setLastUpdated(timestamp);
        setReadingsState(
          Object.keys(latest).length > 0 ? "ready" : "empty"
        );
        setReadingsError(null);
      } catch (err) {
        if (cancelled) return;
        setReadingsState("error");
        setReadingsError(errorMessage(err));
      }
    };
    tick();
    const id = setInterval(tick, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const stale =
    lastUpdated !== null &&
    Date.now() - new Date(lastUpdated).getTime() > POLL_INTERVAL_MS * 3;

  const historyState: ReadingsState =
    history === null ? "loading" : history.length === 0 ? "empty" : "ready";

  const fullReport = report !== null && isFullReport(report) ? report : null;

  return (
    <main className="mx-auto max-w-7xl space-y-4 p-4 sm:p-6">
      <Header
        systemStatus={health?.status ?? null}
        backendUnreachable={backendUnreachable}
        sessionStatus={
          sessionInfo?.status === "ACTIVE" ? "ACTIVE" : "No active session"
        }
        lastUpdated={lastUpdated}
        email={email}
        onSignOut={onSignOut}
      />

      {backendUnreachable && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/40 dark:text-red-300">
          Backend unavailable. Check that the FastAPI server is running at
          the configured API URL.
        </div>
      )}

      <SensorCards
        latest={readings}
        state={readingsState}
        error={readingsError}
        stale={stale}
      />

      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-gray-400 dark:text-gray-500">
          {report && isFullReport(report)
            ? `Report generated ${new Date(report.generated_at).toLocaleString()}`
            : "Report not generated yet"}
        </p>
        <button
          onClick={() => {
            void generateReport();
          }}
          disabled={reportState === "loading"}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {reportState === "loading" ? "Generating…" : "Generate personalized report"}
        </button>
      </div>

      {report && !isFullReport(report) && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-900/40 dark:text-amber-300">
          {report.message}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <PefSection
          report={fullReport}
          pefHistory={pefHistory}
          state={reportState}
          error={reportError}
        />
        <RiskCard report={fullReport} state={reportState} error={reportError} />
        <ShapSection
          explanation={explanation}
          state={explanationState}
          error={explanationError}
        />
        <DataQualitySection
          quality={fullReport?.data_quality ?? null}
          state={reportState}
          error={reportError}
        />
        <SessionPanel
          session={sessionInfo}
          sessionError={sessionError}
          devices={devices}
          lastReadingTimestamp={lastUpdated}
          onSessionChange={(s) => setSessionInfo(s)}
        />
        <PredictionHistory
          history={history}
          state={historyState}
          error={historyError}
        />
      </div>

      <Disclaimer report={fullReport} />
    </main>
  );
}
