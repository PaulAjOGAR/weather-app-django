from typing import Dict, List, Tuple

import math

import numpy as np


def compute_stats(values: List[float]) -> Dict[str, float]:
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return {"mean": math.nan, "variance": math.nan, "std": math.nan}
    return {
        "mean": float(np.nanmean(arr)),
        "variance": float(np.nanvar(arr, ddof=0)),
        "std": float(np.nanstd(arr, ddof=0)),
    }


def detect_anomalies(values: List[float], z_threshold: float = 2.5) -> List[bool]:
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return []
    mu = np.nanmean(arr)
    sigma = np.nanstd(arr)
    if sigma == 0 or np.isnan(sigma):
        return [False] * arr.size
    z = (arr - mu) / sigma
    return [bool(abs(val) > z_threshold) for val in z]
