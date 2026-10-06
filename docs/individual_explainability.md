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

Representative low/moderate/high and time-varying cases are produced at
inference time from the same TreeExplainer; the frontend concept in
`docs/phase8_personalized_ml.md` shows the contract. No SHAP value is
fabricated.
