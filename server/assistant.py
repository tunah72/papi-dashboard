"""Orchestration cho Floating AI Assistant chạy local, có approval gate và JSONL lifecycle log."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import threading
import tomllib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from app.ai import api_exec
from server import services
from server.view_models import json_safe


ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = ROOT / "logs" / "ai_sessions.jsonl"
SOURCE = "UNDP Việt Nam · CECODES · RTA"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
MAX_RESULT_ROWS = 500
_LOG_LOCK = threading.Lock()


class AssistantError(RuntimeError):
    pass


class AssistantConflict(AssistantError):
    pass


class ProviderError(AssistantError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _append_event(session_id: str, event: str, **payload: Any) -> dict[str, Any]:
    record = {"time": _now(), "schemaVersion": "v1", "sessionId": session_id, "event": event, **json_safe(payload)}
    LOG_FILE.parent.mkdir(exist_ok=True)
    with _LOG_LOCK, LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return record


def read_events(session_id: str) -> list[dict[str, Any]]:
    if not LOG_FILE.exists():
        return []
    with _LOG_LOCK, LOG_FILE.open(encoding="utf-8") as handle:
        rows = []
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("sessionId") == session_id:
                rows.append(record)
        return rows


def _proposal_state(session_id: str) -> tuple[dict[str, Any] | None, str | None]:
    proposals: dict[str, dict[str, Any]] = {}
    states: dict[str, str] = {}
    order: list[str] = []
    for event in read_events(session_id):
        proposal_id = event.get("proposalId")
        if event.get("event") == "proposal_pending" and isinstance(proposal_id, str):
            proposals[proposal_id] = event
            states[proposal_id] = "pending"
            order.append(proposal_id)
        elif isinstance(proposal_id, str) and event.get("event") == "proposal_superseded":
            states[proposal_id] = "superseded"
        elif isinstance(proposal_id, str) and event.get("event") == "proposal_approved":
            states[proposal_id] = "approved"
        elif isinstance(proposal_id, str) and event.get("event") in {"execution_succeeded", "execution_failed"}:
            states[proposal_id] = "executed"
    if not order:
        return None, None
    latest_id = order[-1]
    return proposals[latest_id], states.get(latest_id)


def _key() -> str | None:
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    secrets = ROOT / ".streamlit" / "secrets.toml"
    if secrets.exists():
        try:
            value = tomllib.loads(secrets.read_text(encoding="utf-8")).get("GROQ_API_KEY")
            return str(value) if value else None
        except (OSError, tomllib.TOMLDecodeError):
            return None
    return None


def _knowledge_context() -> str:
    meta = services.metadata()["data"]
    dimensions = "\n".join(
        f"- {item['code']}: {item.get('nameVi', item.get('name_vi'))} (có từ {item.get('fromYear', item.get('from_year'))})"
        for item in meta["dimensions"]
    )
    return f"""PAPI là Chỉ số Hiệu quả Quản trị và Hành chính công cấp tỉnh ở Việt Nam, phản ánh trải nghiệm
và cảm nhận của người dân. Dữ liệu dự án bao phủ 2011–2024; D7 và D8 có từ 2018.
{dimensions}
Nguồn phải ghi: {SOURCE}.
Giới hạn: điểm cao chỉ phản ánh kết quả tốt hơn theo khung PAPI; không diễn giải tương quan, hồi quy
hoặc phân cụm thành quan hệ nhân quả hay xếp hạng chính thức. Không so trực tiếp tổng 6 lĩnh vực với
tổng 8 lĩnh vực qua mốc 2018 và không bịa số liệu không có trong context."""


def _number(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def resolve_context(route: str, search: dict[str, str]) -> dict[str, Any]:
    scale = search.get("scale", "eight" if route != "/time-trend" else "six")
    if route == "/overview":
        response = services.overview(scale, _number(search.get("year")))
    elif route == "/time-trend":
        response = services.trends(scale, _number(search.get("from")), _number(search.get("to")), search.get("region"), search.get("province"))
    elif route == "/provincial":
        response = services.provinces(scale, _number(search.get("year")), search.get("region"), search.get("province"))
    elif route == "/dimension":
        response = services.dimensions_view(scale, _number(search.get("year")), search.get("x"), search.get("y"))
    elif route == "/dynamics":
        response = services.dynamics_view(scale, _number(search.get("from")), _number(search.get("to")), _number(search.get("k")))
    else:
        raise AssistantError("Trang hiện tại không hỗ trợ Trợ lý AI.")
    return {"route": route, "filters": response["meta"]["filters"], "insights": response["data"].get("insights", {})}


def _schema_context() -> str:
    lines = ["Các biến pandas/GeoJSON có sẵn trong executor:"]
    for name, value in services.data().items():
        if isinstance(value, pd.DataFrame):
            lines.append(f"- {name}: columns={list(value.columns)}")
            for column in ("region", "code"):
                if column in value.columns:
                    values = sorted(str(item) for item in value[column].dropna().unique())
                    if len(values) <= 20:
                        lines.append(f"  {column}={values}")
        else:
            lines.append(f"- {name}: GeoJSON")
    return "\n".join(lines)


def _prompt(message: str, context: dict[str, Any], *, revision: dict[str, Any] | None, clarification_used: bool) -> str:
    revision_text = ""
    if revision:
        revision_text = f"""\nĐây là yêu cầu chỉnh proposal hiện tại. BẮT BUỘC trả kind=proposal và sinh lại TOÀN BỘ code.
