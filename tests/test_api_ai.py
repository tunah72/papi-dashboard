"""Unit test cho hàm _parse_response trong app/ai/api_ai.py.

Chạy: pytest tests/test_api_ai.py -q
Offline — KHÔNG gọi mạng, KHÔNG cần API key.
"""
import json
import sys
from pathlib import Path

# Thêm 'app' vào sys.path để `from ai import api_ai` chạy được
# (tương tự cách test_trend.py thêm 'src')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from ai import api_ai  # noqa: E402

_parse = api_ai._parse_response


# ---------------------------------------------------------------------------
# (a) JSON sạch
# ---------------------------------------------------------------------------
def test_clean_json():
    payload = {"code": "result = df.head()", "explanation": "Lấy 5 dòng đầu"}
    text = json.dumps(payload, ensure_ascii=False)
    out = _parse(text)
    assert out["code"] == "result = df.head()"
    assert out["explanation"] == "Lấy 5 dòng đầu"


def test_clean_json_code_with_newlines():
    """JSON hợp lệ, trường code chứa ký tự xuống dòng (escaped \\n trong JSON)."""
    payload = {
        "code": "import pandas as pd\nresult = df.describe()",
        "explanation": "Thống kê mô tả",
    }
    text = json.dumps(payload, ensure_ascii=False)
    out = _parse(text)
    assert "\n" in out["code"]
    assert "result = df.describe()" in out["code"]
    assert out["explanation"] == "Thống kê mô tả"


# ---------------------------------------------------------------------------
# (b) Fence ```json ... ```
# ---------------------------------------------------------------------------
def test_json_fence():
    inner = json.dumps({"code": "result = df.shape", "explanation": "Kích thước bảng"})
    text = f"```json\n{inner}\n```"
    out = _parse(text)
    assert out["code"] == "result = df.shape"
    assert out["explanation"] == "Kích thước bảng"


def test_json_fence_with_surrounding_text():
    """Fence ```json có thêm text bên ngoài (LLM hay sinh ra)."""
    inner = json.dumps({"code": "fig = px.bar(df)", "explanation": "Biểu đồ cột"})
    text = f"Đây là kết quả:\n```json\n{inner}\n```\nXong."
    out = _parse(text)
    assert out["code"] == "fig = px.bar(df)"
    assert out["explanation"] == "Biểu đồ cột"


# ---------------------------------------------------------------------------
# (c) Fence ```python ... ```
# ---------------------------------------------------------------------------
def test_python_fence():
    code_block = "result = df.groupby('year')['total'].mean()"
    text = f"```python\n{code_block}\n```"
    out = _parse(text)
    assert out["code"] == code_block
    assert out["explanation"] == ""


def test_python_fence_multiline():
    code_block = "# Nhóm theo năm\nresult = df.groupby('year')['total'].mean()"
    text = f"```python\n{code_block}\n```"
    out = _parse(text)
    assert "Nhóm theo năm" in out["code"]
    assert out["explanation"] == ""


# ---------------------------------------------------------------------------
# (d) Text thuần (không fence) → vào code
# ---------------------------------------------------------------------------
def test_plain_text_becomes_code():
    plain = "result = df[df['province'] == 'Hà Nội']"
    out = _parse(plain)
    assert out["code"] == plain
    assert out["explanation"] == ""


def test_plain_text_multiline_no_fence():
    plain = "# lọc\nresult = df.dropna()\nprint(result)"
    out = _parse(plain)
    assert out["code"] == plain
    assert out["explanation"] == ""


# ---------------------------------------------------------------------------
# Đảm bảo không bao giờ ném lỗi (không bao giờ None cho code)
# ---------------------------------------------------------------------------
def test_empty_string_does_not_raise():
    out = _parse("")
    assert isinstance(out["code"], str)
    assert isinstance(out["explanation"], str)


def test_garbage_input_does_not_raise():
    out = _parse("!!@#$%^&* không phải JSON không phải code")
    assert isinstance(out["code"], str)
    assert out["code"] != ""  # text gốc nên được giữ lại
