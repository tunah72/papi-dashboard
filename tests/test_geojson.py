"""Kiểm tra GeoJSON được chuẩn hoá cho choropleth Plotly mà không sửa nguồn."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from src.data_loader import normalize_geojson_for_plotly


def _signed_area(ring):
    return sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(ring, ring[1:])
    ) / 2


def _polygons(geometry):
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    return geometry["coordinates"]


def test_normalize_geojson_merges_duplicate_province_and_rewinds_rings():
    raw = json.loads((ROOT / "data" / "processed" / "vietnam_provinces.geojson").read_text())
    original = copy.deepcopy(raw)

    normalized = normalize_geojson_for_plotly(raw)

    assert raw == original
    assert len(normalized["features"]) == 63
    ids = [feature["properties"]["province_id"] for feature in normalized["features"]]
    assert len(ids) == len(set(ids)) == 63

    province_49 = next(feature for feature in normalized["features"] if feature["properties"]["province_id"] == 49)
    assert province_49["geometry"]["type"] == "MultiPolygon"
    assert len(province_49["geometry"]["coordinates"]) == 2

    for feature in normalized["features"]:
        for polygon in _polygons(feature["geometry"]):
            assert _signed_area(polygon[0]) < 0
            assert all(_signed_area(hole) > 0 for hole in polygon[1:])
