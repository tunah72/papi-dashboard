"""Use cases dashboard Phase 1. Tái sử dụng logic nghiệp vụ trong ``src.analysis``."""
from __future__ import annotations

from functools import lru_cache

import pandas as pd

from src import data_loader
from src.analysis import dimensions, dynamics, provincial, trend

from server.view_models import SOURCE, records, response


SCALES = {
    "six": {"total_col": "total_papi_6dim", "dims": ["D1", "D2", "D3", "D4", "D5", "D6"], "year_min": 2011,
            "label": "Tổng 6 lĩnh vực gốc", "unit": "điểm tổng 6 lĩnh vực"},
    "eight": {"total_col": "total_papi", "dims": ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"], "year_min": 2018,
              "label": "Tổng PAPI (8 lĩnh vực)", "unit": "điểm tổng 8 lĩnh vực"},
}
REGION_ORDER = [
    "Trung du và miền núi phía Bắc", "Đồng bằng sông Hồng",
    "Bắc Trung Bộ và Duyên hải miền Trung", "Tây Nguyên", "Đông Nam Bộ",
    "Đồng bằng sông Cửu Long",
]


class ContractError(ValueError):
    """Lỗi input có thể hiển thị bằng tiếng Việt cho UI."""


@lru_cache(maxsize=1)
def data():
    return data_loader.load_processed_data()


def _scale(scale: str):
    if scale not in SCALES:
        raise ContractError("Tham số scale chỉ nhận 'six' hoặc 'eight'.")
    return SCALES[scale]


def _years(cfg):
    return sorted(int(year) for year in data()["prov_year"].year.unique() if int(year) >= cfg["year_min"])


def _year(cfg, year: int | None):
    available = _years(cfg)
    resolved = available[-1] if year is None else year
    if resolved not in available:
        raise ContractError(
            f"Năm {resolved} không khả dụng cho phạm vi đã chọn (có thể chọn {available[0]}–{available[-1]})."
        )
    return resolved


def _range(cfg, from_year: int | None, to_year: int | None):
    available = _years(cfg)
    start = available[0] if from_year is None else from_year
    end = available[-1] if to_year is None else to_year
    if start not in available or end not in available or start >= end:
        raise ContractError(
            f"Khoảng năm không hợp lệ. Chọn hai mốc khác nhau trong {available[0]}–{available[-1]} và from < to."
        )
    return start, end


def _labels():
    indicators = data()["dim_ind"].sort_values("sort")
    return dict(zip(indicators.code, indicators.name_vi))


def _artifact(rows, unit, caveats=None, **extra):
    """Metadata cho artifact con; rowCount luôn khác với n của statistic."""
    return {
        "rowCount": len(rows), "unit": unit, "source": SOURCE, "caveats": caveats or [],
        "rows": records(rows) if isinstance(rows, pd.DataFrame) else rows, **extra,
    }


def _contributors(year, columns):
    panel = data()["prov_year"].loc[data()["prov_year"].year.eq(year), columns]
    if isinstance(columns, str):
        return int(panel.notna().sum())
    return int(panel.dropna(subset=columns).shape[0])


def _indicator_rows(codes=None):
    indicators = data()["dim_ind"].sort_values("sort")
    if codes is not None:
        indicators = indicators[indicators.code.isin(codes)]
    return records(indicators)


def metadata():
    d = data()
    return response({
        "scales": [{"id": key, "label": cfg["label"], "years": _years(cfg), "dimensions": cfg["dims"], "totalColumn": cfg["total_col"]} for key, cfg in SCALES.items()],
        "dimensions": _indicator_rows(),
        "regions": [region for region in REGION_ORDER if region in set(d["dim_prov"].region)],
        "provinces": records(d["dim_prov"].sort_values("province_id")),
    }, n=len(d["dim_prov"]), filters={}, unit="metadata", caveats=["D7 và D8 chỉ có từ năm 2018."])


def geojson():
    features = data()["geojson"]["features"]
    return response({"geojson": data()["geojson"]}, n=len(features), filters={}, unit="địa giới tỉnh", caveats=["GeoJSON được chuẩn hoá trong bộ nhớ; file nguồn không bị sửa."])


