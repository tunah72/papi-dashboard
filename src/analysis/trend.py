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
    v_first = float(tot.loc[tot.year == first, total_col].iloc[0])
    v_latest = float(tot.loc[tot.year == latest, total_col].iloc[0])
    return {
        "first": first,
        "latest": latest,
        "v_first": v_first,
        "v_latest": v_latest,
        "net": v_latest - v_first,
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
