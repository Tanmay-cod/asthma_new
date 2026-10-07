import Section from "./Section";
import type { PersonalizedReport, PefReading } from "@/lib/types";

interface PefSectionProps {
  report: PersonalizedReport | null;
  pefHistory: PefReading[] | null;
  state: "loading" | "error" | "ready" | "empty";
  error: string | null;
}

function Sparkline({ values }: { values: number[] }) {
  if (values.length < 2) {
    return (
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Insufficient history for trend
      </p>
    );
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const w = 240;
  const h = 56;
  const pad = 6;
  const points = values
    .map((v, i) => {
      const x = pad + (i / (values.length - 1)) * (w - 2 * pad);
      const y = h - pad - ((v - min) / span) * (h - 2 * pad);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      preserveAspectRatio="none"
      className="h-14 w-full text-blue-600 dark:text-blue-400"
      role="img"
      aria-label="Recent PEF trend"
    >
      <polyline
        points={points}
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}

export default function PefSection({
  report,
  pefHistory,
  state,
  error,
}: PefSectionProps) {
  const measurements = report?.current_measurements;
  const trend = pefHistory
    ? [...pefHistory].reverse().map((p) => p.pef_l_min)
    : report?.recent_trend.recent_pef;

  return (
    <Section
      title="PEF (Peak Expiratory Flow)"
      state={state}
      error={error}
      emptyMessage="No PEF data yet"
      className="md:col-span-2"
    >
      {measurements && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Current PEF
            </p>
            <p className="mt-1 text-3xl font-bold text-gray-900 dark:text-white">
              {measurements.current_pef != null
                ? `${measurements.current_pef.toFixed(0)}`
                : "—"}
              <span className="ml-1 text-sm font-medium text-gray-400 dark:text-gray-500">
                L/min
              </span>
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Personal Best
            </p>
            <p className="mt-1 text-3xl font-bold text-gray-900 dark:text-white">
              {measurements.personal_best_pef != null
                ? `${measurements.personal_best_pef.toFixed(0)}`
                : "—"}
              <span className="ml-1 text-sm font-medium text-gray-400 dark:text-gray-500">
                L/min
              </span>
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              PEF percentage
            </p>
            <p className="mt-1 text-3xl font-bold text-gray-900 dark:text-white">
              {measurements.pef_pct_best != null
                ? `${measurements.pef_pct_best.toFixed(1)}%`
                : "—"}
            </p>
          </div>
        </div>
      )}
      <div className="mt-4">
        <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">
          Recent PEF trend (oldest → newest)
        </p>
        {trend && trend.length > 0 ? (
          <Sparkline values={trend} />
        ) : state === "ready" ? (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Insufficient history for trend
          </p>
        ) : null}
      </div>
      <p className="mt-4 text-xs text-amber-700 dark:text-amber-400">
        Personal best should be established during a period of good/stable
        control and verified before clinical use. The stored personal best is
        shown as recorded by the backend and is not assumed to be your true
        clinical personal best.
      </p>
    </Section>
  );
}
