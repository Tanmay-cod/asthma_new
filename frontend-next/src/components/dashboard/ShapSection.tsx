import Section from "./Section";
import type { PredictionExplanation, ShapFactor } from "@/lib/types";

interface ShapSectionProps {
  explanation: PredictionExplanation | null;
  state: "loading" | "error" | "ready" | "empty";
  error: string | null;
}

function formatShap(v: number): string {
  return `${v >= 0 ? "+" : ""}${v.toFixed(4)}`;
}

function FactorList({
  factors,
  tone,
}: {
  factors: ShapFactor[];
  tone: "up" | "down";
}) {
  if (factors.length === 0) {
    return (
      <p className="text-sm text-gray-400 dark:text-gray-500">
        No factors in this category
      </p>
    );
  }
  return (
    <ul className="divide-y divide-gray-100 text-sm dark:divide-gray-800">
      {factors.map((f) => (
        <li
          key={f.feature}
          className="flex items-center justify-between gap-2 py-1.5"
        >
          <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
            {f.feature}
          </span>
          <span
            className={`rounded px-1.5 py-0.5 font-mono text-xs font-medium ${
              tone === "up"
                ? "bg-red-50 text-red-700 dark:bg-red-900/40 dark:text-red-300"
                : "bg-green-50 text-green-700 dark:bg-green-900/40 dark:text-green-300"
            }`}
          >
            {formatShap(f.shap_value)}
          </span>
        </li>
      ))}
    </ul>
  );
}

export default function ShapSection({
  explanation,
  state,
  error,
}: ShapSectionProps) {
  const increasing = explanation?.explanation?.top_increasing ?? [];
  const decreasing = explanation?.explanation?.top_decreasing ?? [];

  return (
    <Section
      title="Why did the model produce this result?"
      subtitle="SHAP"
      state={state}
      error={error}
      emptyMessage="No explanation available"
      className="md:col-span-2 xl:col-span-2"
    >
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <h3 className="mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
            Factors increasing model score
          </h3>
          <FactorList factors={increasing} tone="up" />
        </div>
        <div>
          <h3 className="mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
            Factors decreasing model score
          </h3>
          <FactorList factors={decreasing} tone="down" />
        </div>
      </div>
      <p className="mt-4 text-xs text-gray-500 dark:text-gray-400">
        SHAP values describe model contribution and do not establish clinical
        causation.
      </p>
    </Section>
  );
}
