"""Hướng 2: So sánh giữa các tỉnh (Lê Xuân Trí). Stub đợt nền, owner sẽ hoàn thiện."""
import streamlit as st

st.title("So sánh giữa các tỉnh")

# Publish ngữ cảnh (Task 2.1)
st.session_state["dash_context"] = {
    "page": "So sánh tỉnh",
    "filters": {},
    "data_scope": {"status": "stub"},
}

st.info("Trang đang được phát triển (Hướng phân tích 2).")
