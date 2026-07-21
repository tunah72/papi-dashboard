"""Logic thuần cho Hướng 2 — so sánh giữa các tỉnh và vùng.

Các hàm trong module chỉ biến đổi ``prov_year`` đã xử lý. Chúng không đọc file,
không import Streamlit/Plotly để page dashboard, AI và unit test cùng dùng một
nguồn sự thật.
"""
import pandas as pd


def snapshot_for_year(prov_year, year, total_col):
    """Lấy panel tỉnh của một năm, bỏ dòng không có thước đo đang chọn."""
    cols = ["province_id", "province_vi", "region", "year", total_col]
    return (
        prov_year.loc[prov_year.year.eq(year), cols]
        .dropna(subset=[total_col])
        .sort_values(["region", total_col, "province_vi"], ascending=[True, False, True])
        .reset_index(drop=True)
    )


def region_summary(snapshot, total_col, region_order=None):
    """Tóm tắt mức và độ phân tán điểm của từng vùng trong một năm.

    ``n_provinces`` là số tỉnh *có dữ liệu* trong snapshot, không suy diễn đủ
    63 tỉnh khi dữ liệu PAPI của một năm bị khuyết.
    """
    summary = (
        snapshot.groupby("region", observed=True)[total_col]
        .agg(mean_score="mean", median_score="median", min_score="min", max_score="max", n_provinces="count")
        .reset_index()
    )
    summary["spread"] = summary["max_score"] - summary["min_score"]
    if region_order:
        summary["region"] = pd.Categorical(summary["region"], categories=region_order, ordered=True)
    return summary.sort_values("mean_score", ascending=False).reset_index(drop=True)


def ranking_in_region(snapshot, region, total_col):
    """Xếp hạng tỉnh có dữ liệu trong một vùng; hạng 1 là điểm cao nhất."""
    ranked = (
        snapshot.loc[snapshot.region.eq(region), ["province_id", "province_vi", "region", total_col]]
        .sort_values([total_col, "province_vi"], ascending=[False, True])
        .reset_index(drop=True)
    )
    ranked["rank_region"] = ranked.index + 1
    return ranked


def top_bottom(snapshot, total_col, n=10):
    """Trả về các tỉnh điểm cao nhất và thấp nhất, không trùng nhau.

    ``snapshot`` phải là lát cắt của cùng một năm và cùng một thước đo. Khi
    số quan sát không đủ cho hai nhóm ``n``, ưu tiên nhóm điểm cao và nhóm còn
    lại là các quan sát thấp nhất chưa xuất hiện ở nhóm đó.
    """
    if n <= 0:
        raise ValueError("n phải lớn hơn 0")

    ordered_high = snapshot.sort_values([total_col, "province_vi"], ascending=[False, True])
    top = ordered_high.head(n).copy()
    bottom = (
        snapshot.loc[~snapshot.index.isin(top.index)]
        .sort_values([total_col, "province_vi"], ascending=[True, True])
        .head(n)
        .copy()
    )
    return top.reset_index(drop=True), bottom.reset_index(drop=True)


def zscore_outliers(snapshot, total_col, threshold=2.0):
    """Gắn cờ ngoại lệ z-score trong một snapshot cùng năm.

    Dùng độ lệch chuẩn mẫu (``ddof=1``). Nếu không đủ hai quan sát có điểm
    hoặc mọi điểm bằng nhau, không có căn cứ để gắn cờ và ``z_score`` giữ NaN.
    """
    if threshold <= 0:
        raise ValueError("threshold phải lớn hơn 0")

    result = snapshot.copy()
    result["z_score"] = float("nan")
    result["is_outlier"] = False
    scores = result[total_col].dropna()
    if len(scores) < 2:
        return result

    std = scores.std(ddof=1)
    if pd.isna(std) or std == 0:
        return result

    result.loc[scores.index, "z_score"] = (scores - scores.mean()) / std
    result["is_outlier"] = result["z_score"].abs().gt(threshold).fillna(False).astype(bool)
    return result


def slope_pair(prov_year, year_start, year_end, total_col):
    """Ghép điểm một tỉnh ở hai năm để vẽ slopegraph, không suy diễn dữ liệu thiếu."""
    if year_start >= year_end:
        raise ValueError("year_start phải nhỏ hơn year_end")

    cols = ["province_id", "province_vi", "year", total_col]
    paired = (
        prov_year.loc[prov_year.year.isin([year_start, year_end]), cols]
        .dropna(subset=[total_col])
        .copy()
    )
    counts = paired.groupby("province_id", observed=True)["year"].nunique()
    paired = paired.loc[paired.province_id.isin(counts[counts.eq(2)].index)]
    if paired.empty:
        return pd.DataFrame(columns=["province_id", "province_vi", "score_start", "score_end", "delta"])

    scores = paired.pivot(index="province_id", columns="year", values=total_col)
    names = paired.drop_duplicates("province_id").set_index("province_id")["province_vi"]
    result = scores.rename(columns={year_start: "score_start", year_end: "score_end"}).join(names)
    result["delta"] = result["score_end"] - result["score_start"]
    return (
        result.reset_index()[["province_id", "province_vi", "score_start", "score_end", "delta"]]
        .sort_values(["delta", "province_vi"], ascending=[False, True])
        .reset_index(drop=True)
    )


def province_benchmarks(snapshot, region, province, total_col):
    """So sánh một tỉnh với trung bình vùng và trung bình toàn bộ snapshot."""
    province_rows = snapshot.loc[snapshot.province_vi.eq(province), ["province_vi", "region", total_col]]
    if province_rows.empty:
        raise ValueError(f"Không tìm thấy tỉnh {province!r} trong snapshot")
    row = province_rows.iloc[0]
    if row.region != region:
        raise ValueError(f"Tỉnh {province!r} không thuộc vùng {region!r}")

    region_mean = snapshot.loc[snapshot.region.eq(region), total_col].mean()
    national_mean = snapshot[total_col].mean()
    score = row[total_col]
    return {
        "province_score": float(score),
        "region_mean": float(region_mean),
        "national_mean": float(national_mean),
        "vs_region": float(score - region_mean),
        "vs_national": float(score - national_mean),
    }


def dimension_benchmarks(prov_year, year, region, province, dims):
    """Profile lĩnh vực của tỉnh so với trung bình vùng và toàn quốc trong cùng năm."""
    cols = ["province_vi", "region", *dims]
    snapshot = prov_year.loc[prov_year.year.eq(year), cols]
    province_rows = snapshot.loc[snapshot.province_vi.eq(province)]
    if province_rows.empty:
        raise ValueError(f"Không tìm thấy tỉnh {province!r} trong năm {year}")

    province_row = province_rows.iloc[0]
    region_mean = snapshot.loc[snapshot.region.eq(region), dims].mean()
    national_mean = snapshot[dims].mean()
    return pd.DataFrame({
        "code": dims,
        "province_score": [province_row[code] for code in dims],
        "region_mean": [region_mean[code] for code in dims],
        "national_mean": [national_mean[code] for code in dims],
    })
