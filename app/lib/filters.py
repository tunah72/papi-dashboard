"""Các selector dùng chung cho sidebar. Mỗi hàm render một widget và trả về lựa chọn.
Page tự compose các selector cần dùng, không bắt buộc dùng hết."""
import streamlit as st

from lib import config


def select_scale_mode(label="Chế độ thang điểm"):
    return st.sidebar.radio(label, config.SCALE_MODES, index=0)


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


def select_dimensions(data, label="Trục", default_all=True):
    """Trả về danh sách code (D1..D8) theo nhãn ngắn người dùng chọn."""
    dim = data["dim_ind"]
    short_to_code = dict(zip(dim.short, dim.code))
    options = list(short_to_code.keys())
    chosen = st.sidebar.multiselect(label, options, default=options if default_all else [])
    return [short_to_code[s] for s in chosen]