def overview(scale="six", year=None):
    cfg = _scale(scale)
    year = _year(cfg, year)
    total = cfg["total_col"]
    snapshot = provincial.snapshot_for_year(data()["prov_year"], year, total)
    if snapshot.empty:
        raise ContractError("Không có dữ liệu cho năm và thước đo đã chọn.")
    ranking = snapshot.sort_values([total, "province_vi"], ascending=[False, True]).reset_index(drop=True)
    ranking["rank"] = ranking.index + 1
    map_rows = snapshot[["province_id", "province_vi", "region", total]].rename(columns={total: "score"})
    metrics = {
        "mean": float(snapshot[total].mean()), "min": float(snapshot[total].min()), "max": float(snapshot[total].max()),
        "leader": ranking.iloc[0]["province_vi"], "last": ranking.iloc[-1]["province_vi"], "gap": float(ranking.iloc[0][total] - ranking.iloc[-1][total]),
    }
    return response({
        "measure": {"id": total, "label": cfg["label"], "unit": cfg["unit"]}, "metrics": metrics,
        "map": _artifact(map_rows, cfg["unit"]),
        "ranking": _artifact(
            ranking.rename(columns={total: "score"}), cfg["unit"],
            top10=records(ranking.head(10).rename(columns={total: "score"})),
            bottom10=records(ranking.tail(10).sort_values([total, "province_vi"]).rename(columns={total: "score"})),
        ),
    }, n=len(snapshot), filters={"scale": scale, "year": year}, unit=cfg["unit"],
       caveats=["Chỉ tính các tỉnh có dữ liệu ở năm đã chọn; không giả định cố định 63 tỉnh."])


def trends(scale="six", from_year=None, to_year=None):
    cfg = _scale(scale)
    start, end = _range(cfg, from_year, to_year)
    total = cfg["total_col"]
    totals = trend.total_by_year(data()["prov_year"], total, start, end)
    if totals.empty:
        raise ContractError("Không có chuỗi tổng cho khoảng năm đã chọn.")
    deltas = trend.dim_deltas(data()["national"], cfg["dims"], start, end)
    labels = _labels()
    total_rows = totals.rename(columns={total: "score"}).copy()
    total_rows["contributor_n"] = total_rows.year.map(lambda year: _contributors(year, total))
    heat = data()["national"].loc[
        data()["national"].code.isin(cfg["dims"]) & data()["national"].year.between(start, end), ["year", "code", "mean_score"]
    ].copy()
    heat = heat.rename(columns={"mean_score": "score"})
    heat["label"] = heat["code"].map(labels)
    heat["contributor_n"] = heat.apply(lambda row: _contributors(int(row.year), row.code), axis=1)
    delta_rows = []
    for code, value in deltas.items():
        series = heat.loc[heat.code.eq(code)].sort_values("year")
        first_row, last_row = series.iloc[0], series.iloc[-1]
        delta_rows.append({
            "code": code, "label": labels[code], "delta": value,
            "from_score": first_row.score, "to_score": last_row.score,
            "contributor_n_from": int(first_row.contributor_n), "contributor_n_to": int(last_row.contributor_n),
        })
    covid_raw = trend.compare_periods(data()["national"], ["D6", "D8"], [2018, 2019], [2021, 2022])
    covid_rows = []
    for code, comparison in covid_raw.items():
        covid_rows.append({
            "code": code, "label": labels[code], "before_score": comparison["before"],
            "after_score": comparison["after"], "change": comparison["diff"],
            "contributor_n_before": sum(_contributors(year, code) for year in (2018, 2019)),
            "contributor_n_after": sum(_contributors(year, code) for year in (2021, 2022)),
        })
    primary_n = int(data()["prov_year"].loc[
        data()["prov_year"].year.between(start, end), total
    ].notna().sum())
    return response({
        "measure": {"id": total, "label": cfg["label"], "unit": cfg["unit"]},
        "summary": trend.summarize_total(totals, total),
        "totalSeries": _artifact(total_rows, cfg["unit"], caveats=["Mỗi điểm là trung bình tỉnh và contributorN là số tỉnh có dữ liệu."]),
        "dimensionSeries": _artifact(heat, "điểm lĩnh vực PAPI"),
        "dimensionDeltas": _artifact(delta_rows, "chênh lệch điểm lĩnh vực PAPI", caveats=["Dùng điểm đầu/cuối có dữ liệu trong khoảng."]),
        "covid": _artifact(covid_rows, "chênh lệch điểm lĩnh vực PAPI", available=bool(start <= 2019 and end >= 2021)),
        "heatmap": _artifact(heat, "điểm lĩnh vực PAPI"),
    }, n=primary_n, filters={"scale": scale, "from": start, "to": end}, unit=cfg["unit"],
       caveats=["D7 và D8 chưa có trước 2018.", "Các thay đổi lĩnh vực dùng năm đầu/cuối có dữ liệu trong khoảng."])


