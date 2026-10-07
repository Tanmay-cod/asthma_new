import type { ReactNode } from "react";

type SectionState = "loading" | "error" | "ready" | "empty" | "idle";

interface SectionProps {
  title: string;
  subtitle?: string;
  state?: SectionState;
  error?: string | null;
  emptyMessage?: string;
  className?: string;
  children: ReactNode;
}

/** Card wrapper with consistent loading / error / empty states. */
export default function Section({
  title,
  subtitle,
  state = "ready",
  error,
  emptyMessage = "No data available",
  className = "",
  children,
}: SectionProps) {
  return (
    <section
      className={`rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900 ${className}`}
    >
      <div className="flex items-baseline justify-between gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
          {title}
        </h2>
        {subtitle && (
          <span className="text-xs text-gray-400 dark:text-gray-500">
            {subtitle}
          </span>
        )}
      </div>
      <div className="mt-3">
        {state === "loading" && (
          <p className="text-sm text-gray-400 dark:text-gray-500">Loading…</p>
        )}
        {state === "error" && (
          <p className="text-sm text-red-600 dark:text-red-400">
            {error ?? "Failed to load"}
          </p>
        )}
        {state === "empty" && (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {emptyMessage}
          </p>
        )}
        {state === "ready" && children}
      </div>
    </section>
  );
}
