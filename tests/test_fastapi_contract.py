"""Matrix contract/numeric tests cho FastAPI local Phase 1."""
import itertools
import json
import math

import numpy as np
import pytest
from fastapi.testclient import TestClient

from server import services
from server.main import create_app
from server.view_models import json_safe
from src.analysis import dimensions, dynamics, provincial, trend


SCALE_YEARS = {key: services._years(cfg) for key, cfg in services.SCALES.items()}


@pytest.fixture(scope="module")
def client():
    return TestClient(create_app())


def _assert_json_safe(value):
    if isinstance(value, float):
        assert math.isfinite(value)
    elif isinstance(value, dict):
        for item in value.values():
            _assert_json_safe(item)
    elif isinstance(value, list):
        for item in value:
            _assert_json_safe(item)


def _artifact(payload):
    assert payload["rowCount"] >= 0
    assert payload["unit"]
    assert payload["source"]
    assert isinstance(payload["caveats"], list)


def test_openapi_uses_concrete_response_models_not_generic_free_form_data(client):
    openapi = client.get("/openapi.json").json()
    expected = {
        "/api/v1/metadata": "MetadataResponse", "/api/v1/geojson": "GeojsonResponse",
        "/api/v1/overview": "OverviewResponse", "/api/v1/trends": "TrendsResponse",
        "/api/v1/provinces": "ProvincesResponse", "/api/v1/dimensions": "DimensionsResponse",
        "/api/v1/dynamics": "DynamicsResponse",
    }
    for path, model in expected.items():
        schema = openapi["paths"][path]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
        assert schema["$ref"].endswith(f"/{model}")
    schemas = openapi["components"]["schemas"]
    assert "DashboardResponse" not in schemas
    assert schemas["OverviewData"]["properties"]["map"]["$ref"].endswith("/OverviewMapArtifact")
    assert schemas["OverviewStoryCards"]["properties"]["annualChanges"]["$ref"].endswith("/AnnualChangeArtifact")
    assert schemas["OverviewStoryCards"]["properties"]["quadrants"]["$ref"].endswith("/QuadrantSummaryArtifact")
    assert schemas["OverviewStoryCards"]["properties"]["changeDistribution"]["$ref"].endswith("/ChangeDistributionArtifact")
    assert schemas["TrendsData"]["properties"]["covid"]["$ref"].endswith("/CovidArtifact")
    assert schemas["TrendsData"]["properties"]["regionalRanks"]["$ref"].endswith("/RegionalRankArtifact")
    assert schemas["DynamicsData"]["properties"]["clusters"]["$ref"].endswith("/ClusterArtifact")
    assert schemas["DynamicsData"]["properties"]["clusterModel"]["$ref"].endswith("/StableClusterArtifact")


@pytest.mark.parametrize("scale,year", [(scale, year) for scale, years in SCALE_YEARS.items() for year in years])
def test_all_available_years_work_for_snapshot_routes_and_have_actual_n(client, scale, year):
    overview = client.get(f"/api/v1/overview?scale={scale}&year={year}")
    provinces = client.get(f"/api/v1/provinces?scale={scale}&year={year}")
    dimensions_response = client.get(f"/api/v1/dimensions?scale={scale}&year={year}")
    for response in (overview, provinces, dimensions_response):
        assert response.status_code == 200
        payload = response.json()
        assert payload["meta"]["n"] > 0
        assert payload["meta"]["filters"]["year"] == year


@pytest.mark.parametrize("scale,start,end", [
    ("six", 2011, 2012), ("six", 2011, 2024), ("six", 2023, 2024),
    ("eight", 2018, 2019), ("eight", 2018, 2024), ("eight", 2023, 2024),
])
def test_representative_valid_ranges_work_for_trends_and_dynamics(client, scale, start, end):
    for endpoint in ("trends", "dynamics"):
        response = client.get(f"/api/v1/{endpoint}?scale={scale}&from={start}&to={end}")
        assert response.status_code == 200
        expected = {"scale": scale, "from": start, "to": end}
        expected.update({"region": None, "province": None} if endpoint == "trends" else {"k": "auto"})
        assert response.json()["meta"]["filters"] == expected


