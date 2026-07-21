"""Hướng 2 — đọc khác biệt PAPI giữa vùng và vị trí của một tỉnh."""
import plotly.graph_objects as go
import streamlit as st

from lib import charts, config, data, filters, layout
from analysis import provincial


REGION_TICK_LABELS = {
    "Trung du và miền núi phía Bắc": "TDMN<br>phía Bắc",
    "Đồng bằng sông Hồng": "ĐBS<br>Hồng",
    "Bắc Trung Bộ và Duyên hải miền Trung": "BTB & DH<br>miền Trung",
    "Tây Nguyên": "Tây<br>Nguyên",
    "Đông Nam Bộ": "Đông<br>Nam Bộ",
    "Đồng bằng sông Cửu Long": "ĐBS<br>Cửu Long",
}


def signed(value):
    return f"{value:+.2f}"


def sync_query_params(mode, year, region, province):
    """Lưu state chính để URL tái tạo được phân tích đang xem."""
    desired = {
        "h2_scale": "6" if mode == config.SCALE_6DIM else "8",
        "h2_year": str(year),
        "h2_region": region,
        "h2_province": province,
    }
    for key, value in desired.items():
        if st.query_params.get(key) != value:
            st.query_params[key] = value


d = data.load_data()
layout.page_header(
    "So sánh PAPI giữa vùng & tỉnh",
    "Chọn một tỉnh trên bản đồ để đối chiếu ngay với vùng và mặt bằng các tỉnh có dữ liệu.",
    eyebrow="Hướng 2 · So sánh không gian",
)
layout.story_route(2)

with st.container(border=True):
    scale_col, year_col, pair_col = st.columns([1.15, 1, 1.25])
    query_scale = st.query_params.get("h2_scale")
    default_mode = config.SCALE_8DIM if query_scale == "8" else config.SCALE_6DIM
    with scale_col:
        mode = filters.scale_segmented("Phạm vi so sánh", default=default_mode, key="h2_scale_control")
    cfg = config.scale_config(mode)
    query_year = st.query_params.get("h2_year")
    default_year = int(query_year) if str(query_year).isdigit() else config.YEAR_MAX
    with year_col:
        year = filters.year_inline(d, "Năm so sánh", default=default_year, year_min=cfg["year_min"])
    with pair_col:
        year_start, year_end = filters.year_range_inline(
            d, "Hai mốc thay đổi", year_min=cfg["year_min"]
        )

total_col = cfg["total_col"]
metric_label = "tổng 6 lĩnh vực gốc" if total_col == "total_papi_6dim" else "tổng PAPI (8 lĩnh vực)"
snapshot = provincial.snapshot_for_year(d["prov_year"], year, total_col)
summary = provincial.region_summary(snapshot, total_col, config.REGION_ORDER)
if snapshot.empty or summary.empty:
    st.warning("Không có đủ dữ liệu tỉnh cho thước đo và năm đang chọn.")
    st.stop()

available_regions = [region for region in config.REGION_ORDER if region in set(summary.region.astype(str))]
query_region = st.query_params.get("h2_region")
if st.session_state.get("h2_region") not in available_regions:
    st.session_state["h2_region"] = query_region if query_region in available_regions else str(summary.iloc[0].region)

layout.section_header(
    f"Chọn một tỉnh trên bản đồ, {year}",
    f"{len(snapshot)} tỉnh có dữ liệu theo {metric_label}. Điểm màu cao hơn không phải là thứ hạng hành chính.",
)
with st.container(border=True):
    fig_map = charts.choropleth(
        snapshot, d["geojson"], total_col, title=None, subtitle=None, source=None, height=490,
    )
    map_event = st.plotly_chart(
        fig_map, on_select="rerun", selection_mode="points", key="h2_map",
        config={"displayModeBar": False}, width="stretch",
    )

try:
    points = map_event.selection.points
    selected_map_id = points[0].get("location") if points else None
except Exception:
    selected_map_id = None
