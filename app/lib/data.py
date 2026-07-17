"""Nạp dữ liệu đã xử lý cho app, có cache. Chỉ đọc data/processed/, không sửa dữ liệu."""
from copy import deepcopy
import json
import pandas as pd
import streamlit as st

from lib import config


def _signed_ring_area(ring):
    """Diện tích có dấu của một vòng GeoJSON: dương là ngược chiều kim đồng hồ."""
    return sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(ring, ring[1:])
    ) / 2


def _rewind_ring(ring, clockwise):
    """Đưa hướng vòng về quy ước Plotly/D3 mà không thay đổi hình học."""
    is_clockwise = _signed_ring_area(ring) < 0
    return list(reversed(ring)) if is_clockwise != clockwise else ring


def _rewind_geometry(geometry):
    """Vòng ngoài theo chiều kim đồng hồ, lỗ theo chiều ngược lại cho Plotly/D3."""
    geometry = deepcopy(geometry)
    if geometry["type"] == "Polygon":
        polygons = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        polygons = geometry["coordinates"]
    else:
        raise ValueError(f"Không hỗ trợ geometry type: {geometry['type']}")

    rewound = []
    for polygon in polygons:
        rewound.append([
            _rewind_ring(ring, clockwise=index == 0)
            for index, ring in enumerate(polygon)
        ])
    geometry["coordinates"] = rewound[0] if geometry["type"] == "Polygon" else rewound
    return geometry


def normalize_geojson_for_plotly(geojson):
    """Tạo bản GeoJSON hiển thị đúng trong Plotly mà không sửa file nguồn.

    Nguồn có hai feature cùng ``province_id=49`` (đất liền Bà Rịa–Vũng Tàu và Côn Đảo).
    Hai feature được gộp thành một MultiPolygon trước khi join với panel tỉnh-năm. Đồng thời,
    các vòng được rewind theo quy ước D3 để tránh Plotly tô phần ngoài Việt Nam thành hình chữ nhật.
    """
    normalized = deepcopy(geojson)
    grouped = {}
    order = []
    for feature in normalized["features"]:
        province_id = feature["properties"]["province_id"]
        if province_id not in grouped:
            grouped[province_id] = []
            order.append(province_id)
        grouped[province_id].append(feature)

    features = []
    for province_id in order:
        province_features = grouped[province_id]
        first = province_features[0]
        if len(province_features) == 1:
            first["geometry"] = _rewind_geometry(first["geometry"])
            features.append(first)
            continue

        polygons = []
        for feature in province_features:
            geometry = _rewind_geometry(feature["geometry"])
            if geometry["type"] == "Polygon":
                polygons.append(geometry["coordinates"])
            else:
                polygons.extend(geometry["coordinates"])
        first["geometry"] = {"type": "MultiPolygon", "coordinates": polygons}
        features.append(first)

    normalized["features"] = features
    return normalized


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
        data["geojson"] = normalize_geojson_for_plotly(json.load(f))
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
