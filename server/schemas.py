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


class TrendFilters(RangeFilters):
    region: str | None = None
    province: str | None = None


class DynamicsFilters(RangeFilters):
    k: int | Literal["auto"]


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
    filters: TrendFilters


class ProvincesMeta(ResponseMeta):
    filters: ProvinceFilters


class DimensionsMeta(ResponseMeta):
    filters: DimensionFilters


class DynamicsMeta(ResponseMeta):
    filters: DynamicsFilters


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


class OverviewMapRow(ScoreRow):
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


class OverviewMapArtifact(Artifact):
    rows: list[OverviewMapRow]


class RankingArtifact(Artifact):
    rows: list[RankingRow]
    top10: list[RankingRow]
    bottom10: list[RankingRow]


class RegionalRankingRow(ScoreRow):
    rank_region: int = Field(alias="rankRegion")


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


class AnnualChangeRow(ApiModel):
    year: int
    score: float | None
    previous_score: float | None = Field(alias="previousScore")
    change: float | None
    contributor_n: int = Field(alias="contributorN", ge=0)
    previous_contributor_n: int = Field(alias="previousContributorN", ge=0)
    baseline: bool


class AnnualChangeArtifact(Artifact):
    rows: list[AnnualChangeRow]
    largest_increase_year: int | None = Field(alias="largestIncreaseYear")
    largest_increase: float | None = Field(alias="largestIncrease")
    largest_decrease_year: int | None = Field(alias="largestDecreaseYear")
    largest_decrease: float | None = Field(alias="largestDecrease")


class DimensionSeriesArtifact(Artifact):
    rows: list[DimensionPoint]


class DeltaArtifact(Artifact):
    rows: list[DeltaPoint]


class CovidArtifact(Artifact):
    available: bool
    rows: list[CovidComparison]


class RegionalPoint(ApiModel):
    year: int
    region: str
    score: float | None
    contributor_n: int = Field(alias="contributorN", ge=0)


class RegionalSeriesArtifact(Artifact):
    rows: list[RegionalPoint]


class RegionalYearOverYearPoint(RegionalPoint):
    previous_score: float | None = Field(alias="previousScore")
    change: float | None


class RegionalYearOverYearArtifact(Artifact):
    rows: list[RegionalYearOverYearPoint]


class RegionalRankPoint(RegionalPoint):
    rank: int


class RegionalRankArtifact(Artifact):
    rows: list[RegionalRankPoint]


class TrendInsights(ApiModel):
    total: str
    regional_year_over_year: str = Field(alias="regionalYearOverYear")
    regional_rank: str = Field(alias="regionalRank")
    dimensions: str


class FocusPoint(ApiModel):
    year: int
    scope: Literal["region", "province"]
    label: str
    score: float | None
    contributor_n: int = Field(alias="contributorN", ge=0)


class FocusSeriesArtifact(Artifact):
    rows: list[FocusPoint]


class TurningPoint(ApiModel):
    year: int
    from_year: int = Field(alias="fromYear")
    score: float | None
    previous_score: float | None = Field(alias="previousScore")
    change: float | None


class TurningPointArtifact(Artifact):
    rows: list[TurningPoint]


class TrendsData(ApiModel):
    measure: Measure
    summary: TotalSummary
    total_series: TotalSeriesArtifact = Field(alias="totalSeries")
    dimension_series: DimensionSeriesArtifact = Field(alias="dimensionSeries")
    dimension_deltas: DeltaArtifact = Field(alias="dimensionDeltas")
    covid: CovidArtifact
    heatmap: DimensionSeriesArtifact
    regional_series: RegionalSeriesArtifact = Field(alias="regionalSeries")
    regional_year_over_year: RegionalYearOverYearArtifact = Field(alias="regionalYearOverYear")
    regional_ranks: RegionalRankArtifact = Field(alias="regionalRanks")
    selected_series: FocusSeriesArtifact = Field(alias="selectedSeries")
    turning_points: TurningPointArtifact = Field(alias="turningPoints")
    insights: TrendInsights


class TrendsResponse(ApiModel):
    meta: TrendsMeta
    data: TrendsData


class DistributionRow(ScoreRow):
    year: int
    rank: int = Field(ge=1)


class RegionMeanRow(ApiModel):
    region: str
    mean_score: float | None = Field(alias="meanScore")
    median_score: float | None = Field(alias="medianScore")
    q1: float | None
    q3: float | None
    iqr: float | None
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
    national_min: float | None = Field(alias="nationalMin")
    national_max: float | None = Field(alias="nationalMax")
    national_q1: float | None = Field(alias="nationalQ1")
    national_q3: float | None = Field(alias="nationalQ3")
    vs_region: float | None = Field(alias="vsRegion")
    vs_national: float | None = Field(alias="vsNational")
    region_n: int = Field(alias="regionN")
    national_n: int = Field(alias="nationalN")
    rank_region: int = Field(alias="rankRegion", ge=1)
    region_total: int = Field(alias="regionTotal", ge=1)


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


class ProvinceInsights(ApiModel):
    distribution: str
    ranking: str
    benchmark: str
    profile: str


class ProvincesData(ApiModel):
    measure: Measure
    distribution: DistributionArtifact
    region_means: RegionMeanArtifact = Field(alias="regionMeans")
    ranking: RankingRowsArtifact
    benchmark: Benchmark
    profile: ProfileArtifact
    availability: ProvinceAvailability
    insights: ProvinceInsights


class ProvincesResponse(ApiModel):
    meta: ProvincesMeta
    data: ProvincesData


