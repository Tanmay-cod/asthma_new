import Section from "./Section";
import type { PredictionSummary, RiskLevel } from "@/lib/types";

interface PredictionHistoryProps {
  history: PredictionSummary[] | null;
  state: "loading" | "error" | "ready" | "empty";
  error: string | null;
}

const LEVEL_STYLES: Record<string, string> = {
  low: "text-green-700 dark:text-green-400",
  moderate: "text-amber-700 dark:text-amber-400",
  high: "text-red-700 dark:text-red-400",
};

export default function PredictionHistory({
  history,
  state,
  error,
}: PredictionHistoryProps) {
  const rows = history ?? [];
  return (
    <Section
      title="Prediction History"
      state={rows.length === 0 && state === "ready" ? "empty" : state}
      error={error}
      emptyMessage="No predictions yet"
      className="md:col-span-2 xl:col-span-2"
    >
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-gray-100 text-xs uppercase tracking-wide text-gray-500 dark:border-gray-800 dark:text-gray-400">
              <th className="py-2 pr-4 font-medium">Date / Time</th>
              <th className="py-2 pr-4 font-medium">Risk</th>
              <th className="py-2 pr-4 font-medium">Risk Level</th>
              <th className="py-2 font-medium">Model</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
            {rows.map((p) => (
              <tr key={p.prediction_id}>
                <td className="py-2 pr-4 text-gray-700 dark:text-gray-300">
                  {new Date(p.prediction_time).toLocaleString()}
                </td>
                <td className="py-2 pr-4 font-medium text-gray-900 dark:text-white">
                  {(p.risk_score * 100).toFixed(2)}%
                </td>
                <td
                  className={`py-2 pr-4 font-semibold uppercase text-xs ${
                    LEVEL_STYLES[p.risk_level as RiskLevel] ?? ""
                  }`}
                >
                  {p.risk_level}
                </td>
                <td className="py-2 font-mono text-xs text-gray-500 dark:text-gray-400">
                  {p.model_version}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Section>
  );
}
