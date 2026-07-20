"""Schema OpenAPI cụ thể cho từng view-model dashboard Phase 1."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ApiModel(BaseModel):
    model_config = {"populate_by_name": True}


class EmptyFilters(ApiModel):
    pass


class ScaleYearFilters(ApiModel):
    scale: Literal["six", "eight"]
    year: int


class RangeFilters(ApiModel):
    scale: Literal["six", "eight"]
    from_year: int = Field(alias="from")
    to: int


class ProvinceFilters(ScaleYearFilters):
    region: str
    province: str


class DimensionFilters(ScaleYearFilters):
    x: str
    y: str


class ResponseMeta(ApiModel):
    schema_version: Literal["v1"] = Field(alias="schemaVersion")
    source: str
    unit: str
    n: int = Field(ge=0, description="Số quan sát hợp lệ của input chính, không phải số hàng hiển thị")
    caveats: list[str] = Field(default_factory=list)


class MetadataMeta(ResponseMeta):
    filters: EmptyFilters


class OverviewMeta(ResponseMeta):
    filters: ScaleYearFilters


class TrendsMeta(ResponseMeta):
    filters: RangeFilters


class ProvincesMeta(ResponseMeta):
    filters: ProvinceFilters


class DimensionsMeta(ResponseMeta):
    filters: DimensionFilters


class DynamicsMeta(ResponseMeta):
    filters: RangeFilters


class Artifact(ApiModel):
    row_count: int = Field(alias="rowCount", ge=0)
    unit: str
    source: str
    caveats: list[str] = Field(default_factory=list)


class Measure(ApiModel):
    id: str
    label: str
    unit: str


class Indicator(ApiModel):
    code: str
    name_vi: str = Field(alias="nameVi")
    name_en: str = Field(alias="nameEn")
    short: str
    color: str
    sort: int
    from_year: int = Field(alias="fromYear")


class Province(ApiModel):
    province_id: int = Field(alias="provinceId")
    province_vi: str = Field(alias="provinceVi")
    province_en: str = Field(alias="provinceEn")
    region: str
    region_id: int = Field(alias="regionId")


class ScaleAvailability(ApiModel):
    id: Literal["six", "eight"]
    label: str
    years: list[int]
    dimensions: list[str]
    total_column: str = Field(alias="totalColumn")


class MetadataData(ApiModel):
    scales: list[ScaleAvailability]
    dimensions: list[Indicator]
    regions: list[str]
    provinces: list[Province]


class MetadataResponse(ApiModel):
    meta: MetadataMeta
    data: MetadataData


Coordinates = list[list[list[float]]] | list[list[list[list[float]]]]


class GeoProperties(ApiModel):
    province_id: int = Field(alias="province_id")
    province_vi: str = Field(alias="province_vi")
    shape_name: str = Field(alias="shapeName")


class GeoGeometry(ApiModel):
    type: Literal["Polygon", "MultiPolygon"]
    coordinates: Coordinates


class GeoFeature(ApiModel):
    type: Literal["Feature"]
    properties: GeoProperties
    geometry: GeoGeometry


class FeatureCollection(ApiModel):
    type: Literal["FeatureCollection"]
    features: list[GeoFeature]


class GeojsonData(ApiModel):
    geojson: FeatureCollection


class GeojsonResponse(ApiModel):
    meta: MetadataMeta
    data: GeojsonData


class ScoreRow(ApiModel):
    province_id: int = Field(alias="provinceId")
    province_vi: str = Field(alias="provinceVi")
    region: str
    score: float | None


class RankingRow(ScoreRow):
    rank: int


class OverviewMetrics(ApiModel):
    mean: float | None
    min: float | None
    max: float | None
    leader: str
    last: str
    gap: float | None


class ScoreRowsArtifact(Artifact):
    rows: list[ScoreRow]


class RankingArtifact(Artifact):
    rows: list[RankingRow]
    top10: list[RankingRow]
    bottom10: list[RankingRow]


class RegionalRankingRow(ScoreRow):
    rank_region: int = Field(alias="rankRegion")


class OverviewData(ApiModel):
    measure: Measure
    metrics: OverviewMetrics
    map: ScoreRowsArtifact
    ranking: RankingArtifact


class OverviewResponse(ApiModel):
    meta: OverviewMeta
    data: OverviewData


class TotalSummary(ApiModel):
    first: int | None
    latest: int | None
    v_first: float | None = Field(alias="vFirst")
    v_latest: float | None = Field(alias="vLatest")
    net: float | None
    peak_year: int | None = Field(alias="peakYear")
    peak_val: float | None = Field(alias="peakValue")
    dip_val: float | None = Field(alias="dipValue")


class TotalPoint(ApiModel):
    year: int
    score: float | None
    contributor_n: int = Field(alias="contributorN", ge=0)


class DimensionPoint(ApiModel):
    year: int
    code: str
    label: str
    score: float | None
    contributor_n: int = Field(alias="contributorN", ge=0)


class DeltaPoint(ApiModel):
    code: str
    label: str
    delta: float | None
    from_score: float | None = Field(alias="fromScore")
    to_score: float | None = Field(alias="toScore")
    contributor_n_from: int = Field(alias="contributorNFrom", ge=0)
    contributor_n_to: int = Field(alias="contributorNTo", ge=0)


class CovidComparison(ApiModel):
    code: str
    label: str
    before_score: float | None = Field(alias="beforeScore")
    after_score: float | None = Field(alias="afterScore")
    change: float | None
    contributor_n_before: int = Field(alias="contributorNBefore", ge=0)
    contributor_n_after: int = Field(alias="contributorNAfter", ge=0)


class TotalSeriesArtifact(Artifact):
    rows: list[TotalPoint]


class DimensionSeriesArtifact(Artifact):
    rows: list[DimensionPoint]


class DeltaArtifact(Artifact):
    rows: list[DeltaPoint]


class CovidArtifact(Artifact):
    available: bool
    rows: list[CovidComparison]


class TrendsData(ApiModel):
    measure: Measure
    summary: TotalSummary
    total_series: TotalSeriesArtifact = Field(alias="totalSeries")
    dimension_series: DimensionSeriesArtifact = Field(alias="dimensionSeries")
    dimension_deltas: DeltaArtifact = Field(alias="dimensionDeltas")
    covid: CovidArtifact
    heatmap: DimensionSeriesArtifact


class TrendsResponse(ApiModel):
    meta: TrendsMeta
    data: TrendsData


class DistributionRow(ScoreRow):
    year: int


class RegionMeanRow(ApiModel):
    region: str
    mean_score: float | None = Field(alias="meanScore")
    median_score: float | None = Field(alias="medianScore")
    min_score: float | None = Field(alias="minScore")
    max_score: float | None = Field(alias="maxScore")
    n: int
    spread: float | None


class Benchmark(ApiModel):
    unit: str
    source: str
    caveats: list[str] = Field(default_factory=list)
    province_score: float | None = Field(alias="provinceScore")
    region_mean: float | None = Field(alias="regionMean")
    national_mean: float | None = Field(alias="nationalMean")
    vs_region: float | None = Field(alias="vsRegion")
    vs_national: float | None = Field(alias="vsNational")
    region_n: int = Field(alias="regionN")
    national_n: int = Field(alias="nationalN")


class ProfileRow(ApiModel):
    code: str
    province_score: float | None = Field(alias="provinceScore")
    region_mean: float | None = Field(alias="regionMean")
    national_mean: float | None = Field(alias="nationalMean")
    region_n: int = Field(alias="regionN")
    national_n: int = Field(alias="nationalN")


class DistributionArtifact(Artifact):
    rows: list[DistributionRow]


class RegionMeanArtifact(Artifact):
    rows: list[RegionMeanRow]


class RankingRowsArtifact(Artifact):
    rows: list[RegionalRankingRow]


class ProfileArtifact(Artifact):
    rows: list[ProfileRow]


class ProvinceAvailability(ApiModel):
    regions: list[str]
    provinces: list[str]


class ProvincesData(ApiModel):
    measure: Measure
    distribution: DistributionArtifact
    region_means: RegionMeanArtifact = Field(alias="regionMeans")
    ranking: RankingRowsArtifact
    benchmark: Benchmark
    profile: ProfileArtifact
    availability: ProvinceAvailability


class ProvincesResponse(ApiModel):
    meta: ProvincesMeta
    data: ProvincesData


class CorrelationArtifact(Artifact):
    n: int
    codes: list[str]
    matrix: list[list[float | None]]


class PairRow(ApiModel):
    province_vi: str = Field(alias="provinceVi")
    region: str
    x: float | None
    y: float | None
    quadrant: Literal["Cao–cao", "Thấp–thấp", "Cao–thấp", "Thấp–cao"]


class PairArtifact(Artifact):
    n: int
    x: str
    y: str
    x_mean: float | None = Field(alias="xMean")
    y_mean: float | None = Field(alias="yMean")
    pearson_r: float | None = Field(alias="pearsonR")
    rows: list[PairRow]


class StdRow(ApiModel):
    code: str
    mean_score: float | None = Field(alias="meanScore")
    std_score: float | None = Field(alias="stdScore")
    n: int


class StdArtifact(Artifact):
    rows: list[StdRow]


class DimensionAvailability(ApiModel):
    dimensions: list[str]


class DimensionsData(ApiModel):
    availability: DimensionAvailability
    correlation: CorrelationArtifact
    pair: PairArtifact
    standard_deviation: StdArtifact = Field(alias="standardDeviation")
    labels: list[Indicator]


class DimensionsResponse(ApiModel):
    meta: DimensionsMeta
    data: DimensionsData


class ChangeRow(ApiModel):
    province_vi: str = Field(alias="provinceVi")
    region: str
    from_score: float | None = Field(alias="fromScore")
    to_score: float | None = Field(alias="toScore")
    change: float | None


class ChangesArtifact(Artifact):
    n: int
    rows: list[ChangeRow]
    top8: list[ChangeRow]
    bottom8: list[ChangeRow]


class ClusterRow(ApiModel):
    province_vi: str = Field(alias="provinceVi")
    region: str
    cluster: str
    d1: float | None = Field(alias="D1", default=None)
    d2: float | None = Field(alias="D2", default=None)
    d3: float | None = Field(alias="D3", default=None)
    d4: float | None = Field(alias="D4", default=None)
    d5: float | None = Field(alias="D5", default=None)
    d6: float | None = Field(alias="D6", default=None)
    d7: float | None = Field(alias="D7", default=None)
    d8: float | None = Field(alias="D8", default=None)


class CentroidRow(ApiModel):
    cluster: str
    n: int
    d1: float | None = Field(alias="D1", default=None)
    d2: float | None = Field(alias="D2", default=None)
    d3: float | None = Field(alias="D3", default=None)
    d4: float | None = Field(alias="D4", default=None)
    d5: float | None = Field(alias="D5", default=None)
    d6: float | None = Field(alias="D6", default=None)
    d7: float | None = Field(alias="D7", default=None)
    d8: float | None = Field(alias="D8", default=None)


class ClusterProvince(ApiModel):
    province_vi: str = Field(alias="provinceVi")
    region: str


class ClusterProfile(ApiModel):
    cluster: str
    n: int
    provinces: list[ClusterProvince]


class ClusterArtifact(Artifact):
    n: int
    count: int
    random_state: Literal[42] = Field(alias="randomState")
    rows: list[ClusterRow]
    centroids: list[CentroidRow]
    profiles: list[ClusterProfile]


class DynamicsData(ApiModel):
    measure: Measure
    changes: ChangesArtifact
    clusters: ClusterArtifact


class DynamicsResponse(ApiModel):
    meta: DynamicsMeta
    data: DynamicsData


class ErrorResponse(ApiModel):
    detail: str
    fields: dict[str, str] | None = None
