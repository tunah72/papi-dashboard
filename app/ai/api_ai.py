"""API AI: nhận yêu cầu ngôn ngữ tự nhiên + context (schema dữ liệu), gọi Gemini,
trả về code Python kèm giải thích. Code ở trạng thái CHỜ DUYỆT, không tự thực thi.

Cần GEMINI_API_KEY trong .streamlit/secrets.toml (lấy free tại aistudio.google.com).
"""
import json
import re

from ai import api_exec

DEFAULT_MODEL = "gemini-2.5-flash"

_SYSTEM = """Bạn là trợ lý phân tích dữ liệu PAPI. Hãy sinh code Python để trả lời yêu cầu của người dùng.

Quy tắc bắt buộc:
- KHÔNG dùng câu lệnh import. Chỉ dùng các tên đã có sẵn: {names}.
- Các DataFrame có sẵn được mô tả ở phần SCHEMA bên dưới.
- Gán bảng kết quả vào biến `result` (pandas DataFrame/Series). Nếu có biểu đồ, gán plotly figure vào biến `fig`.
- Thêm comment tiếng Việt giải thích từng bước (đề bài yêu cầu giải thích bằng ngôn ngữ tự nhiên).
- Không sửa dữ liệu gốc; chỉ đọc.

Trả về DUY NHẤT một JSON object dạng: {{"code": "<python>", "explanation": "<giải thích ngắn bằng tiếng Việt>"}}.
"""


def build_schema_context(data) -> str:
    """Mô tả các bảng và cột để LLM sinh code đúng."""
    import pandas as pd
    lines = ["SCHEMA các bảng dữ liệu (đều là pandas DataFrame, trừ geojson):"]
    for k, v in data.items():
        if isinstance(v, pd.DataFrame):
            lines.append(f"- {k}: cột = {list(v.columns)}")
        else:
            lines.append(f"- {k}: GeoJSON 63 tỉnh (join theo properties.province_id)")
    return "\n".join(lines)


def _parse_response(text: str) -> dict:
    """Tách JSON {code, explanation} từ phản hồi của LLM.

    Thử theo thứ tự ưu tiên — KHÔNG BAO GIỜ ném ngoại lệ:
    (a) JSON sạch → json.loads trực tiếp.
    (b) Fence ```json ... ``` → bóc nội dung rồi json.loads.
    (c) Fence ```python ... ``` → coi là code, explanation="".
    (d) Không khớp gì → code = text.strip(), explanation="".

    Luôn trả {"code": str, "explanation": str}; "code" không bao giờ là None.
    """
    # (a) Thử parse JSON sạch trước
    stripped = text.strip()
    try:
        obj = json.loads(stripped)
        return {
            "code": str(obj.get("code") or ""),
            "explanation": str(obj.get("explanation") or ""),
        }
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    # (b) Thử bóc fence ```json ... ```
    m_json = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m_json:
        try:
            obj = json.loads(m_json.group(1))
            return {
                "code": str(obj.get("code") or ""),
                "explanation": str(obj.get("explanation") or ""),
            }
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    # (c) Thử bóc fence ```python ... ``` → lấy làm code
    m_py = re.search(r"```python\s*(.*?)\s*```", text, re.DOTALL)
    if m_py:
        return {"code": m_py.group(1).strip(), "explanation": ""}

    # (d) Không khớp gì → toàn bộ text là code
    return {"code": stripped, "explanation": ""}


def generate(request: str, data: dict, model: str = DEFAULT_MODEL) -> dict:
    """Gọi Gemini sinh code + giải thích. Trả về {code, explanation}.
    Ném RuntimeError nếu thiếu SDK hoặc API key."""
    import streamlit as st
    try:
        from google import genai
    except ImportError:
        raise RuntimeError("Chưa cài google-genai. Chạy: pip install google-genai")

    key = st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") else None
    if not key:
        raise RuntimeError("Chưa có GEMINI_API_KEY trong .streamlit/secrets.toml")

    names = ", ".join(api_exec.available_names(data))
    prompt = (_SYSTEM.format(names=names) + "\n\n" + build_schema_context(data)
              + "\n\nYêu cầu của người dùng: " + request)

    client = genai.Client(api_key=key)
    resp = client.models.generate_content(model=model, contents=prompt)
    return _parse_response(resp.text)
