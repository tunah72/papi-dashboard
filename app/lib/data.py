"""Nạp dữ liệu đã xử lý cho app, có cache. Chỉ đọc data/processed/, không sửa dữ liệu."""
import json
import pandas as pd
import streamlit as st

from lib import config


def _load_tables():
    """Đọc toàn bộ bảng từ data/processed/. Hàm thuần để test được ngoài Streamlit."""
    p = config.DATA_PROCESSED
    data = {
        "fact": pd.read_parquet(p / "fact_papi_long.parquet"),        # long: tỉnh x năm x trục
        "prov_year": pd.read_parquet(p / "agg_province_year.parquet"),  # wide panel 63x14
        "national": pd.read_parquet(p / "agg_national_year.parquet"),   # trung bình cả nước
        "dim_prov": pd.read_csv(p / "dim_province.csv"),
        "dim_ind": pd.read_csv(p / "dim_indicator.csv"),
    }
    with open(config.GEOJSON, encoding="utf-8") as f:
        data["geojson"] = json.load(f)
    return data


@st.cache_data(show_spinner="Đang nạp dữ liệu...")
def load_data():
    """Phiên bản có cache dùng trong app. Gọi một lần, các lần rerun sau lấy từ cache."""
    return _load_tables()


def dim_maps(dim_ind):
    """Từ bảng dim_indicator, trả về ba dict tra cứu: màu, nhãn ngắn, tên đầy đủ theo code."""
    color = dict(zip(dim_ind.code, dim_ind.color))
    short = dict(zip(dim_ind.code, dim_ind.short))
    name = dict(zip(dim_ind.code, dim_ind.name_vi))
    return color, short, name
