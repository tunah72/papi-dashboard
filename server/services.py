"""Use case Dashboard, tái sử dụng logic nghiệp vụ trong ``src.analysis``."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
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


def _vi_number(value, digits=2):
    """Định dạng số ngắn cho insight tiếng Việt, không thay đổi giá trị artifact."""
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.{digits}f}".replace(".", ",")


def _annual_changes(trend_rows):
    rows = trend_rows.copy()
    rows["previous_score"] = rows.score.shift()
    rows["change"] = rows.score.diff()
    rows["previous_contributor_n"] = rows.contributor_n.shift().fillna(0).astype(int)
    rows["baseline"] = rows.previous_score.isna()
    deltas = rows.dropna(subset=["change"])
    increases = deltas.loc[deltas.change.gt(0)]
    decreases = deltas.loc[deltas.change.lt(0)]
    largest_increase = increases.loc[increases.change.idxmax()] if not increases.empty else None
    largest_decrease = decreases.loc[decreases.change.idxmin()] if not decreases.empty else None
    return rows, largest_increase, largest_decrease


def _quadrant_summary(pair_rows):
    order = ["Cao–cao", "Cao–thấp", "Thấp–cao", "Thấp–thấp"]
    total = len(pair_rows)
    result = []
    for label in order:
        group = pair_rows.loc[pair_rows.quadrant.eq(label)]
        result.append({
            "label": label,
            "n": len(group),
            "percentage": (len(group) / total * 100) if total else 0,
            "provinces": sorted(group.province_vi.astype(str).tolist()),
        })
    return result


def _change_distribution(change_rows, start, end):
    n = len(change_rows)
    if not n:
        return {
            "n": 0, "fromYear": start, "toYear": end, "median": None,
            "positiveN": 0, "negativeN": 0, "unchangedN": 0,
            "positivePercentage": 0, "bins": [], "rows": [],
        }
    values = change_rows.change.astype(float).to_numpy()
    bin_count = max(6, min(12, int(round(np.sqrt(n)))))
    counts, edges = np.histogram(values, bins=bin_count)
    bins = []
    for index, count in enumerate(counts):
        lower, upper = float(edges[index]), float(edges[index + 1])
        inclusive = change_rows.change.le(upper) if index == len(counts) - 1 else change_rows.change.lt(upper)
        members = change_rows.loc[change_rows.change.ge(lower) & inclusive, "province_vi"]
        bins.append({
            "lower": lower, "upper": upper, "center": (lower + upper) / 2,
            "count": int(count), "percentage": float(count / n * 100),
            "provinces": sorted(members.astype(str).tolist()),
        })
    positive_n = int((change_rows.change > 0).sum())
    negative_n = int((change_rows.change < 0).sum())
    unchanged_n = n - positive_n - negative_n
    return {
        "n": n, "fromYear": start, "toYear": end,
        "median": float(change_rows.change.median()),
        "positiveN": positive_n, "negativeN": negative_n, "unchangedN": unchanged_n,
        "positivePercentage": float(positive_n / n * 100),
        "bins": bins, "rows": records(change_rows),
    }


def _focus(region=None, province=None):
    """Xác thực focus vùng/tỉnh dùng cho chuỗi linked-selection."""
    provinces = data()["dim_prov"].set_index("province_vi").region.astype(str).to_dict()
    regions = set(data()["dim_prov"].region.astype(str))
    if province is not None and province not in provinces:
        raise ContractError("Tỉnh được chọn không tồn tại trong danh mục PAPI.")
    inferred_region = provinces.get(province) if province is not None else None
    if region is not None and region not in regions:
        raise ContractError("Vùng được chọn không tồn tại trong danh mục PAPI.")
    if region is not None and inferred_region is not None and region != inferred_region:
        raise ContractError("Tỉnh được chọn không thuộc vùng đã chọn.")
    return inferred_region or region, province


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


def overview(scale="eight", year=None):
    cfg = _scale(scale)
    year = _year(cfg, year)
    total = cfg["total_col"]
    snapshot = provincial.snapshot_for_year(data()["prov_year"], year, total)
    if snapshot.empty:
        raise ContractError("Không có dữ liệu cho năm và thước đo đã chọn.")
    ranking = snapshot.sort_values([total, "province_vi"], ascending=[False, True]).reset_index(drop=True)
    ranking["rank"] = ranking.index + 1
    map_rows = ranking[["province_id", "province_vi", "region", total, "rank"]].rename(columns={total: "score"})
    metrics = {
        "mean": float(snapshot[total].mean()), "min": float(snapshot[total].min()), "max": float(snapshot[total].max()),
        "leader": ranking.iloc[0]["province_vi"], "last": ranking.iloc[-1]["province_vi"], "gap": float(ranking.iloc[0][total] - ranking.iloc[-1][total]),
    }
    start = cfg["year_min"]
    trend_rows = trend.total_by_year(data()["prov_year"], total, start, year).rename(columns={total: "score"})
    trend_rows["contributor_n"] = trend_rows.year.map(lambda item: _contributors(item, total))
    annual_rows, largest_increase, largest_decrease = _annual_changes(trend_rows)
    regions = provincial.region_summary(snapshot, total, REGION_ORDER).rename(columns={"n_provinces": "n"})
    dimension_snapshot = dimensions.snapshot_for_year(data()["prov_year"], year, cfg["dims"])
    x_code, y_code, _ = dimensions.strongest_pair(dimension_snapshot, cfg["dims"])
    if x_code is None or y_code is None:
        pair_rows = pd.DataFrame(columns=["province_vi", "region", "x", "y", "quadrant"])
        x_mean = y_mean = corr = float("nan")
        x_code = y_code = ""
    else:
        pair_rows, x_mean, y_mean, corr = dimensions.pair_snapshot(dimension_snapshot, x_code, y_code)
        pair_rows = pair_rows.rename(columns={x_code: "x", y_code: "y"})
    if year > start:
        highlight_rows = dynamics.changes(data()["prov_year"], total, start, year).rename(
            columns={start: "from_score", year: "to_score"}
        )
    else:
        highlight_rows = pd.DataFrame(columns=["province_vi", "region", "from_score", "to_score", "change"])
    highlight_n = len(highlight_rows)
    quadrants = _quadrant_summary(pair_rows)
    change_distribution = _change_distribution(highlight_rows, start, year)
    largest_quadrant = max(quadrants, key=lambda item: item["n"]) if quadrants else None
    map_insight = (
        f"{metrics['leader']} cao nhất với {_vi_number(metrics['max'])}; "
        f"{metrics['last']} thấp nhất với {_vi_number(metrics['min'])}, cách nhau {_vi_number(metrics['gap'])} điểm."
    )
    if largest_increase is not None and largest_decrease is not None:
        annual_insight = (
            f"Tăng mạnh nhất vào {int(largest_increase.year)} (+{_vi_number(largest_increase.change)}); "
            f"giảm mạnh nhất vào {int(largest_decrease.year)} ({_vi_number(largest_decrease.change)})."
        )
    elif largest_increase is not None:
        annual_insight = f"Mặt bằng chỉ tăng trong phạm vi đang xem; tăng mạnh nhất vào {int(largest_increase.year)} (+{_vi_number(largest_increase.change)})."
    elif largest_decrease is not None:
        annual_insight = f"Mặt bằng chỉ giảm trong phạm vi đang xem; giảm mạnh nhất vào {int(largest_decrease.year)} ({_vi_number(largest_decrease.change)})."
    else:
        annual_insight = "Chưa đủ hai mốc năm để tính thay đổi năm-kề-năm."
    quadrant_insight = (
        f"{x_code} × {y_code} có r = {_vi_number(corr)}; nhóm {largest_quadrant['label']} "
        f"chiếm nhiều nhất với {largest_quadrant['n']}/{len(pair_rows)} tỉnh. Liên hệ này không hàm ý nhân quả."
        if largest_quadrant and len(pair_rows) else "Không đủ dữ liệu để phân nhóm bốn góc."
    )
    change_insight = (
        f"{_vi_number(change_distribution['positivePercentage'], 1)}% tỉnh tăng điểm; trung vị thay đổi "
        f"là {_vi_number(change_distribution['median'])} trên {highlight_n} tỉnh đủ hai mốc."
        if highlight_n else "Chưa đủ hai mốc để tính thay đổi của tỉnh."
    )
    return response({
        "measure": {"id": total, "label": cfg["label"], "unit": cfg["unit"]}, "metrics": metrics,
        "map": _artifact(map_rows, cfg["unit"]),
        "ranking": _artifact(
            ranking.rename(columns={total: "score"}), cfg["unit"],
            top10=records(ranking.head(10).rename(columns={total: "score"})),
            bottom10=records(ranking.tail(10).sort_values([total, "province_vi"]).rename(columns={total: "score"})),
        ),
        "storyCards": {
            "trend": _artifact(trend_rows, cfg["unit"]),
            "regions": _artifact(regions, cfg["unit"]),
            "strongestPair": _artifact(
                pair_rows, "điểm lĩnh vực PAPI", n=len(pair_rows), x=x_code, y=y_code,
                xMean=x_mean, yMean=y_mean, pearsonR=corr,
                caveats=["Pearson r là mối liên hệ quan sát, không chứng minh quan hệ nhân quả."],
            ),
            "changeHighlights": _artifact(
                highlight_rows, "chênh lệch điểm PAPI", n=highlight_n,
                median=float(highlight_rows.change.median()) if highlight_n else None,
                top8=records(highlight_rows.head(8)),
                bottom8=records(highlight_rows.tail(8).sort_values("change")) if highlight_n else [],
                caveats=["Chỉ tỉnh đủ dữ liệu ở cả hai mốc mới có delta."],
            ),
            "annualChanges": _artifact(
                annual_rows, cfg["unit"],
                largestIncreaseYear=int(largest_increase.year) if largest_increase is not None else None,
                largestIncrease=float(largest_increase.change) if largest_increase is not None else None,
                largestDecreaseYear=int(largest_decrease.year) if largest_decrease is not None else None,
                largestDecrease=float(largest_decrease.change) if largest_decrease is not None else None,
            ),
            "quadrants": {
                "rowCount": len(quadrants), "unit": "tỷ lệ tỉnh", "source": SOURCE,
                "caveats": ["Pearson r là mối liên hệ quan sát, không chứng minh quan hệ nhân quả."],
                "n": len(pair_rows), "x": x_code, "y": y_code, "pearsonR": corr, "rows": quadrants,
            },
            "changeDistribution": {
                "rowCount": len(change_distribution["bins"]), "unit": "chênh lệch điểm PAPI",
                "source": SOURCE, "caveats": ["Chỉ tỉnh đủ dữ liệu ở cả hai mốc mới có delta."],
                **change_distribution,
            },
        },
        "insights": {
            "map": map_insight, "annualChange": annual_insight,
            "quadrants": quadrant_insight, "changeDistribution": change_insight,
        },
    }, n=len(snapshot), filters={"scale": scale, "year": year}, unit=cfg["unit"],
       caveats=["Chỉ tính các tỉnh có dữ liệu ở năm đã chọn; không giả định cố định 63 tỉnh."])


def trends(scale="six", from_year=None, to_year=None, region=None, province=None):
    cfg = _scale(scale)
    start, end = _range(cfg, from_year, to_year)
    region, province = _focus(region, province)
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
    regional_rows = trend.regional_total_series(data()["prov_year"], total, start, end)
    regional_yoy = trend.regional_year_over_year(data()["prov_year"], total, start, end)
    regional_ranks = trend.regional_ranks(data()["prov_year"], total, start, end)
    selected_rows = trend.focus_total_series(data()["prov_year"], total, start, end, region, province)
    turning_rows = trend.turning_points(totals, total)
    summary = trend.summarize_total(totals, total)
    net = summary["net"]
    total_insight = (
        f"Điểm {'tăng' if net >= 0 else 'giảm'} {_vi_number(abs(net))} từ {start} đến {end}; "
        f"mức cao nhất {_vi_number(summary['peak_val'])} xuất hiện năm {summary['peak_year']}."
        if net is not None and not pd.isna(net) else "Không đủ dữ liệu để so sánh đầu và cuối kỳ."
    )
    if regional_yoy.empty:
        yoy_insight = "Không đủ hai năm liên tiếp để so sánh nhịp thay đổi theo vùng."
    else:
        grouped = regional_yoy.groupby("year", observed=True).change
        direction = grouped.apply(lambda values: "tăng" if (values > 0).sum() >= (values < 0).sum() else "giảm")
        counts = grouped.apply(lambda values: max(int((values > 0).sum()), int((values < 0).sum())))
        year = int(counts.idxmax())
        candidates = regional_yoy.loc[regional_yoy.year.eq(year)]
        strongest = candidates.loc[candidates.change.abs().idxmax()]
        yoy_insight = f"Năm {year} có {int(counts.loc[year])}/6 vùng cùng {direction.loc[year]}; {strongest.region} biến động mạnh nhất với {_vi_number(strongest.change, 2)} điểm."
    if regional_ranks.empty:
        rank_insight = "Không đủ dữ liệu để so sánh thứ hạng vùng."
    else:
        pivot = regional_ranks.pivot(index="region", columns="year", values="rank").dropna()
        moves = (pivot[end] - pivot[start]).astype(float)
        up_region, down_region = moves.idxmin(), moves.idxmax()
        up, down = int(-moves.loc[up_region]), int(moves.loc[down_region])
        rank_insight = (
            f"{up_region} tăng {up} bậc từ đầu kỳ; {down_region} giảm nhiều nhất với {down} bậc."
            if up > 0 or down > 0 else "Thứ tự vùng ổn định; không vùng nào thay đổi bậc trong khoảng đã chọn."
        )
    valid_deltas = [row for row in delta_rows if row["delta"] is not None]
    best = max(valid_deltas, key=lambda row: row["delta"], default=None)
    worst = min(valid_deltas, key=lambda row: row["delta"], default=None)
    if best and worst:
        best_phrase = "tăng mạnh nhất" if best["delta"] >= 0 else "giảm ít nhất"
        worst_phrase = "giảm mạnh nhất" if worst["delta"] < 0 else "tăng ít nhất"
        dimension_insight = (
            f"{best['label']} {best_phrase} ({_vi_number(best['delta'])}); "
            f"{worst['label']} {worst_phrase} ({_vi_number(worst['delta'])})."
        )
    else:
        dimension_insight = "Không đủ dữ liệu lĩnh vực ở cả hai mốc để tính thay đổi."
    return response({
        "measure": {"id": total, "label": cfg["label"], "unit": cfg["unit"]},
        "summary": summary,
        "totalSeries": _artifact(total_rows, cfg["unit"], caveats=["Mỗi điểm là trung bình tỉnh và contributorN là số tỉnh có dữ liệu."]),
        "dimensionSeries": _artifact(heat, "điểm lĩnh vực PAPI"),
        "dimensionDeltas": _artifact(delta_rows, "chênh lệch điểm lĩnh vực PAPI", caveats=["Dùng điểm đầu/cuối có dữ liệu trong khoảng."]),
        "covid": _artifact(covid_rows, "chênh lệch điểm lĩnh vực PAPI", available=bool(start <= 2019 and end >= 2021)),
        "heatmap": _artifact(heat, "điểm lĩnh vực PAPI"),
        "regionalSeries": _artifact(regional_rows, cfg["unit"]),
        "regionalYearOverYear": _artifact(regional_yoy, f"chênh lệch {cfg['unit']}"),
        "regionalRanks": _artifact(regional_ranks, "hạng vùng", caveats=["Hạng 1 là cao nhất; đồng hạng dùng rank(method='min')."]),
        "selectedSeries": _artifact(selected_rows, cfg["unit"]),
        "turningPoints": _artifact(turning_rows, f"chênh lệch {cfg['unit']}"),
        "insights": {"total": total_insight, "regionalYearOverYear": yoy_insight, "regionalRank": rank_insight, "dimensions": dimension_insight},
    }, n=primary_n, filters={"scale": scale, "from": start, "to": end, "region": region, "province": province}, unit=cfg["unit"],
       caveats=["D7 và D8 chưa có trước 2018.", "Các thay đổi lĩnh vực dùng năm đầu/cuối có dữ liệu trong khoảng."])


def provinces(scale="eight", year=None, region=None, province=None):
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
    distribution["rank"] = distribution["score"].rank(method="min", ascending=False).astype(int)
    ranking_rows = ranking.rename(columns={total: "score"})
    national_scores = snapshot[total].dropna()
    benchmarks.update({
        "unit": cfg["unit"], "source": SOURCE, "caveats": ["So sánh cùng năm và cùng phạm vi scale."],
        "region_n": int(snapshot.loc[snapshot.region.eq(chosen_region), total].notna().sum()),
        "national_n": int(snapshot[total].notna().sum()),
        "national_min": float(national_scores.min()),
        "national_max": float(national_scores.max()),
        "national_q1": float(national_scores.quantile(0.25)),
        "national_q3": float(national_scores.quantile(0.75)),
        "rank_region": int(ranking.loc[ranking.province_vi.eq(chosen_province), "rank_region"].iloc[0]),
        "region_total": len(ranking),
    })
    highest_region = summary.loc[summary.median_score.idxmax()]
    widest_region = summary.loc[summary.iqr.idxmax()]
    distribution_insight = (
        f"{highest_region.region} có trung vị cao nhất ({_vi_number(highest_region.median_score)}); "
        f"{widest_region.region} phân hóa rộng nhất với IQR {_vi_number(widest_region.iqr)} điểm."
    )
    selected_rank = int(benchmarks["rank_region"])
    leader = ranking.iloc[0]
    selected_score = float(benchmarks["province_score"])
    if selected_rank == 1:
        peers = ranking.loc[ranking[total].lt(selected_score)]
        if ranking[total].eq(selected_score).sum() > 1:
            ranking_insight = f"{chosen_province} đồng hạng dẫn đầu vùng với {_vi_number(selected_score)} điểm."
        elif peers.empty:
            ranking_insight = f"{chosen_province} là tỉnh duy nhất có dữ liệu trong vùng."
        else:
            ranking_insight = (
                f"{chosen_province} dẫn đầu vùng, cao hơn vị trí kế tiếp "
                f"{_vi_number(selected_score - float(peers.iloc[0][total]))} điểm."
            )
    else:
        ranking_insight = (
            f"{chosen_province} đứng hạng {selected_rank}/{len(ranking)}, thấp hơn {leader.province_vi} "
            f"{_vi_number(float(leader[total]) - selected_score)} điểm."
        )
    benchmark_insight = (
        f"{chosen_province} {'cao hơn' if benchmarks['vs_region'] >= 0 else 'thấp hơn'} vùng "
        f"{_vi_number(abs(benchmarks['vs_region']))} điểm và "
        f"{'cao hơn' if benchmarks['vs_national'] >= 0 else 'thấp hơn'} toàn bộ mẫu "
        f"{_vi_number(abs(benchmarks['vs_national']))} điểm."
    )
    profile_valid = profile.dropna(subset=["province_score", "region_mean"]).copy()
    profile_valid["delta"] = profile_valid.province_score - profile_valid.region_mean
    if profile_valid.empty:
        profile_insight = "Không đủ dữ liệu lĩnh vực để so sánh tỉnh với vùng."
    else:
        labels = _labels()
        strongest = profile_valid.loc[profile_valid.delta.idxmax()]
        weakest = profile_valid.loc[profile_valid.delta.idxmin()]
        strong_phrase = "vượt vùng nhiều nhất" if strongest.delta >= 0 else "gần vùng nhất"
        weak_phrase = "thấp hơn vùng nhiều nhất" if weakest.delta < 0 else "vượt vùng ít nhất"
        profile_insight = (
            f"{labels.get(strongest.code, strongest.code)} {strong_phrase} ({_vi_number(strongest.delta)}); "
            f"{labels.get(weakest.code, weakest.code)} {weak_phrase} ({_vi_number(weakest.delta)})."
        )
    return response({
        "measure": {"id": total, "label": cfg["label"], "unit": cfg["unit"]},
        "distribution": _artifact(distribution, cfg["unit"]),
        "regionMeans": _artifact(summary, cfg["unit"]),
        "ranking": _artifact(ranking_rows, cfg["unit"]),
        "benchmark": benchmarks,
        "profile": _artifact(profile, "điểm lĩnh vực PAPI"),
        "availability": {"regions": available_regions, "provinces": available_provinces},
        "insights": {
            "distribution": distribution_insight,
            "ranking": ranking_insight,
            "benchmark": benchmark_insight,
            "profile": profile_insight,
        },
    }, n=len(snapshot), filters={"scale": scale, "year": year, "region": chosen_region, "province": chosen_province}, unit=cfg["unit"],
       caveats=["Benchmark toàn quốc chỉ dùng các tỉnh có dữ liệu của snapshot; profile dùng cùng năm."])


def dimensions_view(scale="eight", year=None, x=None, y=None):
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
    counts = dimensions.correlation_counts(snapshot, dims)
    pair, x_mean, y_mean, corr = dimensions.pair_snapshot(snapshot, x, y)
    regression, slope, intercept, r_squared = dimensions.regression_snapshot(snapshot, x, y)
    summary = dimensions.summaries(snapshot, dims)
    labels = _labels()
    label_rows = _indicator_rows(dims)
    short_labels = {row["code"]: row["short"] for row in label_rows}
    pair_rows = pair.rename(columns={"province_vi": "province_vi", x: "x", y: "y"})
    regression_rows = regression.rename(columns={x: "x", y: "y"})
    valid_residuals = regression_rows.dropna(subset=["residual"])
    largest_residual = "" if valid_residuals.empty else str(
        valid_residuals.loc[valid_residuals.residual.abs().idxmax(), "province_vi"]
    )
    strongest_x, strongest_y, strongest_r = dimensions.strongest_pair(snapshot, dims)
    strongest_direction = "cùng chiều" if strongest_r >= 0 else "ngược chiều"
    correlation_insight = (
        f"{short_labels.get(strongest_x, strongest_x)} và {short_labels.get(strongest_y, strongest_y)} "
        f"liên hệ {strongest_direction} mạnh nhất (r = {_vi_number(strongest_r)}); không phải bằng chứng nhân quả."
    )
    quadrant_counts = pair.quadrant.value_counts()
    largest_quadrant = str(quadrant_counts.index[0]) if not quadrant_counts.empty else "Không đủ dữ liệu"
    largest_quadrant_n = int(quadrant_counts.iloc[0]) if not quadrant_counts.empty else 0
    pair_insight = (
        f"{short_labels[x]} và {short_labels[y]} có r = {_vi_number(corr)}, R² = {_vi_number(r_squared)}; "
        f"{largest_quadrant} đông nhất (n = {largest_quadrant_n}), chỉ là liên hệ quan sát."
    )
    if valid_residuals.empty:
        residual_insight = "Không đủ dữ liệu để xác định tỉnh lệch khỏi xu hướng tuyến tính."
    else:
        residual_row = valid_residuals.loc[valid_residuals.residual.abs().idxmax()]
        residual_direction = "cao hơn" if residual_row.residual >= 0 else "thấp hơn"
        residual_insight = (
            f"{residual_row.province_vi} lệch nhiều nhất: {short_labels[y]} {residual_direction} dự đoán "
            f"{_vi_number(abs(residual_row.residual))} điểm; không tự động là lỗi dữ liệu."
        )
    variable_row = summary.loc[summary.std_score.idxmax()]
    highest_row = summary.loc[summary.mean_score.idxmax()]
    variation_insight = (
        f"{short_labels[variable_row.code]} phân hóa mạnh nhất (SD = {_vi_number(variable_row.std_score)}); "
        f"{short_labels[highest_row.code]} có trung bình cao nhất ({_vi_number(highest_row.mean_score)}), trong snapshot này."
    )
    strengths = [
        [dimensions.correlation_strength(value) for value in row]
        for row in matrix.values.tolist()
    ]
    return response({
        "availability": {"dimensions": dims},
        "correlation": {
            "rowCount": len(dims), "unit": "không đơn vị", "source": SOURCE, "caveats": [],
            "n": len(snapshot), "codes": dims, "matrix": matrix.values.tolist(),
            "counts": counts.values.tolist(), "strengths": strengths,
        },
        "pair": _artifact(pair_rows, "điểm lĩnh vực PAPI", n=len(pair), x=x, y=y, xMean=x_mean, yMean=y_mean, pearsonR=corr),
        "standardDeviation": _artifact(summary, "điểm lĩnh vực PAPI"),
        "regression": _artifact(
            regression_rows, "điểm lĩnh vực PAPI", n=len(regression_rows), x=x, y=y,
            slope=slope, intercept=intercept, rSquared=r_squared,
            strength=dimensions.correlation_strength(corr),
            largestResidualProvince=largest_residual,
            caveats=["Hồi quy chỉ mô tả xu hướng quan sát, không chứng minh quan hệ nhân quả."],
        ),
        "labels": label_rows,
        "insights": {
            "correlation": correlation_insight,
            "pair": pair_insight,
            "residual": residual_insight,
            "variation": variation_insight,
        },
    }, n=len(snapshot), filters={"scale": scale, "year": year, "x": x, "y": y}, unit="điểm lĩnh vực PAPI",
       caveats=["Pearson r là mối liên hệ quan sát, không chứng minh quan hệ nhân quả."])


def dynamics_view(scale="eight", from_year=None, to_year=None, k=None):
    cfg = _scale(scale)
    start, end = _range(cfg, from_year, to_year)
    if k is not None and k not in range(2, 7):
        raise ContractError("Số cụm K phải nằm trong khoảng 2–6 hoặc để tự động.")
    total = cfg["total_col"]
    changes = dynamics.changes(data()["prov_year"], total, start, end)
    clusters = dynamics.cluster_profiles(data()["prov_year"], end, cfg["dims"], 4)
    stable = dynamics.cluster_transitions(data()["prov_year"], start, end, cfg["dims"], requested_k=k)
    if changes.empty or clusters.empty:
        raise ContractError("Không đủ dữ liệu cho so sánh thay đổi hoặc phân nhóm.")
    change_rows = changes.rename(columns={start: "from_score", end: "to_score"})
    centroids = clusters.groupby("cluster", observed=True)[cfg["dims"]].mean().reset_index().sort_values("cluster")
    cluster_sizes = clusters.groupby("cluster", observed=True).size()
    centroids["n"] = centroids.cluster.map(cluster_sizes).astype(int)
    profiles = [{"cluster": cluster, "n": len(group), "provinces": records(group[["province_vi", "region"]].sort_values("province_vi"))}
                for cluster, group in clusters.groupby("cluster", observed=True)]
    assignments = stable["assignments"]
    changed_n = int(assignments.changed.sum())
    retained_n = int(len(assignments) - changed_n)
    retention_pct = float(retained_n / len(assignments))
    farthest = assignments.loc[assignments.pca_distance.idxmax()]
    transition_changes = [row for row in stable["transitions"] if row["from_cluster"] != row["to_cluster"]]
    largest_transition = max(transition_changes, key=lambda row: row["n"], default=None)
    label_rows = _indicator_rows(cfg["dims"])
    short_labels = {row["code"]: row["short"] for row in label_rows}
    profile_insights = []
    for centroid in stable["centroids"]:
        ordered = sorted(centroid["values"], key=lambda item: item["z_score"])
        weak = ", ".join(short_labels.get(item["code"], item["code"]) for item in ordered[:2])
        strong = ", ".join(short_labels.get(item["code"], item["code"]) for item in reversed(ordered[-2:]))
        profile_insights.append({
            "cluster": centroid["cluster"],
            "text": (
                f"Hồ sơ {centroid['cluster']} nổi bật ở {strong}, thấp hơn mặt bằng ở {weak}; "
                f"có {centroid['n_end']} tỉnh tại mốc cuối."
            ),
        })
    strongest_change = change_rows.iloc[0]
    weakest_change = change_rows.iloc[-1]
    strongest_label = "tăng nhiều nhất" if strongest_change.change >= 0 else "giảm ít nhất"
    weakest_label = "giảm nhiều nhất" if weakest_change.change <= 0 else "tăng ít nhất"
    change_insight = (
        f"{strongest_change.province_vi} {strongest_label} ({_vi_number(strongest_change.change)}); "
        f"{weakest_change.province_vi} {weakest_label} ({_vi_number(weakest_change.change)})."
    )
    pca_insight = (
        f"{changed_n}/{len(assignments)} tỉnh đổi hồ sơ; {farthest.province_vi} dịch chuyển xa nhất "
        f"trên mặt phẳng PCA ({_vi_number(farthest.pca_distance)})."
    )
    transition_insight = (
        f"{_vi_number(retention_pct * 100)}% tỉnh giữ hồ sơ; "
        + (
            f"luồng chuyển lớn nhất là {largest_transition['from_cluster']} → {largest_transition['to_cluster']} "
            f"với {largest_transition['n']} tỉnh."
            if largest_transition else "không có luồng đổi hồ sơ trong mẫu này."
        )
    )
    return response({
        "measure": {"id": total, "label": cfg["label"], "unit": cfg["unit"]},
        "changes": _artifact(
            change_rows, "chênh lệch điểm PAPI", n=len(change_rows),
            median=float(change_rows.change.median()),
            top8=records(change_rows.head(8)), bottom8=records(change_rows.tail(8).sort_values("change")),
        ),
        "clusters": {
            "rowCount": len(clusters), "unit": "điểm lĩnh vực PAPI", "source": SOURCE,
            "caveats": ["KMeans chuẩn hoá các lĩnh vực trước khi phân cụm."],
            "n": len(clusters), "count": int(clusters.cluster.nunique()), "randomState": 42,
            "rows": records(clusters), "centroids": records(centroids), "profiles": profiles,
        },
        "clusterModel": {
            "rowCount": len(stable["assignments"]), "unit": "profile lĩnh vực chuẩn hoá",
            "source": SOURCE,
            "caveats": [
                "Chuẩn hoá z-score riêng trong từng năm trước khi pool hai mốc.",
                "Nhãn cụm chỉ ổn định trong truy vấn hiện tại và không phải xếp hạng.",
            ],
            "n": len(stable["assignments"]), "selectedK": stable["selected_k"],
            "selectionMode": stable["selection_mode"], "silhouette": stable["silhouette"],
            "randomState": 42, "candidateScores": stable["candidates"],
            "pcaVariance": stable["pca_variance"],
            "assignments": records(assignments),
            "centroids": stable["centroids"], "transitions": stable["transitions"],
            "changedN": changed_n, "changedPct": float(changed_n / len(assignments)),
            "retainedN": retained_n, "retentionPct": retention_pct,
            "farthestProvince": str(farthest.province_vi),
            "farthestDistance": float(farthest.pca_distance),
        },
        "insights": {
            "change": change_insight, "profiles": profile_insights,
            "pca": pca_insight, "transition": transition_insight,
        },
    }, n=len(changes), filters={"scale": scale, "from": start, "to": end, "k": "auto" if k is None else k}, unit=cfg["unit"],
       caveats=["KMeans chuẩn hoá các lĩnh vực và dùng random_state=42; cụm không phải xếp hạng.", "Chỉ tỉnh đủ dữ liệu ở cả hai mốc mới có delta."])