if selected_map_id is not None:
    selected_map = snapshot.loc[snapshot.province_id.astype(str).eq(str(selected_map_id))]
    if not selected_map.empty:
        st.session_state["h2_region"] = selected_map.iloc[0].region
        st.session_state["h2_province"] = selected_map.iloc[0].province_vi

with st.container(border=True):
    region = st.selectbox("Vùng", available_regions, key="h2_region")
    ranking = provincial.ranking_in_region(snapshot, region, total_col)
    province_options = ranking.province_vi.tolist()
    query_province = st.query_params.get("h2_province")
    if st.session_state.get("h2_province") not in province_options:
        st.session_state["h2_province"] = query_province if query_province in province_options else province_options[0]
    province = st.selectbox("Tỉnh", province_options, key="h2_province")

benchmarks = provincial.province_benchmarks(snapshot, region, province, total_col)
sync_query_params(mode, year, region, province)
st.caption(f"Đang xem: **{province}** · {region} · {year}")

st.session_state["dash_context"] = {
    "page": "So sánh giữa các tỉnh và vùng", "scale_mode": mode,
    "total_col": total_col, "year": int(year), "region": region, "province": province,
    "filters": {"scale_mode": mode, "year": int(year), "region": region, "province": province,
                "dims": {code: config.DIM_LABELS[code] for code in cfg["dims"]}},
    "data_scope": {"tables": ["prov_year", "national"], "score_column": total_col},
}

# Drill-down đứng ngay sau map để click có phản hồi tại chỗ.
layout.section_header(
    f"{province} đứng ở đâu trong {region}?",
    "So sánh trong cùng năm, cùng thước đo và chỉ với các tỉnh có dữ liệu.",
)
rank_col, profile_col = st.columns([1.08, 1])
with rank_col:
    with st.container(border=True):
        rank_colors = [config.ACCENT if item == province else "#8FA8CB" for item in ranking.province_vi]
        fig_rank = go.Figure(go.Bar(
            x=ranking[total_col], y=ranking.province_vi, orientation="h", marker_color=rank_colors,
            text=ranking[total_col], texttemplate="%{text:.2f}", textposition="outside",
            hovertemplate="%{y}: %{x:.2f} điểm<extra></extra>",
        ))
        charts.apply_owid(fig_rank, title="Xếp hạng trong vùng", subtitle=f"Tô đỏ: {province}", source=None,
                          height=max(350, 34 * len(ranking) + 88))
        fig_rank.update_layout(margin=dict(l=16, r=86, t=76, b=34))
        fig_rank.update_traces(cliponaxis=False)
        fig_rank.update_xaxes(range=[0, float(ranking[total_col].max()) + 1.4])
        fig_rank.update_yaxes(autorange="reversed")
        layout.chart(fig_rank)
with profile_col:
    with st.container(border=True):
        profile = provincial.dimension_benchmarks(d["prov_year"], year, region, province, cfg["dims"])
        short_labels = dict(zip(d["dim_ind"].code, d["dim_ind"].short))
        short_labels.update({"D4": "Chống TN", "D7": "Môi trường", "D8": "QT điện tử"})
        fig_profile = charts.radar_comparison(
            [short_labels[code] for code in cfg["dims"]],
            [
                {"name": province, "values": profile.province_score, "color": config.ACCENT, "fill": "toself", "opacity": .35, "width": 3},
                {"name": "Trung bình vùng", "values": profile.region_mean, "color": "#4C6A9C", "width": 2.2},
                {"name": "Trung bình tất cả tỉnh", "values": profile.national_mean, "color": "#66717F", "width": 1.8},
            ], title="Profile lĩnh vực", subtitle="Hai benchmark cùng năm", source=None,
            rng=(0, 10), height=410,
        )
        fig_profile.update_layout(margin=dict(l=34, r=34, t=76, b=84))
        layout.chart(fig_profile)

comparison_word = "cao hơn" if benchmarks["vs_region"] >= 0 else "thấp hơn"
layout.insight(
    f"{province} {comparison_word} trung bình {region} {abs(benchmarks['vs_region']):.2f} điểm",
    f"So với trung bình tất cả tỉnh có dữ liệu, chênh lệch là {signed(benchmarks['vs_national'])} điểm.",
    label="Đọc tỉnh được chọn",
)

