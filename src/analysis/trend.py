"""Logic thuần cho Hướng 1 — diễn biến PAPI theo thời gian.

Mọi hàm ở đây nhận DataFrame đã xử lý (theo schema data.load_data) và trả về số/Series/dict.
KHÔNG import streamlit/plotly, KHÔNG vẽ, KHÔNG đọc file — để page H1 lẫn module AI
(technique trend_classification) gọi chung một nguồn sự thật, và để unit-test ngoài Streamlit.

Schema dùng tới:
- prov_year: wide panel 63 tỉnh × năm, có cột total_papi / total_papi_6dim và D1..D8.
- national:  long trung bình 63 tỉnh, cột [year, code, mean_score, ...].
"""
import pandas as pd


def total_by_year(prov_year, total_col, y0=None, y1=None):
    """Trung bình điểm tổng của 63 tỉnh theo từng năm.

    Trả về DataFrame [year, <total_col>] đã sắp theo năm, bỏ năm khuyết toàn bộ (mean NaN).
    y0/y1 (nếu có) lọc khoảng năm bao gồm hai đầu mút.
    """
    s = prov_year.groupby("year")[total_col].mean().reset_index().dropna()
    if y0 is not None:
        s = s[s.year >= y0]
    if y1 is not None:
        s = s[s.year <= y1]
    return s.sort_values("year").reset_index(drop=True)


def dim_deltas(national, dims, y0, y1):
    """Mức thay đổi mỗi lĩnh vực = điểm năm cuối − điểm năm đầu trong khoảng [y0, y1].

    Trả về Series index=code (theo thứ tự `dims`), value = delta (NaN nếu thiếu đầu/cuối).
    """
    sub = national[national.code.isin(dims) & national.year.between(y0, y1)]
    delta = (
        sub.sort_values("year")
        .groupby("code", observed=True)["mean_score"]
        .agg(lambda s: s.iloc[-1] - s.iloc[0] if len(s) else float("nan"))
    )
    return delta.reindex(dims)


def summarize_total(tot, total_col):
    """Tóm tắt chuỗi điểm tổng: hai đầu mút, mức ròng, đỉnh và đáy.

    `tot` là output của total_by_year. Trả dict gồm first/latest (năm),
    v_first/v_latest, net, peak_year/peak_val, dip_val. Rỗng → tất cả None/NaN.
    """
    if tot.empty:
        return {k: None for k in (
            "first", "latest", "v_first", "v_latest", "net",
            "peak_year", "peak_val", "dip_val")}
    first, latest = int(tot.year.min()), int(tot.year.max())
    
    first_rows = tot.loc[tot.year == first, total_col]
    latest_rows = tot.loc[tot.year == latest, total_col]
    
    v_first = float(first_rows.iloc[0]) if not first_rows.empty else float("nan")
    v_latest = float(latest_rows.iloc[0]) if not latest_rows.empty else float("nan")
    
    return {
        "first": first,
        "latest": latest,
        "v_first": v_first,
        "v_latest": v_latest,
        "net": v_latest - v_first if pd.notna(v_first) and pd.notna(v_latest) else float("nan"),
        "peak_year": int(tot.loc[tot[total_col].idxmax(), "year"]),
        "peak_val": float(tot[total_col].max()),
        "dip_val": float(tot[total_col].min()),
    }


def compare_periods(national, codes, before_years, after_years):
    """So sánh điểm trung bình hai giai đoạn cho mỗi lĩnh vực (vd trước/sau COVID).

    Trả dict code -> {"before", "after", "diff"}; thiếu dữ liệu giai đoạn nào → NaN.
    """
    out = {}
    for code in codes:
        g = national[national.code == code]
        before = g[g.year.isin(before_years)].mean_score.mean()
        after = g[g.year.isin(after_years)].mean_score.mean()
        diff = (after - before) if pd.notna(before) and pd.notna(after) else float("nan")
        out[code] = {"before": before, "after": after, "diff": diff}
    return out


def classify_change(value, eps=0.03):
    """Phân loại một mức thay đổi thành nhãn tiếng Việt trung tính.

    Kernel dùng chung cho nhãn biểu đồ H1 và technique AI trend_classification.
    |value| <= eps coi như không đổi (mặc định eps=0.03 điểm).
    """
    if pd.isna(value):
        return "không đủ dữ liệu"
    if value > eps:
        return "tăng"
    if value < -eps:
        return "giảm"
    return "gần như không đổi"


def regional_total_series(prov_year, total_col, y0, y1):
    """Trung bình điểm tổng theo vùng và năm trong khoảng được chọn."""
    return (
        prov_year.loc[
            prov_year.year.between(y0, y1),
            ["year", "region", total_col],
        ]
        .groupby(["year", "region"], observed=True)[total_col]
        .agg(score="mean", contributor_n="count")
        .reset_index()
        .sort_values(["region", "year"])
        .reset_index(drop=True)
    )


def regional_year_over_year(prov_year, total_col, y0, y1):
    """Mức thay đổi trung bình vùng so với năm liền trước trong range."""
    series = regional_total_series(prov_year, total_col, y0, y1)
    series["previous_score"] = series.groupby("region", observed=True)["score"].shift()
    series["change"] = series["score"] - series["previous_score"]
    return series.dropna(subset=["previous_score"]).reset_index(drop=True)


def focus_total_series(prov_year, total_col, y0, y1, region=None, province=None):
    """Chuỗi overlay cho vùng/tỉnh được chọn; không thay đổi chuỗi quốc gia."""
    years = pd.DataFrame({"year": list(range(y0, y1 + 1))})
    frames = []
    if region is not None:
        region_rows = (
            prov_year.loc[
                prov_year.year.between(y0, y1) & prov_year.region.eq(region),
                ["year", total_col],
            ]
            .groupby("year")[total_col]
            .agg(score="mean", contributor_n="count")
            .reset_index()
        )
        region_rows = years.merge(region_rows, on="year", how="left")
        region_rows["scope"] = "region"
        region_rows["label"] = region
        frames.append(region_rows)
    if province is not None:
        province_rows = prov_year.loc[
            prov_year.year.between(y0, y1) & prov_year.province_vi.eq(province),
            ["year", total_col],
        ].rename(columns={total_col: "score"})
        province_rows = years.merge(province_rows, on="year", how="left")
        province_rows["contributor_n"] = province_rows.score.notna().astype(int)
        province_rows["scope"] = "province"
        province_rows["label"] = province
        frames.append(province_rows)
    if not frames:
        return pd.DataFrame(columns=["year", "score", "contributor_n", "scope", "label"])
    return pd.concat(frames, ignore_index=True)[
        ["year", "score", "contributor_n", "scope", "label"]
    ]


def turning_points(total_series, total_col, limit=3):
    """Các biến động YoY lớn nhất theo trị tuyệt đối của chuỗi tổng quốc gia."""
    out = total_series[["year", total_col]].sort_values("year").copy()
    out["previous_score"] = out[total_col].shift()
    out["change"] = out[total_col] - out["previous_score"]
    out["from_year"] = out.year.shift().astype("Int64")
    return (
        out.dropna(subset=["change"])
        .assign(abs_change=lambda frame: frame.change.abs())
        .sort_values(["abs_change", "year"], ascending=[False, True])
        .head(limit)
        .drop(columns="abs_change")
        .rename(columns={total_col: "score"})
        .reset_index(drop=True)
    )
