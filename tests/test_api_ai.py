"""Unit test cho hàm _parse_response trong app/ai/api_ai.py.

Chạy: pytest tests/test_api_ai.py -q
Offline — KHÔNG gọi mạng, KHÔNG cần API key.
"""
import json
import sys
import types
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


def test_loose_json_with_raw_newlines_in_code():
    text = '''{
  "code": "
# Lọc dữ liệu
result = prov_year.head()
",
  "explanation": "Lấy vài dòng đầu."
}'''
    out = _parse(text)
    assert out["code"] == "# Lọc dữ liệu\nresult = prov_year.head()"
    assert out["explanation"] == "Lấy vài dòng đầu."


def test_sanitize_code_payload_extracts_code_from_json_like_text():
    payload = '''{
  "code": "
result = prov_year.head()
",
  "explanation": "ok"
}'''
    assert api_ai.sanitize_code_payload(payload) == "result = prov_year.head()"


def test_sanitize_code_payload_keeps_plain_code():
    code = "result = prov_year.head()"
    assert api_ai.sanitize_code_payload(code) == code


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


def test_format_context_empty():
    assert api_ai._format_context(None) == ""
    assert api_ai._format_context({}) == ""


def test_format_context_legacy_schema():
    text = api_ai._format_context({
        "page": "Diễn biến theo thời gian",
        "scale_mode": "6 lĩnh vực",
        "total_col": "total_papi_6dim",
        "dims": {"D1": "Tham gia", "D2": "Minh bạch"},
        "year_range": [2011, 2024],
    })
    assert "Diễn biến theo thời gian" in text
    assert "total_papi_6dim" in text
    assert "2011 đến 2024" in text
    assert "Tham gia" in text


def test_format_context_new_schema():
    text = api_ai._format_context({
        "page": "Tổng quan",
        "filters": {"year": 2024, "province": "Hà Nội"},
        "data_scope": {"table": "prov_year", "score_column": "total_papi"},
        "chart_id": "Bản đồ PAPI",
    })
    assert "Tổng quan" in text
    assert "year=2024" in text
    assert "province=Hà Nội" in text
    assert "score_column=total_papi" in text
    assert "Bản đồ PAPI" in text


def test_build_prompt_includes_groq_ready_constraints():
    prompt = api_ai._build_prompt(
        "Tính trung bình",
        {"prov_year": object()},
        context={"page": "Tổng quan", "year": 2024},
        system_instruction="Luôn dùng bảng prov_year.",
    )
    assert "KHÔNG sử dụng câu lệnh `import`" in prompt
    assert "GROQ_API_KEY" not in prompt
    assert "Luôn dùng bảng prov_year." in prompt
    assert "Tính trung bình" in prompt


def test_generate_uses_groq_chat_completion(monkeypatch):
    calls = {}

    class _Message:
        content = '{"code": "result = prov_year.head()", "explanation": "ok"}'

    class _Choice:
        message = _Message()

    class _Completions:
        def create(self, **kwargs):
            calls.update(kwargs)
            return types.SimpleNamespace(choices=[_Choice()])

    class _Chat:
        completions = _Completions()

    class _Groq:
        def __init__(self, api_key):
            calls["api_key"] = api_key
            self.chat = _Chat()

    fake_groq = types.SimpleNamespace(Groq=_Groq)
    monkeypatch.setitem(sys.modules, "groq", fake_groq)
    monkeypatch.setattr(api_ai, "_get_groq_api_key", lambda: "test-key")

    out = api_ai.generate("Lấy mẫu", {"prov_year": object()})

    assert calls["api_key"] == "test-key"
    assert calls["model"] == api_ai.DEFAULT_MODEL
    assert calls["messages"][0]["role"] == "user"
    assert out["code"] == "result = prov_year.head()"
