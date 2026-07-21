"""Dịch output pandas/numpy sang view-model JSON an toàn cho UI."""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


SCHEMA_VERSION = "v1"
SOURCE = "PAPI Việt Nam — UNDP, CECODES và RTA"


def json_safe(value: Any) -> Any:
    """Đổi NaN/Infinity và scalar numpy/pandas thành JSON hợp lệ."""
    if value is None or value is pd.NA:
        return None
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (float, np.floating)):
        value = float(value)
        return value if math.isfinite(value) else None
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return json_safe(frame.to_dict(orient="records"))


def response(data: dict[str, Any], *, n: int, filters: dict[str, Any], unit="điểm PAPI", caveats=None):
    return {
        "meta": {
            "schemaVersion": SCHEMA_VERSION,
            "source": SOURCE,
            "unit": unit,
            "n": int(n),
            "caveats": caveats or [],
            "filters": json_safe(filters),
        },
        "data": json_safe(data),
    }
