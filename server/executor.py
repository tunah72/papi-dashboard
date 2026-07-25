"""Thực thi cục bộ mã Python đã được người dùng phê duyệt.

Mã chạy trong một tiến trình con, chỉ nhận bản sao dữ liệu cùng các thư viện
phân tích được cho phép. Kết quả tùy chọn được gán vào ``result`` và ``fig``.
"""
from __future__ import annotations

import builtins
import contextlib
import io
import multiprocessing as mp
import os
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


_SAFE_BUILTINS = {
    name: getattr(builtins, name)
    for name in (
        "abs", "all", "any", "bool", "dict", "enumerate", "filter", "float",
        "format", "getattr", "hasattr", "int", "isinstance", "len", "list",
        "map", "max", "min", "print", "range", "repr", "round", "set",
        "sorted", "str", "sum", "tuple", "type", "zip",
    )
}

_LIBS = {
    "pd": pd,
    "np": np,
    "px": px,
    "go": go,
    "stats": stats,
    "KMeans": KMeans,
    "StandardScaler": StandardScaler,
    "silhouette_score": silhouette_score,
}

MAX_STDOUT_CHARS = 4000
EXEC_TIMEOUT_SECONDS = 8


def _multiprocessing_context():
    if os.name != "posix":
        return mp.get_context()
    return mp.get_context("fork")


class _CappedStringIO(io.StringIO):
    """Bộ đệm giới hạn dung lượng để tránh stdout quá lớn."""

    def __init__(self, limit=MAX_STDOUT_CHARS):
        super().__init__()
        self.limit = limit
        self.truncated = False

    def write(self, value):
        remaining = self.limit - self.tell()
        if remaining <= 0:
            self.truncated = True
            return len(value)
        if len(value) > remaining:
            self.truncated = True
            super().write(value[:remaining])
            return len(value)
        return super().write(value)


def available_names(data) -> list[str]:
    """Trả các tên thư viện và bảng dữ liệu mà mã được phép sử dụng."""
    return list(_LIBS) + list(data)


def _make_globals(data):
    namespace = {"__builtins__": _SAFE_BUILTINS, **_LIBS}
    for name, value in data.items():
        namespace[name] = value.copy() if isinstance(value, pd.DataFrame) else value
    return namespace


def _execute_child(code: str, data: dict, queue):
    namespace = _make_globals(data)
    stdout_buffer = _CappedStringIO()
    stderr_buffer = _CappedStringIO()
    response = {
        "result": None,
        "fig": None,
        "stdout": "",
        "warnings": [],
        "error": None,
    }
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with (
                contextlib.redirect_stdout(stdout_buffer),
                contextlib.redirect_stderr(stderr_buffer),
            ):
                exec(code, namespace)
        response["result"] = namespace.get("result")
        response["fig"] = namespace.get("fig")
        response["warnings"] = [
            f"{warning.category.__name__}: {warning.message}"
            for warning in caught
        ]
    except Exception as exc:
        response["error"] = f"{type(exc).__name__}: {exc}"

    stdout = stdout_buffer.getvalue()
    stderr = stderr_buffer.getvalue()
    if stdout_buffer.truncated:
        stdout += "\n... [đã cắt stdout do quá dài] ..."
    if stderr:
        stdout += ("\n" if stdout else "") + "[stderr]\n" + stderr
    if response["warnings"]:
        stdout += (
            ("\n" if stdout else "")
            + "[warnings]\n"
            + "\n".join(response["warnings"])
        )
    response["stdout"] = stdout
    queue.put(response)


def execute(code: str, data: dict, timeout: int = EXEC_TIMEOUT_SECONDS) -> dict:
    """Chạy mã trong tiến trình con và trả kết quả, cảnh báo hoặc lỗi."""
    mp_context = _multiprocessing_context()
    queue = mp_context.Queue(maxsize=1)
    process = mp_context.Process(target=_execute_child, args=(code, data, queue))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join(1)
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
