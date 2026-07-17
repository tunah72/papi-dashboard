"""Logic thuần cho Hướng 3 — quan hệ và phân tán giữa các lĩnh vực PAPI."""
import pandas as pd


def snapshot_for_year(prov_year, year, dims):
    """Panel tỉnh cùng năm, chỉ giữ hàng đủ điểm cho các lĩnh vực đang so sánh."""
    cols = ["province_vi", "region", "year", *dims]
    return prov_year.loc[prov_year.year.eq(year), cols].dropna(subset=dims).copy()


def correlation_matrix(snapshot, dims):
    """Pearson correlation giữa các lĩnh vực, theo tỉnh trong một năm."""
    return snapshot[dims].corr().reindex(index=dims, columns=dims)


def summaries(snapshot, dims):
    """Trung bình và độ lệch chuẩn liên tỉnh của từng lĩnh vực."""
    out = pd.DataFrame({"code": dims, "mean_score": [snapshot[c].mean() for c in dims],
                        "std_score": [snapshot[c].std() for c in dims]})
    return out


def pair_snapshot(snapshot, x_code, y_code):
    """Dữ liệu scatter kèm phần tư theo trung bình mẫu và hệ số tương quan."""
    out = snapshot[["province_vi", "region", x_code, y_code]].dropna().copy()
    x_mean, y_mean = out[x_code].mean(), out[y_code].mean()
    out["quadrant"] = [
        ("Cao–cao" if x >= x_mean and y >= y_mean else
         "Thấp–thấp" if x < x_mean and y < y_mean else
         "Cao–thấp" if x >= x_mean else "Thấp–cao")
        for x, y in zip(out[x_code], out[y_code])
    ]
    corr = out[x_code].corr(out[y_code])
    return out, float(x_mean), float(y_mean), float(corr)
