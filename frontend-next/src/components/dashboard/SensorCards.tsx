import Section from "./Section";
import type { LatestReadingsFallback, SensorKey } from "@/lib/types";

interface SensorCardsProps {
  latest: LatestReadingsFallback | null;
  state: "loading" | "error" | "ready" | "empty";
  error: string | null;
  stale: boolean;
}

interface CardDef {
  key: SensorKey;
  label: string;
  unit: string;
  format: (v: number) => string;
}

const CARDS: CardDef[] = [
  { key: "heart_rate", label: "Heart Rate", unit: "BPM", format: (v) => v.toFixed(0) },
  { key: "spo2", label: "SpO2", unit: "%", format: (v) => v.toFixed(0) },
  { key: "temperature_c", label: "Temperature", unit: "°C", format: (v) => v.toFixed(1) },
  { key: "humidity_percent", label: "Humidity", unit: "%", format: (v) => v.toFixed(1) },
  {
    key: "dust_indicator",
    label: "Dust indicator",
    unit: "indicator",
    format: (v) => v.toFixed(2),
  },
];

/**
 * Live sensor cards. The backend GET endpoints only return
 * non-null readings, so a missing key means "no valid reading"
 * — we never fabricate a zero.
 */
export default function SensorCards({ latest, state, error, stale }: SensorCardsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
      {CARDS.map((card) => {
        const reading = latest?.[card.key];
        const hasValue =
          reading !== undefined &&
          reading.value !== null &&
          reading.value !== undefined &&
          reading.valid !== false;
        return (
          <Section
            key={card.key}
            title={card.label}
            state={state === "ready" ? "ready" : state}
            error={error}
            emptyMessage="No valid reading"
          >
            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl font-bold text-gray-900 dark:text-white">
                {hasValue ? card.format(reading!.value!) : "—"}
              </span>
              {hasValue && (
                <span className="text-sm font-medium text-gray-400 dark:text-gray-500">
                  {card.unit}
                </span>
              )}
            </div>
            {hasValue && (
              <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                {new Date(reading!.timestamp).toLocaleTimeString()}
                {stale ? " · stale" : ""}
              </p>
            )}
          </Section>
        );
      })}
    </div>
  );
}
