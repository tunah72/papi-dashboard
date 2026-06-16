"""API Thực thi: chạy code đã được người dùng duyệt, trong một namespace hạn chế.
Chỉ cung cấp bản sao read-only của dữ liệu và một số thư viện phân tích. Mọi thứ chạy tại máy.

Giao kèo với code: gán bảng kết quả vào biến `result`, biểu đồ plotly vào biến `fig` (đều tùy chọn).
"""
import io
import contextlib
import builtins

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from scipy import stats

# Builtins an toàn (loại open, exec, eval, __import__, compile, input...)
_SAFE_BUILTINS = {k: getattr(builtins, k) for k in (
    "abs", "all", "any", "bool", "dict", "enumerate", "filter", "float", "format",
    "getattr", "hasattr", "int", "isinstance", "len", "list", "map", "max", "min",
    "print", "range", "repr", "round", "set", "sorted", "str", "sum", "tuple", "type", "zip",
)}

# Các tên có sẵn cho code (ngoài các DataFrame của dữ liệu)
_LIBS = {"pd": pd, "np": np, "px": px, "go": go, "stats": stats,
         "KMeans": KMeans, "StandardScaler": StandardScaler, "silhouette_score": silhouette_score}


def available_names(data) -> list:
    """Danh sách tên biến code có thể dùng (thư viện + các bảng dữ liệu)."""
    return list(_LIBS.keys()) + [k for k in data]


def _make_globals(data):
    g = {"__builtins__": _SAFE_BUILTINS, **_LIBS}
    for k, v in data.items():
        g[k] = v.copy() if isinstance(v, pd.DataFrame) else v   # read-only: làm việc trên bản sao
    return g


def execute(code: str, data: dict) -> dict:
    """Chạy code trong namespace hạn chế. Trả về dict gồm result, fig, stdout, error."""
    g = _make_globals(data)
    out = io.StringIO()
    res = {"result": None, "fig": None, "stdout": "", "error": None}
    try:
        with contextlib.redirect_stdout(out):
            exec(code, g)
        res["result"] = g.get("result")
        res["fig"] = g.get("fig")
    except Exception as e:
        res["error"] = f"{type(e).__name__}: {e}"
    res["stdout"] = out.getvalue()
    return res
