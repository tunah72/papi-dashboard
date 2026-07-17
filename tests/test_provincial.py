import pandas as pd
import pytest

from analysis import provincial


@pytest.fixture
def panel():
    return pd.DataFrame({
        "province_id": [1, 2, 3, 4, 1],
        "province_vi": ["A", "B", "C", "D", "A"],
        "region": ["Bắc", "Bắc", "Nam", "Nam", "Bắc"],
        "year": [2024, 2024, 2024, 2024, 2023],
        "score": [10.0, 8.0, 9.0, None, 7.0],
        "D1": [1.0, 2.0, 3.0, 4.0, 1.0],
        "D2": [2.0, 3.0, 4.0, 5.0, 2.0],
    })


def test_snapshot_and_region_summary_only_count_available_scores(panel):
    snapshot = provincial.snapshot_for_year(panel, 2024, "score")
    summary = provincial.region_summary(snapshot, "score")

    assert snapshot.province_vi.tolist() == ["A", "B", "C"]
    bac = summary.set_index("region").loc["Bắc"]
    assert bac.n_provinces == 2
    assert bac.mean_score == pytest.approx(9.0)
    assert bac.spread == pytest.approx(2.0)


def test_ranking_and_benchmarks(panel):
    snapshot = provincial.snapshot_for_year(panel, 2024, "score")
    ranking = provincial.ranking_in_region(snapshot, "Bắc", "score")
    benchmarks = provincial.province_benchmarks(snapshot, "Bắc", "B", "score")

    assert ranking.province_vi.tolist() == ["A", "B"]
    assert ranking.rank_region.tolist() == [1, 2]
    assert benchmarks["vs_region"] == pytest.approx(-1.0)
    assert benchmarks["vs_national"] == pytest.approx(-1.0)


def test_dimension_benchmarks_compare_same_year(panel):
    profile = provincial.dimension_benchmarks(panel, 2024, "Bắc", "A", ["D1", "D2"])

    assert profile.code.tolist() == ["D1", "D2"]
    assert profile.province_score.tolist() == [1.0, 2.0]
    assert profile.region_mean.tolist() == [1.5, 2.5]
    # Benchmark theo từng lĩnh vực giữ lại mọi tỉnh có điểm lĩnh vực, kể cả khi
    # điểm tổng của tỉnh đó khuyết vì một lĩnh vực khác không có dữ liệu.
    assert profile.national_mean.tolist() == [2.5, 3.5]
