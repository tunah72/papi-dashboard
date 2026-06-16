"""Các selector dùng chung cho sidebar. Mỗi hàm render một widget và trả về lựa chọn.
Page tự compose các selector cần dùng, không bắt buộc dùng hết."""
import streamlit as st

from lib import config


def select_scale_mode(label="Thước đo"):
    return st.sidebar.radio(label, config.SCALE_MODES, index=0)


def scale_segmented(label="Phạm vi so sánh"):
    """Chọn phạm vi so sánh dạng segmented control, render tại vị trí gọi (không phải sidebar)."""
    mode = st.segmented_control(label, config.SCALE_MODES, default=config.SCALE_MODES[0])
    return mode or config.SCALE_MODES[0]


def year_range_inline(data, label="Năm", year_min=None):
    """Chọn khoảng năm bằng select_slider, render tại vị trí gọi."""
    years = sorted(y for y in data["prov_year"].year.unique() if year_min is None or y >= year_min)
    return st.select_slider(label, options=years, value=(years[0], years[-1]))


def dimension_pills(data, codes=None, label="Lĩnh vực"):
    """Chip bật/tắt lĩnh vực bằng tên đầy đủ, render tại vị trí gọi. Trả về danh sách code."""
    codes = codes or config.DIM_CODES
    label_to_code = {config.DIM_LABELS[c]: c for c in codes}
    options = list(label_to_code.keys())
    chosen = st.pills(label, options, selection_mode="multi", default=options)
    return [label_to_code[c] for c in chosen] or codes


def select_year(data, label="Năm", default=config.YEAR_MAX):
    years = sorted(data["prov_year"].year.unique())
    default = default if default in years else years[-1]
    return st.sidebar.select_slider(label, options=years, value=default)


def select_year_range(data, label="Khoảng năm", year_min=None):
    years = sorted(y for y in data["prov_year"].year.unique() if year_min is None or y >= year_min)
    return st.sidebar.select_slider(label, options=years, value=(years[0], years[-1]))


def select_regions(data, label="Vùng"):
    return st.sidebar.multiselect(label, config.REGION_ORDER, default=config.REGION_ORDER)


def select_provinces(data, label="Tỉnh", default=None):
    provs = data["dim_prov"].province_vi.tolist()
    return st.sidebar.multiselect(label, provs, default=default or [])


def select_dimensions(data, label="Lĩnh vực", default_all=True):
    """Trả về danh sách code (D1..D8) theo tên lĩnh vực đầy đủ người dùng chọn."""
    codes = list(data["dim_ind"].code)
    label_to_code = {config.DIM_LABELS[c]: c for c in codes}
    options = list(label_to_code.keys())
    chosen = st.sidebar.multiselect(label, options, default=options if default_all else [])
    return [label_to_code[s] for s in chosen]
