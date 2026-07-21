import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analysis import dimensions


def test_dimension_snapshot_and_pair_quadrants():
    panel = pd.DataFrame({"province_vi":["A","B","C"], "region":["X"]*3, "year":[2024]*3,
                          "D1":[1.,2.,3.], "D2":[1.,3.,2.]})
    snapshot = dimensions.snapshot_for_year(panel, 2024, ["D1", "D2"])
    pair, xm, ym, corr = dimensions.pair_snapshot(snapshot, "D1", "D2")
    assert len(snapshot) == 3
    assert (xm, ym) == pytest.approx((2., 2.))
    assert pair.quadrant.tolist() == ["Thấp–thấp", "Cao–cao", "Cao–cao"]
    assert corr == pytest.approx(.5)


def test_dimension_summaries_and_correlation_order():
    df = pd.DataFrame({"D2":[1.,2.,3.], "D1":[1.,3.,None]})
    summary = dimensions.summaries(df, ["D1", "D2"])
    corr = dimensions.correlation_matrix(df, ["D1", "D2"])
    counts = dimensions.correlation_counts(df, ["D1", "D2"])
    assert summary.code.tolist() == ["D1", "D2"]
    assert summary.loc[0, "mean_score"] == pytest.approx(2.)
    assert summary.loc[0, "min_score"] == pytest.approx(1.)
    assert summary.loc[0, "max_score"] == pytest.approx(3.)
    assert summary.loc[0, "n"] == 2
    assert corr.index.tolist() == ["D1", "D2"]
    assert counts.loc["D1", "D2"] == 2
    assert counts.loc["D2", "D2"] == 3


def test_snapshot_keeps_partial_rows_for_pairwise_statistics():
    panel = pd.DataFrame({
        "province_vi": ["A", "B", "C"], "region": ["X"] * 3, "year": [2024] * 3,
        "D1": [1.0, 2.0, None], "D2": [1.0, None, 3.0],
    })

    snapshot = dimensions.snapshot_for_year(panel, 2024, ["D1", "D2"])

    assert snapshot.province_vi.tolist() == ["A", "B", "C"]
    assert dimensions.correlation_counts(snapshot, ["D1", "D2"]).loc["D1", "D2"] == 1


def test_strongest_pair_regression_and_strength_label():
    frame = pd.DataFrame({
        "province_vi": ["A", "B", "C", "D"], "region": ["X"] * 4,
        "D1": [1.0, 2.0, 3.0, 4.0], "D2": [2.0, 4.0, 6.0, 8.0],
        "D3": [4.0, 1.0, 3.0, 2.0],
    })
    x, y, corr = dimensions.strongest_pair(frame, ["D1", "D2", "D3"])
    assert (x, y) == ("D1", "D2")
    assert corr == pytest.approx(1.0)
    regression, slope, intercept, r_squared = dimensions.regression_snapshot(frame, "D1", "D2")
    assert slope == pytest.approx(2.0)
    assert intercept == pytest.approx(0.0)
    assert r_squared == pytest.approx(1.0)
    assert regression.residual.abs().max() == pytest.approx(0.0)
    assert dimensions.correlation_strength(corr) == "mạnh"
