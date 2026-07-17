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
    df = pd.DataFrame({"D2":[1.,2.,3.], "D1":[1.,3.,2.]})
    summary = dimensions.summaries(df, ["D1", "D2"])
    corr = dimensions.correlation_matrix(df, ["D1", "D2"])
    assert summary.code.tolist() == ["D1", "D2"]
    assert summary.loc[0, "mean_score"] == pytest.approx(2.)
    assert corr.index.tolist() == ["D1", "D2"]
