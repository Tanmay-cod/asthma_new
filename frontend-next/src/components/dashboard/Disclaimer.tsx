import type { PersonalizedReport } from "@/lib/types";

export default function Disclaimer({
  report,
}: {
  report: PersonalizedReport | null;
}) {
  const safety =
    report?.safety ??
    "This is a research/development decision-support system. It is not a diagnosis and does not establish that an asthma exacerbation will occur. It does not replace clinical assessment and does not provide medication or treatment instructions.";
  return (
    <footer className="rounded-xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-900">
      <p className="text-sm text-gray-600 dark:text-gray-300">{safety}</p>
      <p className="mt-2 text-sm font-medium text-gray-700 dark:text-gray-200">
        Clinical validation: PENDING
      </p>
      <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
        Research/development prototype. Model outputs are monitoring signals
        only and must not be used for diagnosis or treatment decisions.
      </p>
    </footer>
  );
}