<previous_code>\n{revision.get('code', '')}\n</previous_code>"""
    clarification_rule = "Không hỏi làm rõ thêm; hãy trả answer hoặc proposal dựa trên thông tin hiện có." if clarification_used else "Nếu thật sự mơ hồ, được hỏi tối đa một câu làm rõ."
    return f"""Bạn là Trợ lý AI phân tích dữ liệu PAPI. Chỉ trả MỘT JSON hợp lệ, không markdown và không reasoning nội bộ.

Ba output hợp lệ:
{{"kind":"answer","answer":"...","source":"{SOURCE}"}}
{{"kind":"clarification","question":"..."}}
{{"kind":"proposal","explanation":"2-3 câu tiếng Việt","code":"Python đầy đủ"}}

Quy tắc:
- Câu hỏi kiến thức trả answer có nguồn. Không bịa số liệu.
- Nếu cần tính mới, trả proposal. Không nói rằng code đã chạy.
- Code không import, không đọc/ghi file, không gọi mạng; chỉ dùng {api_exec.available_names(services.data())}.
- Code chỉ đọc bản sao dữ liệu, có comment tiếng Việt, gán bảng/scalar vào result và Plotly figure tùy chọn vào fig.
- Không dùng open/exec/eval/__import__/input, dunder, process hoặc filesystem.
- {clarification_rule}

