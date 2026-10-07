import Section from "./Section";
import type { DataQualityState } from "@/lib/types";

interface DataQualitySectionProps {
  quality: DataQualityState | null;
  state: "loading" | "error" | "ready" | "empty";
  error: string | null;
}

const STATUS_STYLES: Record<string, string> = {
  GOOD_DATA:
    "bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300",
  STALE_DATA:
    "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300",
  SENSOR_UNAVAILABLE:
    "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  INSUFFICIENT_DATA:
    "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300",
};

function Chip({ label, value }: { label: string; value: string | null }) {
  const style =
    STATUS_STYLES[value ?? ""] ??
    "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300";
  return (
    <div className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
      <span className="text-sm text-gray-600 dark:text-gray-300">
        {label}
      </span>
      <span
        className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${style}`}
      >
        {value ?? "—"}
      </span>
    </div>
  );
}

export default function DataQualitySection({
  quality,
  state,
  error,
}: DataQualitySectionProps) {
  return (
    <Section
      title="Data Quality"
      state={state}
      error={error}
      emptyMessage="No data-quality information"
    >
      <div className="space-y-2">
        <Chip label="PEFR" value={quality?.pefr ?? null} />
        <Chip label="Heart rate" value={quality?.hr ?? null} />
        <Chip label="Overall" value={quality?.overall ?? null} />
      </div>
    </Section>
  );
}
