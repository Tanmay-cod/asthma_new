"""Patient-level split utility. Deterministic via seed."""
import numpy as np


def patient_level_split(user_keys, train_frac=0.7, val_frac=0.15, seed=42):
    users = np.array(sorted(set(user_keys)))
    rng = np.random.default_rng(seed)
    rng.shuffle(users)
    n = len(users)
    n_train = int(n * train_frac)
    n_val = int(n * val_frac)
    train = users[:n_train]
    val = users[n_train:n_train + n_val]
    test = users[n_train + n_val:]
    return {"train": set(train), "val": set(val), "test": set(test)}
