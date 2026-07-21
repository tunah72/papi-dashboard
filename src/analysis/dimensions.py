"""Logic thuần cho Hướng 3 — quan hệ và phân tán giữa các lĩnh vực PAPI."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


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


def strongest_pair(snapshot, dims):
    """Cặp có |Pearson r| lớn nhất, bỏ đường chéo và cặp lặp."""
    matrix = correlation_matrix(snapshot, dims)
    candidates = [
        (x_code, y_code, matrix.loc[x_code, y_code])
        for x_index, x_code in enumerate(dims)
        for y_code in dims[x_index + 1:]
        if pd.notna(matrix.loc[x_code, y_code])
    ]
    if not candidates:
        return None, None, float("nan")
    return max(candidates, key=lambda item: (abs(item[2]), item[0], item[1]))


def correlation_strength(value):
    """Nhãn mô tả UI; không phải kiểm định thống kê hay bằng chứng nhân quả."""
    if pd.isna(value):
        return "không đủ dữ liệu"
    magnitude = abs(value)
    if magnitude < 0.3:
        return "yếu"
    if magnitude < 0.5:
        return "trung bình"
    if magnitude < 0.7:
        return "khá mạnh"
    return "mạnh"


def regression_snapshot(snapshot, x_code, y_code):
    """OLS mô tả cho cặp lĩnh vực, kèm predicted và residual theo tỉnh."""
    out = snapshot[["province_vi", "region", x_code, y_code]].dropna().copy()
    if len(out) < 2 or out[x_code].nunique() < 2:
        out["predicted"] = np.nan
        out["residual"] = np.nan
        return out, float("nan"), float("nan"), float("nan")
    model = LinearRegression().fit(out[[x_code]], out[y_code])
    out["predicted"] = model.predict(out[[x_code]])
    out["residual"] = out[y_code] - out["predicted"]
    return out, float(model.coef_[0]), float(model.intercept_), float(model.score(out[[x_code]], out[y_code]))
