interface HeaderProps {
  systemStatus: string | null;
  backendUnreachable: boolean;
  sessionStatus: string;
  lastUpdated: string | null;
  email: string;
  onSignOut: () => void;
}

function StatusDot({ ok, pulse }: { ok: boolean; pulse?: boolean }) {
  return (
    <span
      className={`inline-block h-2 w-2 rounded-full ${
        ok ? "bg-green-500" : "bg-gray-400"
      } ${pulse ? "animate-pulse" : ""}`}
      aria-hidden
    />
  );
}

export default function Header({
  systemStatus,
  backendUnreachable,
  sessionStatus,
  lastUpdated,
  email,
  onSignOut,
}: HeaderProps) {
  return (
    <header className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Asthma Monitoring Dashboard
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Personalized PEF Deterioration Risk Monitoring
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1 text-sm">
            <span className="flex items-center gap-1.5 text-gray-600 dark:text-gray-300">
              <StatusDot
                ok={!backendUnreachable && systemStatus === "ok"}
                pulse={!backendUnreachable}
              />
              System status:{" "}
              {backendUnreachable
                ? "Backend unreachable"
                : systemStatus ?? "checking…"}
            </span>
            <span className="flex items-center gap-1.5 text-gray-600 dark:text-gray-300">
              <StatusDot ok={sessionStatus === "ACTIVE"} />
              Measurement session: {sessionStatus}
            </span>
            <span className="text-gray-600 dark:text-gray-300">
              Last updated:{" "}
              {lastUpdated
                ? new Date(lastUpdated).toLocaleTimeString()
                : "—"}
            </span>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
            {email}
          </p>
          <button
            onClick={onSignOut}
            className="mt-1 text-xs text-blue-600 hover:underline dark:text-blue-400"
          >
            Sign out
          </button>
          <p className="mt-2 inline-block rounded bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
            Research / Development Prototype
          </p>
          <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
            Clinical validation status: PENDING
          </p>
        </div>
      </div>
    </header>
  );
}
