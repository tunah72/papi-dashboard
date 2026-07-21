"""Unit test cho src/analysis/trend.py — hàm thuần, dữ liệu nhỏ tự dựng.

Chạy: pytest tests/test_trend.py   (hoặc: python -m pytest)
Không phụ thuộc Streamlit hay dữ liệu parquet thật.
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analysis import trend  # noqa: E402


def _prov_year():
    """2 tỉnh × 3 năm; total = trung bình hai tỉnh: 2020→10, 2021→20, 2022→30."""
    return pd.DataFrame({
        "year":  [2020, 2020, 2021, 2021, 2022, 2022],
        "total": [8.0, 12.0, 18.0, 22.0, 28.0, 32.0],
    })


def _national():
    """Long: D1 tăng (1→3), D2 giảm (5→4), qua 2020–2022."""
    return pd.DataFrame({
        "year":       [2020, 2021, 2022, 2020, 2021, 2022],
        "code":       ["D1", "D1", "D1", "D2", "D2", "D2"],
        "mean_score": [1.0, 2.0, 3.0, 5.0, 4.5, 4.0],
    })


def test_total_by_year_means_and_filters():
    out = trend.total_by_year(_prov_year(), "total")
    assert out["total"].tolist() == [10.0, 20.0, 30.0]
    assert out["year"].tolist() == [2020, 2021, 2022]
    clipped = trend.total_by_year(_prov_year(), "total", 2021, 2022)
    assert clipped["year"].tolist() == [2021, 2022]


def test_total_by_year_drops_all_nan_year():
    df = _prov_year()
    df.loc[df.year == 2021, "total"] = np.nan       # cả năm khuyết
    out = trend.total_by_year(df, "total")
    assert 2021 not in out["year"].tolist()


def test_dim_deltas_last_minus_first():
    delta = trend.dim_deltas(_national(), ["D1", "D2"], 2020, 2022)
    assert delta["D1"] == 2.0          # 3 - 1
    assert delta["D2"] == -1.0         # 4 - 5
    assert delta.idxmax() == "D1" and delta.idxmin() == "D2"


def test_dim_deltas_missing_dim_is_nan():
    delta = trend.dim_deltas(_national(), ["D1", "D9"], 2020, 2022)
    assert math.isnan(delta["D9"])


def test_summarize_total():
    s = trend.summarize_total(trend.total_by_year(_prov_year(), "total"), "total")
    assert (s["first"], s["latest"]) == (2020, 2022)
    assert (s["v_first"], s["v_latest"], s["net"]) == (10.0, 30.0, 20.0)
    assert s["peak_year"] == 2022 and s["peak_val"] == 30.0 and s["dip_val"] == 10.0


def test_summarize_total_empty():
    s = trend.summarize_total(pd.DataFrame({"year": [], "total": []}), "total")
    assert s["first"] is None and s["net"] is None


def test_compare_periods():
    cmp = trend.compare_periods(_national(), ["D1", "D2"], [2020], [2022])
    assert cmp["D1"]["before"] == 1.0 and cmp["D1"]["after"] == 3.0
    assert cmp["D1"]["diff"] == 2.0
    assert cmp["D2"]["diff"] == -1.0


def test_compare_periods_missing_is_nan():
    cmp = trend.compare_periods(_national(), ["D1"], [1990], [2022])
    assert math.isnan(cmp["D1"]["diff"])


def test_classify_change():
    assert trend.classify_change(0.5) == "tăng"
    assert trend.classify_change(-0.5) == "giảm"
    assert trend.classify_change(0.0) == "gần như không đổi"
    assert trend.classify_change(0.02) == "gần như không đổi"   # trong ngưỡng eps
    assert trend.classify_change(float("nan")) == "không đủ dữ liệu"


def test_regional_series_yoy_focus_and_turning_points():
    panel = pd.DataFrame({
        "province_vi": ["A", "B"] * 3,
        "region": ["Bắc", "Nam"] * 3,
        "year": [2020, 2020, 2021, 2021, 2022, 2022],
        "total": [8.0, 12.0, 10.0, 16.0, 14.0, 18.0],
    })
    regional = trend.regional_total_series(panel, "total", 2020, 2022)
    assert regional.query("region == 'Bắc'").score.tolist() == [8.0, 10.0, 14.0]
    yoy = trend.regional_year_over_year(panel, "total", 2020, 2022)
    assert yoy.query("region == 'Bắc'").change.tolist() == [2.0, 4.0]
    focus = trend.focus_total_series(panel, "total", 2020, 2022, "Bắc", "A")
    assert set(focus.scope) == {"region", "province"}
    totals = trend.total_by_year(panel, "total", 2020, 2022)
    points = trend.turning_points(totals, "total", limit=1)
    assert points.iloc[0].year == 2021
    assert points.iloc[0].change == pytest.approx(3.0)


def test_regional_ranks_use_min_rank_for_ties():
    panel = pd.DataFrame({
        "region": ["A", "B", "C", "A", "B", "C"],
        "year": [2020, 2020, 2020, 2021, 2021, 2021],
        "total": [10.0, 10.0, 8.0, 9.0, 11.0, 8.0],
    })
    ranks = trend.regional_ranks(panel, "total", 2020, 2022)
    assert set(ranks.columns) >= {"year", "region", "score", "contributor_n", "rank"}
    assert ranks["rank"].min() == 1
    assert ranks.query("year == 2020 and region in ['A', 'B']")['rank'].tolist() == [1, 1]