def test_every_valid_range_is_accepted_by_the_service_contract():
    for scale, years in SCALE_YEARS.items():
        for start, end in itertools.combinations(years, 2):
            assert services.trends(scale, start, end)["meta"]["filters"] == {
                "scale": scale, "from": start, "to": end, "region": None, "province": None,
            }


def test_semantic_artifacts_contributors_and_bool_are_typed(client):
    payload = client.get("/api/v1/trends?scale=eight&from=2018&to=2024").json()
    assert payload["meta"]["n"] == 430  # valid province-year total observations, not seven annual rows
    for key in (
        "totalSeries", "dimensionSeries", "dimensionDeltas", "covid", "heatmap",
        "regionalSeries", "regionalYearOverYear", "regionalRanks", "selectedSeries", "turningPoints",
    ):
        _artifact(payload["data"][key])
    assert payload["data"]["totalSeries"]["rowCount"] == 7
    assert set(payload["data"]["insights"]) == {"total", "regionalYearOverYear", "regionalRank", "dimensions"}
    assert all(1 <= row["rank"] <= 6 for row in payload["data"]["regionalRanks"]["rows"])
    assert all(point["contributorN"] > 0 for point in payload["data"]["totalSeries"]["rows"])
    assert isinstance(payload["data"]["covid"]["available"], bool)
    assert payload["data"]["covid"]["available"] is True


def test_overview_trends_and_geojson_numeric_parity(client):
    d = services.data()
    overview = client.get("/api/v1/overview?scale=six&year=2024").json()
    snapshot = provincial.snapshot_for_year(d["prov_year"], 2024, "total_papi_6dim")
    assert overview["meta"]["n"] == len(snapshot)
    assert overview["data"]["metrics"]["mean"] == pytest.approx(snapshot.total_papi_6dim.mean(), abs=1e-9)
    assert overview["data"]["ranking"]["rowCount"] == len(snapshot)
    assert overview["data"]["storyCards"]["trend"]["rowCount"] == 14
    assert overview["data"]["storyCards"]["regions"]["rowCount"] == 6
    assert overview["data"]["storyCards"]["strongestPair"]["pearsonR"] is not None
    assert overview["data"]["map"]["rows"][0]["rank"] == 1
    annual = overview["data"]["storyCards"]["annualChanges"]
    assert annual["rows"][0]["baseline"] is True
    assert annual["rows"][1]["change"] == pytest.approx(
        annual["rows"][1]["score"] - annual["rows"][0]["score"], abs=1e-9
    )
    quadrants = overview["data"]["storyCards"]["quadrants"]
    assert sum(row["n"] for row in quadrants["rows"]) == quadrants["n"]
    assert sum(row["percentage"] for row in quadrants["rows"]) == pytest.approx(100, abs=1e-9)
    distribution = overview["data"]["storyCards"]["changeDistribution"]
    assert sum(row["count"] for row in distribution["bins"]) == distribution["n"]
    assert distribution["positiveN"] + distribution["negativeN"] + distribution["unchangedN"] == distribution["n"]
    assert set(overview["data"]["insights"]) == {"map", "annualChange", "quadrants", "changeDistribution"}

    api_trends = client.get("/api/v1/trends?scale=eight&from=2018&to=2024").json()
    reference = trend.total_by_year(d["prov_year"], "total_papi", 2018, 2024)
    assert api_trends["data"]["totalSeries"]["rows"][-1]["score"] == pytest.approx(reference.iloc[-1].total_papi, abs=1e-9)
    geojson = client.get("/api/v1/geojson").json()["data"]["geojson"]["features"]
    assert len(geojson) == client.get("/api/v1/geojson").json()["meta"]["n"]


