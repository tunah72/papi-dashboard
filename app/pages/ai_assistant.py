"""Trang AI Assistant: luồng human-in-the-loop.
AI đề xuất code + giải thích -> người dùng xem, sửa, phê duyệt -> thực thi tại máy -> hiển thị -> log."""
import difflib
import pandas as pd
import streamlit as st

from lib import data
from ai import api_ai, api_exec, api_logs, registry

st.title("AI Assistant")
st.caption("AI đề xuất code và giải thích. Bạn xem, chỉnh sửa, phê duyệt rồi mới thực thi tại máy. "
           "Code chỉ đọc dữ liệu, chạy local. Toàn bộ quá trình được ghi log.")

d = data.load_data()
registry.discover()
techs = registry.all_techniques()
FREE_INPUT_LABEL = "(Tự nhập yêu cầu)"


def _clear_ai_work_state():
    """Xóa trạng thái sinh/chạy code hiện tại nhưng giữ context dashboard và lựa chọn technique."""
    for key in [
        "ai_code", "ai_explanation", "ai_request", "ai_request_input",
        "ai_default_prompt_input", "ai_default_prompt_source", "ai_extra_request_input",
        "ai_edit", "exec_result", "ai_last_run_status",
    ]:
        st.session_state.pop(key, None)


def _set_free_input_state():
    """Đưa trang về mode tự nhập: không prompt mẫu, không yêu cầu bổ sung, không kết quả cũ."""
    _clear_ai_work_state()
    st.session_state["ai_choice"] = FREE_INPUT_LABEL
    st.session_state["ai_choice_committed"] = FREE_INPUT_LABEL
    st.session_state["ai_default_prompt_input"] = ""
    st.session_state["ai_default_prompt_source"] = FREE_INPUT_LABEL
    st.session_state["ai_extra_request_input"] = ""


def _handle_choice_change():
    current = st.session_state.get("ai_choice")
    previous = st.session_state.get("ai_choice_committed")
    if previous is not None and current != previous:
        if current == FREE_INPUT_LABEL:
            _set_free_input_state()
        else:
            _clear_ai_work_state()
    st.session_state["ai_choice_committed"] = current


def _compose_request(base_request: str, extra_request: str) -> str:
    base = (base_request or "").strip()
    extra = (extra_request or "").strip()
    if base and extra:
        return (
            "Câu hỏi chính của người dùng:\n"
            + base
            + "\n\nYêu cầu phân tích bổ sung của người dùng:\n"
            + extra
        )
    return base or extra


# Chọn technique có sẵn hoặc tự nhập yêu cầu
labels = [FREE_INPUT_LABEL] + [t["label"] for t in techs]
default_req = ""
seed = st.session_state.pop("ai_seed", None)

# Nếu có seed từ nút "Giải thích biểu đồ", ưu tiên dùng seed
current_system_instruction = None

if seed:
    choice = st.selectbox("Chọn kỹ thuật phân tích", labels, index=0, key="ai_choice", on_change=_handle_choice_change)
    default_req = seed
else:
    choice = st.selectbox("Chọn kỹ thuật phân tích", labels, key="ai_choice", on_change=_handle_choice_change)
    if choice != labels[0]:
        t = next(t for t in techs if t["label"] == choice)
        default_req = t.get("user_prompt", t.get("default_request", ""))
        current_system_instruction = t.get("system_instruction", "")

st.session_state["ai_choice_committed"] = choice

if st.session_state.get("ai_default_prompt_source") != choice:
    st.session_state["ai_default_prompt_input"] = default_req
    st.session_state["ai_default_prompt_source"] = choice

base_request = st.text_area(
    "Câu hỏi gợi ý (có thể chỉnh sửa)",
    value=default_req,
    height=86,
    key="ai_default_prompt_input",
)
extra_request = st.text_area(
    "Yêu cầu phân tích bổ sung (tuỳ chọn)",
    value="",
    height=80,
    key="ai_extra_request_input",
)
request = _compose_request(base_request, extra_request)

