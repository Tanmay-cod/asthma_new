# Model Evaluation

Models: Logistic Regression (balanced), Random Forest (balanced), XGBoost.
All with reproducible seed 42, participant-level disjoint splits, preprocessing
fit on train only.

## Metrics used

ROC-AUC, PR-AUC, sensitivity, specificity, F1, Brier score (raw and calibrated).

## Results

See `artifacts/aamos00/model_comparison.csv` and `model_metrics.json`.
Selection is not by ROC-AUC alone — see `docs/model_selection.md`.

## Limitations

- Only 15 participants in the pipeline; test partition is small.
- Overlapping target windows make row-level estimates optimistic.
- No external validation; development model only.
