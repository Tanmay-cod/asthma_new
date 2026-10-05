# Dataset Split Strategy

- **Unit of splitting:** `user_key` (participant), never rows.
- Deterministic: seeded shuffle (`dataset.patient_level_split(seed=42)`).
- Default: 70% train / 15% validation / 15% test by participant.
- A participant never appears in two partitions; enforced by
  `leakage.assert_user_partition_disjoint`.
- Temporal order is preserved within each participant's rows.
- Alternative: GroupKFold by `user_key` for small-N evaluation.
- Preprocessors (imputers, encoders, scalers) must be **fit on train only**;
  trigger vocabulary (`features.encode_triggers(vocab=None)`) must be built
  from the training partition only.