col_gen, col_reset = st.columns([1, 1])
with col_gen:
    btn_gen = st.button("Sinh code (AI đề xuất)", type="primary", use_container_width=True)
with col_reset:
    btn_reset = st.button("Reset", type="secondary", use_container_width=True)

if btn_reset:
    api_logs.log({
        "request": "[HÀNH ĐỘNG] Người dùng Reset trang",
        "code_ai": "", "code_run": "",
        "explanation": "",
        "context": st.session_state.get("dash_context"),
        "error": None,
        "has_result": False, "has_fig": False,
    })
    dash_context = st.session_state.get("dash_context")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    if dash_context is not None:
        st.session_state["dash_context"] = dash_context
    _set_free_input_state()
    st.rerun()

if btn_gen:
    try:
        with st.spinner("Groq đang sinh code..."):
            out = api_ai.generate(
                request=request, 
                data=d, 
                context=st.session_state.get("dash_context"),
                system_instruction=current_system_instruction
            )
        st.session_state["ai_code"] = api_ai.sanitize_code_payload(out["code"])
        st.session_state["ai_explanation"] = out["explanation"]
        st.session_state["ai_request"] = request
        st.session_state["ai_last_run_status"] = "pending"
        # Log ngay khi AI đề xuất để cả code chưa được duyệt cũng truy xuất được.
        api_logs.log({
            "event": "generated_pending_approval",
            "request": request,
            "code_ai": st.session_state["ai_code"], "code_run": "",
            "explanation": out["explanation"],
            "context": st.session_state.get("dash_context"),
            "error": None, "has_result": False, "has_fig": False,
        })
        # Reset trạng thái chỉnh sửa cũ
        if "ai_edit" in st.session_state:
            del st.session_state["ai_edit"]
    except Exception as e:
        st.error(str(e))

# Code ở trạng thái chờ duyệt
if "ai_code" in st.session_state:
    code_ai = api_ai.sanitize_code_payload(st.session_state["ai_code"])
    if code_ai != st.session_state["ai_code"]:
        st.session_state["ai_code"] = code_ai
    # Kiểm tra xem người dùng đã sửa code chưa để hiển thị badge (Task 1.2)
    is_edited = "ai_edit" in st.session_state and st.session_state["ai_edit"] != code_ai
    if st.session_state.get("ai_last_run_status") == "executed":
        status_label = "Đã thực thi"
    else:
        status_label = "Chờ duyệt (Đã chỉnh sửa)" if is_edited else "Chờ duyệt (AI đề xuất)"

    st.subheader(f"Code phân tích — {status_label}")
    if st.session_state.get("ai_explanation"):
        st.markdown("**Giải thích:** " + st.session_state["ai_explanation"])

    if "ai_edit" in st.session_state:
        clean_edit = api_ai.sanitize_code_payload(st.session_state["ai_edit"])
        if clean_edit != st.session_state["ai_edit"]:
            st.session_state["ai_edit"] = clean_edit

    edited = st.text_area("Chỉnh sửa code trước khi duyệt (nếu cần)", value=code_ai,
                          height=300, key="ai_edit")

    if st.button("Phê duyệt và thực thi", type="primary"):
        edited_to_run = api_ai.sanitize_code_payload(edited)
        if edited_to_run != edited:
            st.info("Đã tự bóc phần `code` từ JSON payload trước khi thực thi.")
            st.session_state["ai_edit"] = edited_to_run
        res = api_exec.execute(edited_to_run, d)
        result = res["result"]
        result_shape = None
        if isinstance(result, pd.DataFrame):
            result_shape = list(result.shape)
        elif isinstance(result, pd.Series):
            result_shape = [int(result.shape[0])]
        api_logs.log({
            "event": "executed_after_approval",
            "request": st.session_state.get("ai_request", ""),
            "code_ai": code_ai, "code_run": edited_to_run,
            "explanation": st.session_state.get("ai_explanation", ""),
            "context": st.session_state.get("dash_context"),
            "stdout_preview": res["stdout"],
            "warnings": res.get("warnings", []),
            "error": res["error"],
            "has_result": res["result"] is not None, "has_fig": res["fig"] is not None,
            "result_shape": result_shape,
            "fig_type": type(res["fig"]).__name__ if res["fig"] is not None else None,
        })

        # Lưu kết quả thực thi vào session nhưng vẫn giữ code để người dùng xem/sửa/chạy lại.
        st.session_state["exec_result"] = res
        st.session_state["ai_last_run_status"] = "executed" if not res["error"] else "pending"