def provinces(scale="six", year=None, region=None, province=None):
    cfg = _scale(scale)
    year = _year(cfg, year)
    total = cfg["total_col"]
    snapshot = provincial.snapshot_for_year(data()["prov_year"], year, total)
    summary = provincial.region_summary(snapshot, total, REGION_ORDER)
    if summary.empty:
        raise ContractError("Không có dữ liệu tỉnh cho năm và thước đo đã chọn.")
    available_regions = summary.region.astype(str).tolist()
    province_regions = snapshot.set_index("province_vi").region.to_dict()
    if province is not None and province not in province_regions:
        raise ContractError("Tỉnh được chọn không có dữ liệu trong năm và phạm vi này.")
    inferred_region = province_regions.get(province) if province is not None else None
    if region is not None and inferred_region is not None and region != inferred_region:
        raise ContractError("Tỉnh được chọn không thuộc vùng đã chọn.")
    chosen_region = inferred_region or (str(summary.iloc[0].region) if region is None else region)
    if chosen_region not in available_regions:
        raise ContractError("Vùng được chọn không có dữ liệu trong năm và phạm vi này.")
    ranking = provincial.ranking_in_region(snapshot, chosen_region, total)
    available_provinces = ranking.province_vi.tolist()
    chosen_province = available_provinces[0] if province is None else province
    if chosen_province not in available_provinces:
        raise ContractError("Tỉnh được chọn không thuộc vùng đã chọn hoặc không có dữ liệu.")
    benchmarks = provincial.province_benchmarks(snapshot, chosen_region, chosen_province, total)
    profile = provincial.dimension_benchmarks(data()["prov_year"], year, chosen_region, chosen_province, cfg["dims"])
    profile["region_n"] = [int(data()["prov_year"].loc[
        data()["prov_year"].year.eq(year) & data()["prov_year"].region.eq(chosen_region), code
    ].notna().sum()) for code in cfg["dims"]]
    profile["national_n"] = [int(data()["prov_year"].loc[data()["prov_year"].year.eq(year), code].notna().sum()) for code in cfg["dims"]]
    summary = summary.rename(columns={"n_provinces": "n"})
    distribution = snapshot.rename(columns={total: "score"})
    ranking_rows = ranking.rename(columns={total: "score"})
    benchmarks.update({
        "unit": cfg["unit"], "source": SOURCE, "caveats": ["So sánh cùng năm và cùng phạm vi scale."],
        "region_n": int(snapshot.loc[snapshot.region.eq(chosen_region), total].notna().sum()),
        "national_n": int(snapshot[total].notna().sum()),
    })
    return response({
        "measure": {"id": total, "label": cfg["label"], "unit": cfg["unit"]},
        "distribution": _artifact(distribution, cfg["unit"]),
        "regionMeans": _artifact(summary, cfg["unit"]),
        "ranking": _artifact(ranking_rows, cfg["unit"]),
        "benchmark": benchmarks,
        "profile": _artifact(profile, "điểm lĩnh vực PAPI"),
        "availability": {"regions": available_regions, "provinces": available_provinces},
    }, n=len(snapshot), filters={"scale": scale, "year": year, "region": chosen_region, "province": chosen_province}, unit=cfg["unit"],
       caveats=["Benchmark toàn quốc chỉ dùng các tỉnh có dữ liệu của snapshot; profile dùng cùng năm."])


