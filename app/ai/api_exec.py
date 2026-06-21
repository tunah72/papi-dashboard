"""API Thực thi: chạy code đã được người dùng duyệt, trong một namespace hạn chế.
Chỉ cung cấp bản sao read-only của dữ liệu và một số thư viện phân tích. Mọi thứ chạy tại máy.

Giao kèo với code: gán bảng kết quả vào biến `result`, biểu đồ plotly vào biến `fig` (đều tùy chọn).
"""
import io
import contextlib
import builtins
import multiprocessing as mp
import os
import __main__
import warnings

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

MAX_STDOUT_CHARS = 4000
EXEC_TIMEOUT_SECONDS = 8


def _multiprocessing_context():
    if os.name != "posix":
        return mp.get_context()
    # Streamlit/forkserver có thể import lại main script và sinh cảnh báo ScriptRunContext.
    # fork giữ app context local hơn cho use case demo chạy trên Linux.
    return mp.get_context("fork")


class _CappedStringIO(io.StringIO):
    """StringIO giới hạn dung lượng để code print vô hạn không làm đầy RAM."""

    def __init__(self, limit=MAX_STDOUT_CHARS):
        super().__init__()
        self.limit = limit
        self.truncated = False

    def write(self, s):
        current = self.tell()
        remaining = self.limit - current
        if remaining <= 0:
            self.truncated = True
            return len(s)
        if len(s) > remaining:
            self.truncated = True
            super().write(s[:remaining])
            return len(s)
        return super().write(s)


def available_names(data) -> list:
    """Danh sách tên biến code có thể dùng (thư viện + các bảng dữ liệu)."""
    return list(_LIBS.keys()) + [k for k in data]


def _make_globals(data):
    g = {"__builtins__": _SAFE_BUILTINS, **_LIBS}
    for k, v in data.items():
        g[k] = v.copy() if isinstance(v, pd.DataFrame) else v   # read-only: làm việc trên bản sao
    return g


def _execute_child(code: str, data: dict, queue):
    g = _make_globals(data)
    out = _CappedStringIO()
    err = _CappedStringIO()
    res = {"result": None, "fig": None, "stdout": "", "warnings": [], "error": None}
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                exec(code, g)
        res["result"] = g.get("result")
        res["fig"] = g.get("fig")
        res["warnings"] = [f"{w.category.__name__}: {w.message}" for w in caught]
    except Exception as e:
        res["error"] = f"{type(e).__name__}: {e}"
    stdout = out.getvalue()
    stderr = err.getvalue()
    if out.truncated:
        stdout += "\n... [đã cắt stdout do quá dài] ..."
    if stderr:
        stdout += ("\n" if stdout else "") + "[stderr]\n" + stderr
    if res["warnings"]:
        stdout += ("\n" if stdout else "") + "[warnings]\n" + "\n".join(res["warnings"])
    res["stdout"] = stdout
    queue.put(res)


def execute(code: str, data: dict, timeout: int = EXEC_TIMEOUT_SECONDS) -> dict:
    """Chạy code trong namespace hạn chế. Trả về dict gồm result, fig, stdout, error."""
    mp_context = _multiprocessing_context()
    queue = mp_context.Queue(maxsize=1)
    proc = mp_context.Process(target=_execute_child, args=(code, data, queue))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join(1)
        return {
            "result": None,
            "fig": None,
            "stdout": "",
            "warnings": [],
            "error": f"TimeoutError: Code chạy quá {timeout} giây và đã bị dừng.",
        }

    if not queue.empty():
        return queue.get()

    return {
        "result": None,
        "fig": None,
        "stdout": "",
        "warnings": [],
        "error": "RuntimeError: Tiến trình thực thi kết thúc nhưng không trả kết quả.",
    }