# Hiển thị kết quả (nếu có)
if "exec_result" in st.session_state:
    res = st.session_state["exec_result"]
    st.subheader("Kết quả thực thi")
    if res["error"]:
        st.error(res["error"])
        # Nếu có lỗi mà code đã bị ẩn, hiện nút để người dùng thử lại
        if "ai_code" not in st.session_state:
             st.info("💡 Mẹo: Nhập lại yêu cầu ở trên để AI thử sinh code khác.")
    if res["stdout"]:
        st.code(res["stdout"], language="text")
    elif res.get("warnings"):
        st.warning("\n".join(res["warnings"]))
    if res["fig"] is not None:
        st.plotly_chart(res["fig"], width="stretch")
    if isinstance(res["result"], (pd.DataFrame, pd.Series)):
        st.dataframe(res["result"])
    elif res["result"] is not None:
        st.write(res["result"])
    if res["error"] is None and res["result"] is None and res["fig"] is None:
        st.warning("Code chưa gán biến `result` hoặc `fig`. Hãy thử yêu cầu rõ hơn.")

# Nhật ký (Task 1.1: Diff Log)
with st.expander("Nhật ký phiên AI (10 mục gần nhất)"):
    logs = api_logs.read_all()[-10:][::-1]
    if not logs:
        st.write("Chưa có log.")
    for r in logs:
        with st.container(border=True):
            event = r.get("event")
            if event == "generated_pending_approval":
                st.caption("AI đã sinh code — chờ người dùng xem, sửa hoặc phê duyệt; chưa thực thi.")
            elif event == "executed_after_approval":
                st.caption("Đã thực thi local sau khi người dùng phê duyệt.")
            st.write(f"**Thời gian:** {r.get('time')} | **Lỗi:** {r.get('error')}")
            st.write(f"**Yêu cầu:** {r.get('request', '')}")
            
            # Hiển thị Diff nếu có chỉnh sửa (Task 1.1)
            if r.get("code_ai") and r.get("code_run") and r.get("code_ai") != r.get("code_run"):
                st.caption("Thay đổi của người dùng so với AI đề xuất:")

                raw_ai = r["code_ai"].splitlines()
                raw_run = r["code_run"].splitlines()
                diff = list(difflib.unified_diff(
                    raw_ai,
                    raw_run,
                    lineterm="", fromfile="AI", tofile="User"
                ))
                if [line.strip() for line in raw_ai] == [line.strip() for line in raw_run]:
                    st.caption("*(Chỉ thay đổi khoảng trắng; diff vẫn hiển thị nguyên bản vì thụt lề Python có ý nghĩa.)*")
                st.code("\n".join(diff), language="diff")
            elif not r.get("code_ai") and r.get("code_run"):
                st.caption("Code (không có bản gốc AI):")
                st.code(r.get("code_run", ""), language="python")
            elif r.get("code_ai") and r.get("code_run") and r.get("event") == "executed_after_approval":
                st.caption("Người dùng giữ nguyên code AI đề xuất.")
            elif r.get("code_ai"):
                st.caption("Code AI đang chờ người dùng duyệt:")
                st.code(r.get("code_ai", ""), language="python")
