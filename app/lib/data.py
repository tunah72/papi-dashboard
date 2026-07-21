"""Adapter cache cho Streamlit fallback; logic data thuần nằm ở ``src/data_loader``."""
import streamlit as st

from lib import config
from data_loader import dim_maps, load_processed_data, normalize_geojson_for_plotly


@st.cache_data(show_spinner="Đang nạp dữ liệu...")
def load_data():
    """Phiên bản có cache dùng trong app. Gọi một lần, các lần rerun sau lấy từ cache."""
    return load_processed_data(config.DATA_PROCESSED)
