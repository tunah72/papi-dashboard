"""Trang AI Assistant: luồng human-in-the-loop.
AI đề xuất code + giải thích -> người dùng xem, sửa, phê duyệt -> thực thi tại máy -> hiển thị -> log."""
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

# Chọn technique có sẵn hoặc tự nhập yêu cầu
labels = ["(Tự nhập yêu cầu)"] + [t["label"] for t in techs]
choice = st.selectbox("Chọn kỹ thuật phân tích", labels)
default_req = ""
if choice != labels[0]:
    t = next(t for t in techs if t["label"] == choice)
    st.info(t["description"])
    default_req = t["default_request"]

request = st.text_area("Yêu cầu phân tích (ngôn ngữ tự nhiên)", value=default_req, height=100)

if st.button("Sinh code (AI đề xuất)", type="primary"):
    try:
        with st.spinner("Gemini đang sinh code..."):
            out = api_ai.generate(request, d)
        st.session_state["ai_code"] = out["code"]
        st.session_state["ai_explanation"] = out["explanation"]
        st.session_state["ai_request"] = request
    except Exception as e:
        st.error(str(e))

# Code ở trạng thái chờ duyệt
if "ai_code" in st.session_state:
    st.subheader("Code AI đề xuất — trạng thái: chờ duyệt")
    if st.session_state.get("ai_explanation"):
        st.markdown("**Giải thích:** " + st.session_state["ai_explanation"])
    edited = st.text_area("Chỉnh sửa code trước khi duyệt", value=st.session_state["ai_code"],
                          height=300, key="ai_edit")

    if st.button("Phê duyệt và thực thi", type="primary"):
        res = api_exec.execute(edited, d)
        api_logs.log({
            "request": st.session_state.get("ai_request", ""),
            "code_ai": st.session_state["ai_code"], "code_run": edited,
            "explanation": st.session_state.get("ai_explanation", ""),
            "error": res["error"],
            "has_result": res["result"] is not None, "has_fig": res["fig"] is not None,
        })
        st.subheader("Kết quả")
        if res["error"]:
            st.error(res["error"])
        if res["stdout"]:
            st.code(res["stdout"], language="text")
        if res["fig"] is not None:
            st.plotly_chart(res["fig"], width="stretch")
        if isinstance(res["result"], (pd.DataFrame, pd.Series)):
            st.dataframe(res["result"])
        elif res["result"] is not None:
            st.write(res["result"])
        if res["error"] is None and res["result"] is None and res["fig"] is None:
            st.warning("Code chưa gán biến `result` hoặc `fig`. Hãy bổ sung rồi duyệt lại.")

# Nhật ký
with st.expander("Nhật ký phiên AI (10 mục gần nhất)"):
    logs = api_logs.read_all()[-10:][::-1]
    if not logs:
        st.write("Chưa có log.")
    for r in logs:
        st.write(f"- {r.get('time')} | {r.get('request', '')[:80]} | lỗi: {r.get('error')}")
