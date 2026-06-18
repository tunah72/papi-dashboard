"""API AI: nhận yêu cầu ngôn ngữ tự nhiên + context (schema dữ liệu), gọi Groq,
trả về code Python kèm giải thích. Code ở trạng thái CHỜ DUYỆT, không tự thực thi.

Cần GROQ_API_KEY trong .streamlit/secrets.toml hoặc biến môi trường.
"""
import json
import os
import re

from ai import api_exec

DEFAULT_MODEL = "llama-3.3-70b-versatile"

_SYSTEM = """<role>
Bạn là chuyên gia khoa học dữ liệu và phân tích dữ liệu PAPI (Chỉ số Hiệu quả Quản trị và Hành chính công cấp tỉnh tại Việt Nam). 
Nhiệm vụ của bạn là sinh ra mã Python an toàn, chính xác để giải quyết yêu cầu phân tích dữ liệu từ người dùng.
</role>

<constraints>
- KHÔNG sử dụng câu lệnh `import`. Chỉ sử dụng các thư viện và biến đã được cung cấp sẵn trong môi trường: {names}.
- Các DataFrame có sẵn được cung cấp cấu trúc trong phần `<schema>`. Bạn chỉ được ĐỌC dữ liệu, tuyệt đối KHÔNG SỬA dữ liệu gốc.
- BẮT BUỘC gán bảng kết quả (pandas DataFrame hoặc Series) vào biến có tên là `result`. 
- Nếu có yêu cầu vẽ biểu đồ, BẮT BUỘC gán đối tượng plotly figure vào biến có tên là `fig`.
- Code phải chứa các comment tiếng Việt giải thích từng bước logic (vì hệ thống sẽ trích xuất và hiển thị các bước này cho người dùng).
- CẢNH BÁO KIỂU DỮ LIỆU: Tuyệt đối KHÔNG ép kiểu dữ liệu sang số nguyên bằng lệnh `.astype(int)` vì dữ liệu thực tế có thể chứa giá trị NaN gây lỗi `IntCastingNaNError`. Hãy giữ nguyên kiểu số thực (float) hoặc sử dụng `pd.Int64Dtype()` nếu bắt buộc phải dùng số nguyên.
- Khi lọc DataFrame rồi cần gán cột mới, BẮT BUỘC gọi `.copy()` ngay sau bước lọc và dùng `.loc[:, "ten_cot"] = ...` để tránh `SettingWithCopyWarning`.
- Không dùng vòng lặp vô hạn, không in toàn bộ DataFrame lớn. Nếu cần kiểm tra dữ liệu mẫu, dùng `.head()` hoặc bảng tổng hợp.
- Không đọc/ghi file, không gọi mạng, không dùng `open`, `exec`, `eval`, `__import__`, `input`.
- Nếu dữ liệu không đủ để phân tích, vẫn gán `result` là một DataFrame giải thích lý do thay vì để code crash.
</constraints>

<output_format>
Bạn phải trả về DUY NHẤT một chuỗi JSON hợp lệ với cấu trúc sau, không có bất kỳ văn bản nào nằm ngoài khối JSON này:
{{
  "code": "<Mã Python thực thi>",
  "explanation": "<Một đoạn văn ngắn gọn (2-3 câu) bằng tiếng Việt giải thích phương pháp bạn vừa dùng>"
}}
</output_format>
"""


def build_schema_context(data) -> str:
    """Mô tả các bảng và cột để LLM sinh code đúng."""
    import pandas as pd
    lines = ["<schema>"]
    lines.append("Dưới đây là cấu trúc các bảng dữ liệu có sẵn trong bộ nhớ (đều là pandas DataFrame, ngoại trừ bảng geojson):")
    for k, v in data.items():
        if isinstance(v, pd.DataFrame):
            lines.append(f"- Biến `{k}`: các cột = {list(v.columns)}")
        else:
            lines.append(f"- Biến `{k}`: GeoJSON 63 tỉnh (join với dữ liệu qua trường `properties.province_id`)")
    lines.append("</schema>")
    return "\n".join(lines)


def _parse_response(text: str) -> dict:
    """Tách JSON {code, explanation} từ phản hồi LLM.

    Hàm này cố tình không ném lỗi để UI luôn hiển thị được thứ model trả về:
    JSON sạch -> fence json -> fence python -> text thuần.
    """
    stripped = (text or "").strip()

    try:
        obj = json.loads(stripped)
        return {
            "code": str(obj.get("code") or ""),
            "explanation": str(obj.get("explanation") or ""),
        }
    except (json.JSONDecodeError, ValueError, TypeError, AttributeError):
        pass

    m_json = re.search(r"```json\s*(\{.*?\})\s*```", stripped, re.DOTALL)
    if m_json:
        try:
            obj = json.loads(m_json.group(1))
            return {
                "code": str(obj.get("code") or ""),
                "explanation": str(obj.get("explanation") or ""),
            }
        except (json.JSONDecodeError, ValueError, TypeError, AttributeError):
            pass

    m_py = re.search(r"```python\s*(.*?)\s*```", stripped, re.DOTALL)
    if m_py:
        return {"code": m_py.group(1).strip(), "explanation": ""}

    # Một số model trả JSON-looking nhưng nhét newline thô trong chuỗi "code",
    # khiến json.loads không parse được. Bóc thủ công để vẫn giữ được code.
    m_loose = re.search(
        r'"code"\s*:\s*"(.*?)"\s*,\s*"explanation"\s*:\s*"(.*?)"',
        stripped,
        re.DOTALL,
    )
    if m_loose:
        return {
            "code": m_loose.group(1).strip(),
            "explanation": m_loose.group(2).strip(),
        }

    return {"code": stripped, "explanation": ""}


