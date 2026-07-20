"""Nạp snapshot processed và chuẩn hoá GeoJSON, không phụ thuộc giao diện.

Mọi hàm ở đây chỉ đọc ``data/processed``.  Không hàm nào ghi hay biến đổi file
nguồn trên đĩa; GeoJSON trả về luôn là một bản sao dành cho hiển thị.
"""
from copy import deepcopy
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
GEOJSON = DATA_PROCESSED / "vietnam_provinces.geojson"


def _signed_ring_area(ring):
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:])) / 2


def _rewind_ring(ring, clockwise):
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

    rewound = [
        [_rewind_ring(ring, clockwise=index == 0) for index, ring in enumerate(polygon)]
        for polygon in polygons
    ]
    geometry["coordinates"] = rewound[0] if geometry["type"] == "Polygon" else rewound
    return geometry


def normalize_geojson_for_plotly(geojson):
    """Gộp hai geometry của tỉnh 49 và rewind vòng, không sửa GeoJSON đầu vào."""
    normalized = deepcopy(geojson)
    grouped, order = {}, []
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
            polygons.extend(
                [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
            )
        first["geometry"] = {"type": "MultiPolygon", "coordinates": polygons}
        features.append(first)
    normalized["features"] = features
    return normalized


def load_processed_data(processed_dir: Path | None = None):
    """Đọc snapshot processed đã có; hữu ích cho cả fallback lẫn API local."""
    processed_dir = processed_dir or DATA_PROCESSED
    data = {
        "fact": pd.read_parquet(processed_dir / "fact_papi_long.parquet"),
        "prov_year": pd.read_parquet(processed_dir / "agg_province_year.parquet"),
        "national": pd.read_parquet(processed_dir / "agg_national_year.parquet"),
        "dim_prov": pd.read_csv(processed_dir / "dim_province.csv"),
        "dim_ind": pd.read_csv(processed_dir / "dim_indicator.csv"),
    }
    with (processed_dir / "vietnam_provinces.geojson").open(encoding="utf-8") as file:
        data["geojson"] = normalize_geojson_for_plotly(json.load(file))
    return data


def dim_maps(dim_ind):
    """Trả lookup màu, nhãn ngắn và tên đầy đủ theo code lĩnh vực."""
    return (
        dict(zip(dim_ind.code, dim_ind.color)),
        dict(zip(dim_ind.code, dim_ind.short)),
        dict(zip(dim_ind.code, dim_ind.name_vi)),
    )
