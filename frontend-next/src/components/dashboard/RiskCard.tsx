import Section from "./Section";
import type { PersonalizedReport } from "@/lib/types";

interface RiskCardProps {
  report: PersonalizedReport | null;
  state: "loading" | "error" | "ready" | "empty";
  error: string | null;
}

const LEVEL_STYLES: Record<string, string> = {
  low: "bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300",
  moderate:
    "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300",
  high: "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300",
};

export default function RiskCard({ report, state, error }: RiskCardProps) {
  const prediction = report?.model_prediction;
  const riskPct =
    prediction?.risk_probability != null
      ? (prediction.risk_probability * 100).toFixed(2)
      : null;
  const level = prediction?.risk_level;

  return (
    <Section
      title="Personalized Risk"
      state={state}
      error={error}
      emptyMessage="No prediction yet"
      className="md:col-span-2 xl:col-span-1"
    >
      <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
        7-Day PEF Deterioration Risk
      </p>
      <div className="mt-2 flex flex-wrap items-end gap-3">
        <p className="text-5xl font-bold tracking-tight text-gray-900 dark:text-white">
          {riskPct !== null ? `${riskPct}%` : "—"}
        </p>
        {level && (
          <span
            className={`mb-1.5 rounded-full px-3 py-1 text-sm font-semibold uppercase tracking-wide ${
              LEVEL_STYLES[level] ?? "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
            }`}
          >
            {level}
          </span>
        )}
      </div>
      <dl className="mt-4 space-y-1 text-sm text-gray-600 dark:text-gray-300">
        <div className="flex justify-between gap-2">
          <dt>Prediction horizon</dt>
          <dd className="font-medium">
            {prediction?.horizon_days ?? "—"} days
          </dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt>Model</dt>
          <dd className="font-medium">{prediction?.model_version ?? "—"}</dd>
        </div>
      </dl>
      <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
        Target: {prediction?.target ?? "—"}
      </p>
      <p className="mt-3 rounded-md bg-blue-50 px-3 py-2 text-xs text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">
        This is a PEF deterioration risk/monitoring signal. It is not an
        asthma attack or exacerbation prediction, not a diagnosis, and not a
        clinical decision or treatment recommendation.
      </p>
    </Section>
  );
}
