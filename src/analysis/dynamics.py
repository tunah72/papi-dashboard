"""Logic thuần H4: thay đổi đầu-cuối và KMeans trên profile lĩnh vực."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
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


def _endpoint_profiles(prov_year, y0, y1, dims):
    """Hai endpoint chỉ gồm các tỉnh hoàn chỉnh ở cả hai mốc."""
    columns = ["province_vi", "region", "year", *dims]
    endpoints = prov_year.loc[prov_year.year.isin([y0, y1]), columns].dropna(subset=dims).copy()
    counts = endpoints.groupby(["province_vi", "region"], observed=True).year.nunique()
    complete = counts[counts.eq(2)].index
    indexed = endpoints.set_index(["province_vi", "region"])
    return indexed.loc[indexed.index.isin(complete)].reset_index()


def _year_standardize(frame, dims):
    """Chuẩn hoá tương đối trong từng năm để loại dịch chuyển mặt bằng chung."""
    grouped = frame.groupby("year", observed=True)[dims]
    means = grouped.transform("mean")
    deviations = grouped.transform(lambda values: values.std(ddof=0)).replace(0, 1)
    return ((frame[dims] - means) / deviations).fillna(0.0)


def cluster_transitions(prov_year, y0, y1, dims, requested_k=None, k_min=2, k_max=6):
    """Phân cụm chung hai mốc, chọn K bằng silhouette và chiếu PCA 2D.

    Nhãn cụm chỉ ổn định trong một truy vấn. Chúng được sắp lại A..F theo
    trung bình centroid z-score để output deterministic với cùng input.
    """
    endpoints = _endpoint_profiles(prov_year, y0, y1, dims)
    if endpoints.empty:
        return {
            "endpoints": endpoints, "assignments": pd.DataFrame(), "centroids": [],
            "transitions": [], "candidates": [], "selected_k": 0,
            "silhouette": float("nan"), "pca_variance": [], "selection_mode": "auto",
        }
    standardized = _year_standardize(endpoints, dims)
    max_candidate = min(k_max, len(standardized) - 1)
    candidate_ks = list(range(k_min, max_candidate + 1))
    candidates = []
    fitted = {}
    for k_value in candidate_ks:
        labels = KMeans(n_clusters=k_value, n_init=50, random_state=42).fit_predict(standardized)
        score = silhouette_score(standardized, labels) if len(set(labels)) > 1 else float("nan")
        candidates.append({"k": k_value, "silhouette": float(score)})
        fitted[k_value] = labels
    if not candidates:
        raise ValueError("Không đủ profile để đánh giá tối thiểu hai cụm.")
    valid_requested = requested_k in fitted
    selected_k = requested_k if valid_requested else max(
        candidates, key=lambda item: (item["silhouette"], -item["k"])
    )["k"]
    selection_mode = "manual" if valid_requested else "auto"
    model = KMeans(n_clusters=selected_k, n_init=50, random_state=42).fit(standardized)
    centers = model.cluster_centers_
    order = sorted(
        range(selected_k),
        key=lambda index: (float(np.mean(centers[index])), *centers[index].tolist()),
    )
    remap = {old: chr(65 + new) for new, old in enumerate(order)}
    endpoints = endpoints.copy()
    endpoints["cluster"] = pd.Series(model.labels_, index=endpoints.index).map(remap)
    for code in dims:
        endpoints[f"z_{code}"] = standardized[code].to_numpy()
    component_count = min(2, len(dims), len(endpoints))
    pca = PCA(n_components=component_count, random_state=42).fit(standardized)
    projection = pca.transform(standardized)
    endpoints["pc1"] = projection[:, 0]
    endpoints["pc2"] = projection[:, 1] if component_count > 1 else 0.0

    pivot = endpoints.pivot(index=["province_vi", "region"], columns="year")
    assignment_rows = []
    for (province, region), row in pivot.iterrows():
        assignment_rows.append({
            "province_vi": province, "region": region,
            "start_cluster": row[("cluster", y0)], "end_cluster": row[("cluster", y1)],
            "changed": row[("cluster", y0)] != row[("cluster", y1)],
            "start_pc1": row[("pc1", y0)], "start_pc2": row[("pc2", y0)],
            "end_pc1": row[("pc1", y1)], "end_pc2": row[("pc2", y1)],
        })
    assignments = pd.DataFrame(assignment_rows).sort_values("province_vi").reset_index(drop=True)

    centroids = []
    for cluster, group in endpoints.groupby("cluster", observed=True, sort=True):
        values = [{
            "code": code,
            "z_score": float(group[f"z_{code}"].mean()),
            "raw_score": float(group[code].mean()),
        } for code in dims]
        strongest = sorted(values, key=lambda item: item["z_score"], reverse=True)[:2]
        weakest = sorted(values, key=lambda item: item["z_score"])[:2]
        centroids.append({
            "cluster": cluster,
            "n_start": int((group.year == y0).sum()), "n_end": int((group.year == y1).sum()),
            "descriptor": (
                f"Mạnh tương đối: {', '.join(item['code'] for item in strongest)}; "
                f"yếu tương đối: {', '.join(item['code'] for item in weakest)}"
            ),
            "values": values,
        })

    transitions = []
    for (start_cluster, end_cluster), group in assignments.groupby(
        ["start_cluster", "end_cluster"], observed=True, sort=True
    ):
        transitions.append({
            "from_cluster": start_cluster, "to_cluster": end_cluster, "n": len(group),
            "provinces": group.province_vi.sort_values().tolist(),
        })
    selected_score = next(item["silhouette"] for item in candidates if item["k"] == selected_k)
    return {
        "endpoints": endpoints, "assignments": assignments, "centroids": centroids,
        "transitions": transitions, "candidates": candidates, "selected_k": int(selected_k),
        "silhouette": float(selected_score), "pca_variance": pca.explained_variance_ratio_.tolist(),
        "selection_mode": selection_mode,
    }