class CorrelationArtifact(Artifact):
    n: int
    codes: list[str]
    matrix: list[list[float | None]]
    counts: list[list[int]]
    strengths: list[list[str]]


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
    min_score: float | None = Field(alias="minScore")
    max_score: float | None = Field(alias="maxScore")
    n: int


class StdArtifact(Artifact):
    rows: list[StdRow]


class RegressionRow(ApiModel):
    province_vi: str = Field(alias="provinceVi")
    region: str
    x: float | None
    y: float | None
    predicted: float | None
    residual: float | None


class RegressionArtifact(Artifact):
    n: int
    x: str
    y: str
    slope: float | None
    intercept: float | None
    r_squared: float | None = Field(alias="rSquared")
    strength: str
    largest_residual_province: str = Field(alias="largestResidualProvince")
    rows: list[RegressionRow]


class DimensionAvailability(ApiModel):
    dimensions: list[str]


class DimensionInsights(ApiModel):
    correlation: str
    pair: str
    residual: str
    variation: str


class DimensionsData(ApiModel):
    availability: DimensionAvailability
    correlation: CorrelationArtifact
    pair: PairArtifact
    standard_deviation: StdArtifact = Field(alias="standardDeviation")
    regression: RegressionArtifact
    labels: list[Indicator]
    insights: DimensionInsights


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
    median: float | None
    rows: list[ChangeRow]
    top8: list[ChangeRow]
    bottom8: list[ChangeRow]


class QuadrantSummaryRow(ApiModel):
    label: str
    n: int = Field(ge=0)
    percentage: float = Field(ge=0, le=100)
    provinces: list[str]


class QuadrantSummaryArtifact(Artifact):
    n: int = Field(ge=0)
    x: str
    y: str
    pearson_r: float | None = Field(alias="pearsonR")
    rows: list[QuadrantSummaryRow]


class HistogramBin(ApiModel):
    lower: float
    upper: float
    center: float
    count: int = Field(ge=0)
    percentage: float = Field(ge=0, le=100)
    provinces: list[str]


class ChangeDistributionArtifact(Artifact):
    n: int = Field(ge=0)
    from_year: int = Field(alias="fromYear")
    to_year: int = Field(alias="toYear")
    median: float | None
    positive_n: int = Field(alias="positiveN", ge=0)
    negative_n: int = Field(alias="negativeN", ge=0)
    unchanged_n: int = Field(alias="unchangedN", ge=0)
    positive_percentage: float = Field(alias="positivePercentage", ge=0, le=100)
    bins: list[HistogramBin]
    rows: list[ChangeRow]


class OverviewInsights(ApiModel):
    map: str
    annual_change: str = Field(alias="annualChange")
    quadrants: str
    change_distribution: str = Field(alias="changeDistribution")


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


class ClusterCandidate(ApiModel):
    k: int = Field(ge=2, le=6)
    silhouette: float | None


class ClusterAssignment(ApiModel):
    province_vi: str = Field(alias="provinceVi")
    region: str
    start_cluster: str = Field(alias="startCluster")
    end_cluster: str = Field(alias="endCluster")
    changed: bool
    start_pc1: float | None = Field(alias="startPc1")
    start_pc2: float | None = Field(alias="startPc2")
    end_pc1: float | None = Field(alias="endPc1")
    end_pc2: float | None = Field(alias="endPc2")


class ClusterCentroidValue(ApiModel):
    code: str
    z_score: float | None = Field(alias="zScore")
    raw_score: float | None = Field(alias="rawScore")


class StableClusterCentroid(ApiModel):
    cluster: str
    n_start: int = Field(alias="nStart", ge=0)
    n_end: int = Field(alias="nEnd", ge=0)
    descriptor: str
    values: list[ClusterCentroidValue]


class ClusterTransition(ApiModel):
    from_cluster: str = Field(alias="fromCluster")
    to_cluster: str = Field(alias="toCluster")
    n: int = Field(ge=1)
    provinces: list[str]


class StableClusterArtifact(Artifact):
    n: int
    selected_k: int = Field(alias="selectedK", ge=2, le=6)
    selection_mode: Literal["auto", "manual"] = Field(alias="selectionMode")
    silhouette: float | None
    random_state: Literal[42] = Field(alias="randomState")
    candidate_scores: list[ClusterCandidate] = Field(alias="candidateScores")
    pca_variance: list[float] = Field(alias="pcaVariance")
    assignments: list[ClusterAssignment]
    centroids: list[StableClusterCentroid]
    transitions: list[ClusterTransition]


class DynamicsData(ApiModel):
    measure: Measure
    changes: ChangesArtifact
    clusters: ClusterArtifact
    cluster_model: StableClusterArtifact = Field(alias="clusterModel")


class DynamicsResponse(ApiModel):
    meta: DynamicsMeta
    data: DynamicsData


class OverviewStoryCards(ApiModel):
    trend: TotalSeriesArtifact
    regions: RegionMeanArtifact
    strongest_pair: PairArtifact = Field(alias="strongestPair")
    change_highlights: ChangesArtifact = Field(alias="changeHighlights")
    annual_changes: AnnualChangeArtifact = Field(alias="annualChanges")
    quadrants: QuadrantSummaryArtifact
    change_distribution: ChangeDistributionArtifact = Field(alias="changeDistribution")


class OverviewData(ApiModel):
    measure: Measure
    metrics: OverviewMetrics
    map: OverviewMapArtifact
    ranking: RankingArtifact
    story_cards: OverviewStoryCards = Field(alias="storyCards")
    insights: OverviewInsights


class OverviewResponse(ApiModel):
    meta: OverviewMeta
    data: OverviewData


class ErrorResponse(ApiModel):
    detail: str
    fields: dict[str, str] | None = None