def test_h2_benchmark_and_profile_parity_and_province_only_filter(client):
    d = services.data()
    default = client.get("/api/v1/provinces?scale=six&year=2024").json()
    province = default["meta"]["filters"]["province"]
    province_only = client.get(f"/api/v1/provinces?scale=six&year=2024&province={province}").json()
    region = province_only["meta"]["filters"]["region"]
    assert province_only["meta"]["filters"]["province"] == province
    region_only = client.get(f"/api/v1/provinces?scale=six&year=2024&region={region}").json()
    assert region_only["meta"]["filters"]["region"] == region
    assert region_only["meta"]["filters"]["province"] in region_only["data"]["availability"]["provinces"]
    snapshot = provincial.snapshot_for_year(d["prov_year"], 2024, "total_papi_6dim")
    reference = provincial.province_benchmarks(snapshot, region, province, "total_papi_6dim")
    assert province_only["data"]["benchmark"]["vsRegion"] == pytest.approx(reference["vs_region"], abs=1e-9)
    assert province_only["data"]["benchmark"]["unit"] == "điểm tổng 6 lĩnh vực"
    profile = provincial.dimension_benchmarks(d["prov_year"], 2024, region, province, services.SCALES["six"]["dims"])
    assert province_only["data"]["profile"]["rows"][0]["nationalMean"] == pytest.approx(profile.iloc[0].national_mean, abs=1e-9)
    assert all(row["regionN"] > 0 and row["nationalN"] > 0 for row in province_only["data"]["profile"]["rows"])
    assert province_only["data"]["benchmark"]["rankRegion"] >= 1
    assert province_only["data"]["benchmark"]["regionTotal"] == len(region_only["data"]["ranking"]["rows"])
    _artifact(province_only["data"]["distribution"])
    _artifact(province_only["data"]["regionMeans"])
    _artifact(province_only["data"]["ranking"])


def test_h3_matrix_quadrant_std_parity_and_partial_dimension_filters(client):
    d = services.data()
    x_only = client.get("/api/v1/dimensions?scale=eight&year=2024&x=D1")
    y_only = client.get("/api/v1/dimensions?scale=eight&year=2024&y=D2")
    assert x_only.status_code == y_only.status_code == 200
    assert x_only.json()["meta"]["filters"]["x"] != x_only.json()["meta"]["filters"]["y"]
    assert y_only.json()["meta"]["filters"]["x"] != y_only.json()["meta"]["filters"]["y"]
    payload = client.get("/api/v1/dimensions?scale=eight&year=2024&x=D1&y=D2").json()
    snap = dimensions.snapshot_for_year(d["prov_year"], 2024, services.SCALES["eight"]["dims"])
    matrix = dimensions.correlation_matrix(snap, services.SCALES["eight"]["dims"])
    pair, _, _, _ = dimensions.pair_snapshot(snap, "D1", "D2")
    std = dimensions.summaries(snap, services.SCALES["eight"]["dims"])
    assert payload["data"]["correlation"]["unit"] == "không đơn vị"
    assert payload["data"]["correlation"]["matrix"][0][1] == pytest.approx(matrix.iloc[0, 1], abs=1e-9)
    assert payload["data"]["pair"]["rows"][0]["quadrant"] == pair.iloc[0].quadrant
    assert payload["data"]["standardDeviation"]["rows"][0]["stdScore"] == pytest.approx(std.iloc[0].std_score, abs=1e-9)
    regression, slope, intercept, r_squared = dimensions.regression_snapshot(snap, "D1", "D2")
    assert payload["data"]["regression"]["slope"] == pytest.approx(slope, abs=1e-9)
    assert payload["data"]["regression"]["intercept"] == pytest.approx(intercept, abs=1e-9)
    assert payload["data"]["regression"]["rSquared"] == pytest.approx(r_squared, abs=1e-9)
    assert payload["data"]["regression"]["rowCount"] == len(regression)


def test_h4_delta_centroid_profile_parity_and_no_dynamic_year_keys(client):
    d = services.data()
    payload = client.get("/api/v1/dynamics?scale=six&from=2011&to=2024").json()
    reference_changes = dynamics.changes(d["prov_year"], "total_papi_6dim", 2011, 2024)
    reference_clusters = dynamics.cluster_profiles(d["prov_year"], 2024, services.SCALES["six"]["dims"], 4)
    assert payload["data"]["changes"]["rows"][0]["change"] == pytest.approx(reference_changes.iloc[0].change, abs=1e-9)
    assert {"fromScore", "toScore"} <= set(payload["data"]["changes"]["rows"][0])
    assert "2011" not in payload["data"]["changes"]["rows"][0] and "2024" not in payload["data"]["changes"]["rows"][0]
    centroid = reference_clusters.groupby("cluster", observed=True)[services.SCALES["six"]["dims"]].mean().reset_index().sort_values("cluster")
    assert payload["data"]["clusters"]["centroids"][0]["D1"] == pytest.approx(centroid.iloc[0].D1, abs=1e-9)
    assert payload["data"]["clusters"]["centroids"][0]["n"] == int((reference_clusters.cluster == centroid.iloc[0].cluster).sum())
    assert sum(profile["n"] for profile in payload["data"]["clusters"]["profiles"]) == len(reference_clusters)
    assert payload["data"]["clusters"]["randomState"] == 42
    stable = payload["data"]["clusterModel"]
    assert stable["selectionMode"] == "auto"
    assert 2 <= stable["selectedK"] <= 6
    assert sum(item["n"] for item in stable["transitions"]) == stable["n"]
    assert len(stable["pcaVariance"]) == 2


