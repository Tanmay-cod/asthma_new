import { useState } from "react";
import Section from "./Section";
import { api, errorMessage } from "@/lib/api";
import type {
  CurrentSessionResponse,
  DeviceInfo,
  SensorValue,
} from "@/lib/types";

interface SessionPanelProps {
  session: CurrentSessionResponse | null;
  sessionError: string | null;
  devices: DeviceInfo[];
  lastReadingTimestamp: string | null;
  onSessionChange: (s: CurrentSessionResponse | null) => void;
}

export default function SessionPanel({
  session,
  sessionError,
  devices,
  lastReadingTimestamp,
  onSessionChange,
}: SessionPanelProps) {
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const isActive = session?.status === "ACTIVE";
  const device: DeviceInfo | undefined = isActive
    ? devices.find((d) => d.id === session.device_id)
    : devices.find((d) => d.device_code === "ESP001" && d.is_active);

  async function startSession() {
    setBusy(true);
    setActionError(null);
    try {
      const esp = devices.find((d) => d.device_code === "ESP001" && d.is_active);
      await api.post("/measurement-sessions/start", esp ? { device_id: esp.id } : {});
      const updated = await api.get<CurrentSessionResponse>(
        "/measurement-sessions/current"
      );
      onSessionChange(updated);
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function endSession() {
    if (!isActive || !session || session.status !== "ACTIVE") return;
    setBusy(true);
    setActionError(null);
    try {
      await api.post(`/measurement-sessions/${session.session_id}/end`);
      onSessionChange({ status: "NO_ACTIVE_SESSION" });
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Section
      title="Measurement Session"
      state="ready"
      className="xl:col-span-1"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm text-gray-600 dark:text-gray-300">
          Current session status
        </span>
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
            isActive
              ? "bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300"
              : "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
          }`}
        >
          {isActive ? "ACTIVE" : "No active session"}
        </span>
      </div>
      <dl className="mt-3 space-y-1 text-sm text-gray-600 dark:text-gray-300">
        <div className="flex justify-between gap-2">
          <dt>Device</dt>
          <dd className="font-medium">{device?.device_code ?? "—"}</dd>
        </div>
        {isActive && session && session.status === "ACTIVE" && (
          <div className="flex justify-between gap-2">
            <dt>Session ID</dt>
            <dd className="break-all text-right font-mono text-xs">
              {session.session_id}
            </dd>
          </div>
        )}
        <div className="flex justify-between gap-2">
          <dt>Started at</dt>
          <dd className="font-medium">
            {isActive && session && session.status === "ACTIVE"
              ? new Date(session.started_at).toLocaleString()
              : "—"}
          </dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt>Last reading</dt>
          <dd className="font-medium">
            {lastReadingTimestamp
              ? new Date(lastReadingTimestamp).toLocaleString()
              : "—"}
          </dd>
        </div>
      </dl>
      {sessionError && (
        <p className="mt-2 text-xs text-red-600 dark:text-red-400">
          {sessionError}
        </p>
      )}
      {actionError && (
        <p className="mt-2 text-xs text-red-600 dark:text-red-400">
          {actionError}
        </p>
      )}
      <div className="mt-4 flex gap-2">
        {!isActive && (
          <button
            onClick={startSession}
            disabled={busy}
            className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {busy ? "Starting…" : "Start session"}
          </button>
        )}
        {isActive && (
          <button
            onClick={endSession}
            disabled={busy}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-800"
          >
            {busy ? "Ending…" : "End session"}
          </button>
        )}
      </div>
      <p className="mt-3 text-xs text-gray-400 dark:text-gray-500">
        The shared ESP8266 device authenticates with its own device token.
        Device credentials are never exposed in this dashboard.
      </p>
    </Section>
  );
}
