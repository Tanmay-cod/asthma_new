# Model Calibration

Because predictions are presented as personalized probabilities, calibration
was evaluated.

- Method: isotonic regression fitted on **validation-set** raw probabilities,
  applied to test-set raw probabilities (never fitted on test).
- Reported: Brier score raw vs calibrated, plus confusion-matrix metrics at
  threshold 0.5 for calibrated probabilities.
- Observed: with only ~2–3 test participants and tiny validation positives,
  isotonic calibration is unstable (calibrated ROC-AUC can differ sharply from
  raw). This is reported honestly in `artifacts/aamos00/calibration_metrics.json`.
  In production, calibration must be refit on a larger validation set.

## Calibration status

`NOT_CLINICALLY_VALIDATED` — probabilities are research/development estimates,
not calibrated clinical risks.