def test_focus_series_manual_k_and_product_defaults(client):
    default_overview = client.get("/api/v1/overview").json()
    default_provinces = client.get("/api/v1/provinces").json()
    default_dimensions = client.get("/api/v1/dimensions").json()
    assert default_overview["meta"]["filters"] == {"scale": "eight", "year": 2024}
    assert default_provinces["meta"]["filters"]["scale"] == "eight"
    assert default_dimensions["meta"]["filters"]["scale"] == "eight"
    focused = client.get(
        "/api/v1/trends?scale=eight&from=2018&to=2024&province=Quảng%20Ninh"
    ).json()
    assert focused["meta"]["filters"]["region"] == "Đồng bằng sông Hồng"
    assert {row["scope"] for row in focused["data"]["selectedSeries"]["rows"]} == {"region", "province"}
    manual = client.get("/api/v1/dynamics?scale=eight&from=2018&to=2024&k=3").json()
    assert manual["meta"]["filters"]["k"] == 3
    assert manual["data"]["clusterModel"]["selectedK"] == 3
    assert manual["data"]["clusterModel"]["selectionMode"] == "manual"


def test_partial_range_filters_resolve_deterministically(client):
    for endpoint in ("trends", "dynamics"):
        from_only = client.get(f"/api/v1/{endpoint}?scale=eight&from=2020").json()
        to_only = client.get(f"/api/v1/{endpoint}?scale=eight&to=2022").json()
        extra = {"region": None, "province": None} if endpoint == "trends" else {"k": "auto"}
        assert from_only["meta"]["filters"] == {"scale": "eight", "from": 2020, "to": 2024, **extra}
        assert to_only["meta"]["filters"] == {"scale": "eight", "from": 2018, "to": 2022, **extra}


@pytest.mark.parametrize("path", [
    "/api/v1/overview?scale=nine", "/api/v1/trends?scale=six&from=2024&to=2011",
    "/api/v1/dimensions?scale=six&year=2024&x=D1&y=D1",
    "/api/v1/dimensions?scale=six&year=2024&x=D8&y=D1",
    "/api/v1/provinces?scale=six&year=1999",
    "/api/v1/provinces?scale=six&year=2024&region=Tây%20Nguyên&province=Quảng%20Ninh",
    "/api/v1/trends?scale=eight&from=2018&to=2024&region=Tây%20Nguyên&province=Quảng%20Ninh",
    "/api/v1/dynamics?scale=eight&from=2018&to=2024&k=7",
])
def test_invalid_filter_combinations_return_vietnamese_422(client, path):
    response = client.get(path)
    assert response.status_code == 422
    assert response.json()["detail"]


def test_cors_allowlist_and_strict_json_null_normalization(client):
    allowed = client.get("/health", headers={"Origin": "http://localhost:5173"})
    denied = client.get("/health", headers={"Origin": "https://example.org"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-origin" not in denied.headers
    for path in [
        "/api/v1/metadata", "/api/v1/geojson", "/api/v1/overview?scale=eight&year=2024",
        "/api/v1/trends?scale=six&from=2011&to=2024", "/api/v1/provinces?scale=six&year=2024",
        "/api/v1/dimensions?scale=eight&year=2024&x=D1&y=D2", "/api/v1/dynamics?scale=eight&from=2018&to=2024",
    ]:
        payload = client.get(path).json()
        json.dumps(payload, allow_nan=False)
        _assert_json_safe(payload)
    assert json_safe({"numpyBool": np.bool_(True), "nan": float("nan"), "inf": float("inf")}) == {
        "numpyBool": True, "nan": None, "inf": None,
    }