def sanitize_code_payload(text: str) -> str:
    """Nếu text area còn chứa JSON payload LLM, bóc riêng trường code.

    Dùng như lớp bảo vệ cuối trước khi lưu/chạy code, để session cũ hoặc model
    trả JSON không chuẩn không bị đưa thẳng vào `exec`.
    """
    if not isinstance(text, str):
        return ""
    stripped = text.strip()
    if not stripped:
        return ""
    looks_like_payload = stripped.startswith("{") and '"code"' in stripped
    if not looks_like_payload:
        return text
    parsed = _parse_response(stripped)
    code = parsed.get("code", "")
    if code and code != stripped:
        return code
    return text


def _format_context_value(value):
    if value is None:
        return None
    if isinstance(value, dict):
        parts = []
        for key, val in value.items():
            formatted = _format_context_value(val)
            if formatted not in (None, ""):
                parts.append(f"{key}={formatted}")
        return "; ".join(parts)
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(v) for v in value)
    return str(value)


def _format_context(context) -> str:
    """Định dạng ngữ cảnh dashboard thành chuỗi đưa vào prompt.

    Nếu context là None hoặc rỗng → trả "".
    """
    if not context or not isinstance(context, dict):
        return ""

    lines = ["<dashboard_context>"]
    lines.append("Người dùng hiện đang xem dashboard với các bộ lọc sau (hãy ưu tiên sử dụng thông tin này nếu yêu cầu của người dùng bị mờ hồ):")

    # Schema mới: page, filters, data_scope, chart_id.
    if context.get("filters") and isinstance(context["filters"], dict):
        formatted = _format_context_value(context["filters"])
        if formatted:
            lines.append(f"- Bộ lọc: {formatted}")
    if context.get("data_scope"):
        lines.append(f"- Phạm vi dữ liệu: {_format_context_value(context['data_scope'])}")
    if context.get("chart_id"):
        lines.append(f"- Biểu đồ đang hỏi: {context['chart_id']}")

    # Schema cũ: các key top-level đang được page hiện tại publish.
    mapping = {
        "page": "Trang hiện tại",
        "scale_mode": "Phạm vi so sánh",
        "total_col": "Cột tổng điểm đang dùng",
        "province": "Tỉnh/Thành phố",
        "region": "Vùng địa lý",
    }

    for key, label in mapping.items():
        if key in context and context[key]:
            lines.append(f"- {label}: {context[key]}")

    # Xử lý lĩnh vực (dims)
    if "dims" in context and isinstance(context["dims"], dict):
        dims_str = ", ".join(context["dims"].values())
        if dims_str:
            lines.append(f"- Các lĩnh vực đang hiển thị: {dims_str}")

    # Xử lý thời gian (year_range hoặc year đơn lẻ)
    if "year_range" in context and isinstance(context["year_range"], (list, tuple)) and len(context["year_range"]) >= 2:
        lines.append(f"- Khoảng năm đang chọn: {context['year_range'][0]} đến {context['year_range'][1]}")
    elif "year" in context:
        lines.append(f"- Năm đang chọn: {context['year']}")

    lines.append("</dashboard_context>")
    return "\n".join(lines) if len(lines) > 2 else ""


def _build_prompt(request: str, data: dict, context=None, system_instruction=None) -> str:
    """Ghép prompt đầy đủ để gọi LLM. Tách riêng để test offline."""
    names = ", ".join(api_exec.available_names(data))

    # 1. Khởi tạo Base Prompt (Role, Constraints, Output Format)
    prompt = _SYSTEM.format(names=names) + "\n\n"

    # 2. Thêm Schema dữ liệu
    prompt += build_schema_context(data) + "\n\n"

    # 3. Thêm Dashboard Context (Nếu có)
    context_part = _format_context(context)
    if context_part:
        prompt += context_part + "\n\n"

    # 4. Thêm Hướng dẫn kỹ thuật riêng của Plugin (Nếu có)
    if system_instruction:
        prompt += "<plugin_instruction>\nĐây là quy trình chuyên môn cụ thể bạn PHẢI áp dụng cho yêu cầu này:\n"
        prompt += system_instruction + "\n</plugin_instruction>\n\n"

    # 5. Thêm Yêu cầu của người dùng
    prompt += f"<user_request>\n{request}\n</user_request>"
    return prompt


def _get_groq_api_key():
    """Đọc Groq API key từ Streamlit secrets hoặc biến môi trường."""
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY")


def generate(request: str, data: dict, context=None, system_instruction=None, model: str = DEFAULT_MODEL) -> dict:
    """Gọi Groq sinh code + giải thích. Trả về {code, explanation}."""
    try:
        from groq import Groq
    except ImportError:
        raise RuntimeError("Chưa cài groq. Chạy: pip install groq")

    key = _get_groq_api_key()
    if not key:
        raise RuntimeError("Chưa có GROQ_API_KEY trong .streamlit/secrets.toml hoặc biến môi trường.")

    prompt = _build_prompt(request, data, context=context, system_instruction=system_instruction)

    client = Groq(api_key=key)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return _parse_response(resp.choices[0].message.content)
