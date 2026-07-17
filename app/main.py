"""Entry point của PAPI Dashboard. Chạy: streamlit run app/main.py
Khai báo multipage navigation. Các trang nằm trong app/pages/."""
import streamlit as st

from lib import config, layout

st.set_page_config(page_title=config.APP_TITLE, layout="wide")
layout.inject_global_styles()

pages = [
    st.Page("pages/overview.py", title="Tổng quan", default=True),
    st.Page("pages/time_trend.py", title="Diễn biến theo thời gian"),
    st.Page("pages/provincial.py", title="So sánh giữa các tỉnh"),
    st.Page("pages/dimension.py", title="Phân tích theo trục"),
    st.Page("pages/dynamics.py", title="Động lực thay đổi và phân nhóm"),
    st.Page("pages/ai_assistant.py", title="AI Assistant"),
]

st.navigation(pages).run()
