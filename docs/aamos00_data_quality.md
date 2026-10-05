# AAMOS-00 Data Quality Report

All checks below are implemented in `backend/app/ml/data_validation.py` and
executed on every pipeline run.

## Checks performed

- Required columns present per table
- No null `user_key` / `date`
- Dates within 0..400
- `pef_max ∈ [0,900]`, `temperature ∈ [-40,60]`, `humidity ∈ [0,100]`, `hr ∈ [20,250]`
- Duplicate-row counts per table
- Missingness summary per column
- Participant coverage and row counts
- Referential integrity implied by shared `user_key` / `date`

## Key findings (from latest run)

- 10 files, all loadable; inventory + validation reports in `artifacts/aamos00/`.
- `smartwatch*.hr` missing 18–33% (see `data_inventory.json`).
- `peakflow.pefs` 11.4% missing; `weekly_*` symptom fields 10–54% missing.
- `weekly_hospital/er/doc` use 0 / negative day-offset encoding (confirmed from
  the official dictionary) — parsed cautiously in target analysis.
- 6 of 22 participants have no PEF sessions → excluded from PEF-based dataset
  (cold-start rows removed = 16 after baseline requirement).
- Duplicate full rows reported as warnings, not silently deduplicated.

See `artifacts/aamos00/data_validation_report.json` for the machine-readable report.
