"""Logic thuần H4: thay đổi đầu-cuối và KMeans trên profile lĩnh vực."""
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def changes(prov_year, total_col, y0, y1):
    """Điểm cuối trừ điểm đầu cho các tỉnh có đủ hai mốc."""
    p = prov_year[prov_year.year.isin([y0, y1])][["province_vi", "region", "year", total_col]]
    wide = p.pivot_table(index=["province_vi", "region"], columns="year", values=total_col, observed=True).dropna()
    wide["change"] = wide[y1] - wide[y0]
    return wide.reset_index().sort_values("change", ascending=False).reset_index(drop=True)


def cluster_profiles(prov_year, year, dims, n_clusters=4):
    """Chuẩn hoá các lĩnh vực rồi phân nhóm tỉnh; trả profile và nhãn cụm ổn định."""
    data = prov_year.loc[prov_year.year.eq(year), ["province_vi", "region", *dims]].dropna().copy()
    n_clusters = min(n_clusters, len(data))
    scaled = StandardScaler().fit_transform(data[dims])
    labels = KMeans(n_clusters=n_clusters, n_init=20, random_state=42).fit_predict(scaled)
    data["cluster"] = labels.astype(str)
    return data
