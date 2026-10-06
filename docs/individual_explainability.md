# Individual Explainability

Every prediction carries SHAP-based explanation for that user:

- Predicted probability (0–1)
- Risk level: LOW/MODERATE/HIGH (configurable)
- Top positive contributors (features increasing risk)
- Top negative contributors (protective factors)
- Feature values + SHAP contributions

Language rule: "contributed to the model prediction" — never
"caused your asthma to worsen". Descriptions are per-user, using their actual
values and personal-best comparison.

## Global explanation

See `artifacts/aamos00/shap_global_importance.csv` (mean |SHAP| per feature).

## Individual cases

Persisted per Phase 8.1 in:

- `artifacts/aamos00/shap_individual_examples.csv`
- `artifacts/aamos00/shap_individual_examples.json`

Cases: low-risk, moderate-risk, high-risk, and a time-varying participant where
present. Missing categories are recorded as `NOT AVAILABLE IN DATA`; no
explanations are fabricated.
