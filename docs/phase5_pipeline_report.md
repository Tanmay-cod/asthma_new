# Phase 5 Pipeline Report

1. Files created: backend/app/ml/{ingestion,data_validation,aggregation,baselines,features,labels,dataset,leakage,pipeline}.py, backend/app/tests/test_ml_pipeline.py, docs/{ml_data_pipeline,aamos00_data_quality,dataset_split_strategy,phase5_pipeline_report}.md, artifacts/aamos00/{data_inventory.json,data_validation_report.json,feature_metadata.json,dataset_summary.json,feature_matrix.parquet}
2. Participants: 15
3. Usable prediction rows: 1083
4. Features: 38
5. Coverage: PEF 1083, HR 938, symptoms 928, medication 928, environment 963; cold-start rows removed 16
6. Candidate target config (dev only): {'threshold_pct': 80, 'consecutive_days': 2, 'prediction_horizon_days': 7, 'baseline_method': 'expanding_max'}
7. Leakage tests passed: 10/10
8. Unit tests passed: 13/13 (incl. API tests)
9. Known limitations: SpO2 and dust excluded (documented); weekly fields parsed as timing fields; 6 users lack PEF; HR missing 18-33% in source; trigger vocab top-5 + unknown bucket.
10. Blocked: any model training until clinical target validation.

MODEL TRAINING BLOCKED — CLINICAL TARGET DEFINITION NOT YET VALIDATED