<knowledge>\n{_knowledge_context()}\n</knowledge>
<schema>\n{_schema_context()}\n</schema>
<dashboard_context>\n{json.dumps(context, ensure_ascii=False)}\n</dashboard_context>{revision_text}
<user_request>\n{message}\n</user_request>"""


def _parse_provider(text: str) -> dict[str, Any]:
    stripped = (text or "").strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, re.DOTALL)
    if fenced:
        stripped = fenced.group(1)
    try:
        payload = json.loads(stripped)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ProviderError("Groq trả về cấu trúc không hợp lệ. Hãy thử diễn đạt yêu cầu ngắn gọn hơn.") from exc
    if not isinstance(payload, dict) or payload.get("kind") not in {"answer", "clarification", "proposal"}:
        raise ProviderError("Groq trả về loại phản hồi không được hỗ trợ.")
    kind = payload["kind"]
    required = {"answer": "answer", "clarification": "question", "proposal": "code"}[kind]
    if not isinstance(payload.get(required), str) or not payload[required].strip():
        raise ProviderError("Groq trả về phản hồi thiếu nội dung bắt buộc.")
    return payload


def generate_reply(message: str, context: dict[str, Any], *, revision: dict[str, Any] | None = None, clarification_used: bool = False) -> dict[str, Any]:
    try:
        from groq import Groq
    except ImportError as exc:
        raise ProviderError("Chưa cài thư viện Groq cho FastAPI local.") from exc
    key = _key()
    if not key:
        raise ProviderError("FastAPI local chưa được cấu hình GROQ_API_KEY.")
    try:
        response = Groq(api_key=key, max_retries=0).chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": _prompt(message, context, revision=revision, clarification_used=clarification_used)}],
            temperature=0.2,
        )
        return _parse_provider(response.choices[0].message.content)
    except ProviderError:
        raise
    except Exception as exc:
        raise ProviderError("Không thể nhận phản hồi từ Groq lúc này. Hãy thử lại sau.") from exc


_BLOCKED_NAMES = {"open", "exec", "eval", "compile", "__import__", "input", "breakpoint", "help", "quit", "exit", "getattr", "setattr", "delattr"}
_BLOCKED_ATTRIBUTES = {
    "to_csv", "to_excel", "to_json", "to_parquet", "to_pickle", "to_sql", "to_feather", "to_hdf",
    "to_stata", "to_xml", "system", "popen", "remove", "unlink", "write_text", "write_bytes", "save", "dump",
}


def normalize_and_validate_code(code: str) -> str:
    normalized = "\n".join(
        line for line in code.splitlines() if not line.strip().startswith(("import ", "from "))
    ).strip()
    if not normalized:
        raise ProviderError("Proposal không chứa code có thể hiển thị.")
    try:
        tree = ast.parse(normalized)
    except SyntaxError as exc:
        raise ProviderError("Code Groq đề xuất không phải Python hợp lệ.") from exc
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal)):
            raise ProviderError("Code đề xuất chứa cú pháp không được phép trong executor local.")
        if isinstance(node, ast.Name) and (node.id in _BLOCKED_NAMES or node.id.startswith("__")):
            raise ProviderError("Code đề xuất truy cập tên bị chặn trong executor local.")
        if isinstance(node, ast.Attribute) and (node.attr.startswith("__") or node.attr in _BLOCKED_ATTRIBUTES):
            raise ProviderError("Code đề xuất chứa thao tác file/process không được phép.")
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.startswith("__"):
            raise ProviderError("Code đề xuất chứa truy cập dunder không được phép.")
    return normalized


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def handle_message(*, session_id: str | None, message: str, route: str, search: dict[str, str], revision_of: str | None) -> dict[str, Any]:
    session_id = session_id or str(uuid.uuid4())
    turn_id = str(uuid.uuid4())
    context = resolve_context(route, search)
    latest, state = _proposal_state(session_id)
    revision = None
    if revision_of:
        if not latest or latest.get("proposalId") != revision_of or state != "pending":
            raise AssistantConflict("Chỉ proposal mới nhất đang chờ duyệt mới có thể yêu cầu chỉnh lại.")
        revision = latest
    clarification_used = any(event.get("event") == "clarification_returned" for event in read_events(session_id)[-3:])
    _append_event(session_id, "request_received", turnId=turn_id, message=message, context=context, revisionOf=revision_of)
    reply = generate_reply(message, context, revision=revision, clarification_used=clarification_used)
    if revision and reply.get("kind") != "proposal":
        raise ProviderError("Yêu cầu chỉnh sửa chưa trả về một proposal code đầy đủ.")
    common = {"sessionId": session_id, "turnId": turn_id, "kind": reply["kind"]}
    if reply["kind"] == "answer":
        response = {**common, "answer": reply["answer"].strip(), "source": SOURCE}
        _append_event(session_id, "answer_returned", turnId=turn_id, answer=response["answer"], source=SOURCE)
        return response
    if reply["kind"] == "clarification":
        if clarification_used:
            raise ProviderError("Trợ lý đã dùng câu hỏi làm rõ cho yêu cầu này.")
        response = {**common, "question": reply["question"].strip()}
        _append_event(session_id, "clarification_returned", turnId=turn_id, question=response["question"])
        return response
    code = normalize_and_validate_code(reply["code"])
    if latest and state == "pending":
        _append_event(session_id, "proposal_superseded", proposalId=latest["proposalId"])
    proposal_id = str(uuid.uuid4())
    response = {
        **common, "proposalId": proposal_id, "explanation": str(reply.get("explanation") or "Code do AI đề xuất."),
        "code": code, "status": "pending_approval", "source": SOURCE,
    }
    _append_event(session_id, "proposal_pending", turnId=turn_id, proposalId=proposal_id, explanation=response["explanation"], code=code, codeHash=_hash(code), source=SOURCE, context=context)
    return response


def _serialize_result(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, pd.Series):
        value = value.rename(value.name or "value").reset_index()
    if isinstance(value, pd.DataFrame):
        total = len(value)
        preview = value.head(MAX_RESULT_ROWS)
        return {
            "kind": "table", "columns": [str(column) for column in preview.columns],
            "rows": json_safe(preview.to_dict(orient="records")), "totalRows": total,
            "truncated": total > MAX_RESULT_ROWS, "shape": [int(value.shape[0]), int(value.shape[1])],
        }
    return {"kind": "scalar", "value": json_safe(value), "totalRows": 1, "truncated": False, "shape": []}


def execute_proposal(*, session_id: str, proposal_id: str) -> dict[str, Any]:
    latest, state = _proposal_state(session_id)
    if not latest or latest.get("proposalId") != proposal_id or state != "pending":
        raise AssistantConflict("Proposal này không còn là bản mới nhất đang chờ duyệt.")
    code = str(latest["code"])
    if latest.get("codeHash") != _hash(code):
        raise AssistantConflict("Code proposal không khớp checksum đã lưu.")
    _append_event(session_id, "proposal_approved", proposalId=proposal_id, codeHash=latest["codeHash"])
    output = api_exec.execute(code, services.data())
    result = _serialize_result(output.get("result"))
    figure = json.loads(output["fig"].to_json()) if output.get("fig") is not None else None
    status = "failed" if output.get("error") else "succeeded"
    response = {
        "sessionId": session_id, "proposalId": proposal_id, "status": status, "result": result,
        "figure": figure, "stdout": output.get("stdout", ""), "warnings": output.get("warnings", []),
        "error": output.get("error"),
    }
    _append_event(session_id, f"execution_{status}", proposalId=proposal_id, **{key: value for key, value in response.items() if key not in {"sessionId", "proposalId"}})
    return response
