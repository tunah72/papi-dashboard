"""Các selector còn được Streamlit fallback sử dụng."""
import streamlit as st

from lib import config


def scale_segmented(label="Phạm vi so sánh"):
    """Chọn phạm vi so sánh dạng segmented control, render tại vị trí gọi (không phải sidebar)."""
    mode = st.segmented_control(label, config.SCALE_MODES, default=config.SCALE_MODES[0])
    return mode or config.SCALE_MODES[0]


def year_range_inline(data, label="Năm", year_min=None):
    """Chọn khoảng năm bằng select_slider, render tại vị trí gọi."""
    years = sorted(y for y in data["prov_year"].year.unique() if year_min is None or y >= year_min)
    return st.select_slider(label, options=years, value=(years[0], years[-1]))


def year_inline(data, label="Năm", default=config.YEAR_MAX, year_min=None):
    """Chọn một năm tại vị trí gọi, có thể giới hạn theo thước đo đang dùng."""
    years = sorted(y for y in data["prov_year"].year.unique() if year_min is None or y >= year_min)
    default = default if default in years else years[-1]
    return st.select_slider(label, options=years, value=default)