top_region, bottom_region = summary.iloc[0], summary.iloc[-1]
selected_region = summary.loc[summary.region.astype(str).eq(region)].iloc[0]
layout.kpi_cards([
    {"label": "Vùng trung bình cao nhất", "value": str(top_region.region), "big": False,
     "delta": (f"{top_region.mean_score:.2f} điểm", "pos")},
    {"label": "Chênh lệch vùng cao-thấp", "value": f"{top_region.mean_score - bottom_region.mean_score:.2f}",
     "delta": (f"{year} · {metric_label}", "neutral")},
    {"label": f"Độ phân tán {region}", "value": f"{selected_region.spread:.2f}",
     "delta": (f"{int(selected_region.n_provinces)} tỉnh có dữ liệu", "neutral")},
])

layout.section_header("Khác biệt giữa các vùng", "Mỗi chấm là một tỉnh có dữ liệu; hộp mô tả phân bố nội vùng.")
with st.container(border=True):
    fig_distribution = charts.boxplot(
        snapshot, x="region", y=total_col, color="region", points="all",
        category_order=available_regions, color_map=config.REGION_COLORS,
        title=None, subtitle=None, source=None, height=430,
    )
    fig_distribution.update_layout(showlegend=False, margin=dict(l=16, r=24, t=22, b=94))
    fig_distribution.update_xaxes(tickvals=available_regions,
                                  ticktext=[REGION_TICK_LABELS[item] for item in available_regions],
                                  tickfont=dict(size=11), tickangle=0)
    fig_distribution.update_traces(marker=dict(size=5, opacity=.78))
    layout.chart(fig_distribution)
    st.caption(config.SOURCE_DEFAULT)

layout.section_header("Khám phá thêm", "Mở một câu hỏi phụ tại một thời điểm để giữ phần chính dễ đọc.")
explore_mode = st.segmented_control("Câu hỏi phụ", ["Cực trị", "Thay đổi"], default="Cực trị", key="h2_explore")
if explore_mode == "Thay đổi":
    changed = provincial.largest_absolute_changes(d["prov_year"], year_start, year_end, total_col, n=7)
    if changed.empty:
        st.info(f"Không có tỉnh nào có đủ {metric_label} ở cả hai năm {year_start} và {year_end}.")
    else:
        with st.container(border=True):
            chart_data = changed.rename(columns={"province_vi": "Tỉnh", "delta": "Thay đổi"})
            fig_change = charts.diverging_bar(
                chart_data, "Tỉnh", "Thay đổi", title=None, subtitle=None, source=None, height=380,
            )
            fig_change.update_layout(margin=dict(l=16, r=36, t=18, b=38))
            layout.chart(fig_change)
            st.caption(f"Nguồn: PAPI — UNDP, CECODES, RTA · {year_start}–{year_end} · 7 tỉnh đổi mạnh nhất.")
else:
    top, bottom = provincial.top_bottom(snapshot, total_col, n=5)
    outliers = provincial.zscore_outliers(snapshot, total_col)
    top_col, bottom_col = st.columns(2)
    with top_col:
        with st.container(border=True):
            layout.chart(charts.bar_ranking(top, total_col, "province_vi", title="5 tỉnh điểm cao nhất",
                                             subtitle=None, source=None, color="#4C6A9C", height=315))
    with bottom_col:
        with st.container(border=True):
            layout.chart(charts.bar_ranking(bottom, total_col, "province_vi", title="5 tỉnh điểm thấp nhất",
                                             subtitle=None, source=None, color=config.ACCENT, ascending=True, height=315))
    flagged = outliers.loc[outliers.is_outlier]
    if not flagged.empty:
        st.caption("Ngoại lệ z-score mẫu (|z| > 2): " + ", ".join(flagged.province_vi.tolist()))
    st.caption(config.SOURCE_DEFAULT)