def dimensions_view(scale="six", year=None, x=None, y=None):
    cfg = _scale(scale)
    year = _year(cfg, year)
    dims = cfg["dims"]
    if x is not None and x not in dims or y is not None and y not in dims:
        raise ContractError("Hai lĩnh vực x và y phải thuộc phạm vi scale đã chọn.")
    if x is None and y is None:
        x, y = dims[min(1, len(dims) - 1)], dims[0]
    elif x is None:
        x = next(code for code in dims if code != y)
    elif y is None:
        y = next(code for code in dims if code != x)
    if x == y:
        raise ContractError("Hai lĩnh vực x và y phải khác nhau và thuộc phạm vi scale đã chọn.")
    snapshot = dimensions.snapshot_for_year(data()["prov_year"], year, dims)
    if snapshot.empty:
        raise ContractError("Không đủ dữ liệu lĩnh vực cho năm đã chọn.")
    matrix = dimensions.correlation_matrix(snapshot, dims)
    pair, x_mean, y_mean, corr = dimensions.pair_snapshot(snapshot, x, y)
    summary = dimensions.summaries(snapshot, dims)
    labels = _labels()
    pair_rows = pair.rename(columns={"province_vi": "province_vi", x: "x", y: "y"})
    summary["n"] = len(snapshot)
    return response({
        "availability": {"dimensions": dims},
        "correlation": {
            "rowCount": len(dims), "unit": "không đơn vị", "source": SOURCE, "caveats": [],
            "n": len(snapshot), "codes": dims, "matrix": matrix.values.tolist(),
        },
        "pair": _artifact(pair_rows, "điểm lĩnh vực PAPI", n=len(pair), x=x, y=y, xMean=x_mean, yMean=y_mean, pearsonR=corr),
        "standardDeviation": _artifact(summary, "điểm lĩnh vực PAPI"),
        "labels": _indicator_rows(dims),
    }, n=len(snapshot), filters={"scale": scale, "year": year, "x": x, "y": y}, unit="điểm lĩnh vực PAPI",
       caveats=["Pearson r là mối liên hệ quan sát, không chứng minh quan hệ nhân quả."])


def dynamics_view(scale="six", from_year=None, to_year=None):
    cfg = _scale(scale)
    start, end = _range(cfg, from_year, to_year)
    total = cfg["total_col"]
    changes = dynamics.changes(data()["prov_year"], total, start, end)
    clusters = dynamics.cluster_profiles(data()["prov_year"], end, cfg["dims"], 4)
    if changes.empty or clusters.empty:
        raise ContractError("Không đủ dữ liệu cho so sánh thay đổi hoặc phân nhóm.")
    change_rows = changes.rename(columns={start: "from_score", end: "to_score"})
    centroids = clusters.groupby("cluster", observed=True)[cfg["dims"]].mean().reset_index().sort_values("cluster")
    cluster_sizes = clusters.groupby("cluster", observed=True).size()
    centroids["n"] = centroids.cluster.map(cluster_sizes).astype(int)
    profiles = [{"cluster": cluster, "n": len(group), "provinces": records(group[["province_vi", "region"]].sort_values("province_vi"))}
                for cluster, group in clusters.groupby("cluster", observed=True)]
    return response({
        "measure": {"id": total, "label": cfg["label"], "unit": cfg["unit"]},
        "changes": _artifact(
            change_rows, "chênh lệch điểm PAPI", n=len(change_rows),
            top8=records(change_rows.head(8)), bottom8=records(change_rows.tail(8).sort_values("change")),
        ),
        "clusters": {
            "rowCount": len(clusters), "unit": "điểm lĩnh vực PAPI", "source": SOURCE,
            "caveats": ["KMeans chuẩn hoá các lĩnh vực trước khi phân cụm."],
            "n": len(clusters), "count": int(clusters.cluster.nunique()), "randomState": 42,
            "rows": records(clusters), "centroids": records(centroids), "profiles": profiles,
        },
    }, n=len(changes), filters={"scale": scale, "from": start, "to": end}, unit=cfg["unit"],
       caveats=["KMeans chuẩn hoá các lĩnh vực và dùng random_state=42; cụm không phải xếp hạng.", "Chỉ tỉnh đủ dữ liệu ở cả hai mốc mới có delta."])
