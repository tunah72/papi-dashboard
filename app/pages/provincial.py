"""Hướng 2 — Đọc khác biệt PAPI giữa vùng và vị trí của từng tỉnh."""
import plotly.graph_objects as go
import streamlit as st

# Import lib.config trước để đăng ký src/ vào sys.path, sau đó mới import analysis.
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
    """Chuỗi chênh lệch gọn, có dấu để đọc benchmark nhanh."""
    return f"{value:+.2f}"


d = data.load_data()

layout.page_header(
    "Khác biệt PAPI giữa các vùng và tỉnh",
    "So sánh mức điểm, độ phân tán trong vùng và vị trí của một tỉnh so với hai benchmark phù hợp.",
    eyebrow="Hướng 2 · So sánh không gian",
)

# ── Control bar ────────────────────────────────────────────────────────────────────────
with st.container(border=True):
    scale_col, year_col = st.columns([1.35, 1])
    with scale_col:
        mode = filters.scale_segmented("Phạm vi so sánh")
    cfg = config.scale_config(mode)
    with year_col:
        year = filters.year_inline(d, "Năm so sánh", year_min=cfg["year_min"])

total_col = cfg["total_col"]
snapshot = provincial.snapshot_for_year(d["prov_year"], year, total_col)
summary = provincial.region_summary(snapshot, total_col, config.REGION_ORDER)

if snapshot.empty or summary.empty:
    st.warning("Không có đủ dữ liệu tỉnh cho thước đo và năm đang chọn.")
    st.stop()

available_regions = [region for region in config.REGION_ORDER if region in set(summary.region.astype(str))]
default_region = str(summary.iloc[0].region)

with st.container(border=True):
    region = st.selectbox(
        "Đi sâu vào vùng", available_regions,
        index=available_regions.index(default_region), key="h2_region",
    )

ranking = provincial.ranking_in_region(snapshot, region, total_col)
province_options = ranking.province_vi.tolist()
province = st.selectbox("Tỉnh cần đối chiếu", province_options, key="h2_province")
benchmarks = provincial.province_benchmarks(snapshot, region, province, total_col)

# Publish trạng thái để AI Assistant kế thừa câu hỏi và phạm vi dữ liệu đúng.
st.session_state["dash_context"] = {
    "page": "So sánh giữa các tỉnh và vùng",
    "scale_mode": mode,
    "total_col": total_col,
    "year": int(year),
    "region": region,
    "province": province,
    "filters": {
        "scale_mode": mode,
        "year": int(year),
        "region": region,
        "province": province,
        "dims": {code: config.DIM_LABELS[code] for code in cfg["dims"]},
    },
    "data_scope": {"tables": ["prov_year", "national"], "score_column": total_col},
}

top_region = summary.iloc[0]
bottom_region = summary.iloc[-1]
selected_region = summary.loc[summary.region.astype(str).eq(region)].iloc[0]
metric_label = "tổng 6 lĩnh vực gốc" if total_col == "total_papi_6dim" else "tổng PAPI (8 lĩnh vực)"

layout.kpi_cards([
    {"label": "Vùng có điểm trung bình cao nhất", "value": str(top_region.region), "big": False,
     "delta": (f"{top_region.mean_score:.2f} điểm", "pos")},
    {"label": "Vùng có điểm trung bình thấp nhất", "value": str(bottom_region.region), "big": False,
     "delta": (f"{bottom_region.mean_score:.2f} điểm", "neg")},
    {"label": "Chênh lệch giữa hai vùng", "value": f"{top_region.mean_score - bottom_region.mean_score:.2f}",
     "delta": (f"{year} · {metric_label}", "neutral")},
    {"label": f"Độ phân tán tại {region}", "value": f"{selected_region.spread:.2f}",
     "delta": (f"{int(selected_region.n_provinces)} tỉnh có dữ liệu", "neutral")},
])

regional_gap = top_region.mean_score - bottom_region.mean_score
layout.insight(
    f"Khoảng cách trung bình vùng là {regional_gap:.2f} điểm trong năm {year}",
    f"{top_region.region} có mức trung bình cao nhất, trong khi {bottom_region.region} thấp nhất theo {metric_label}. "
    f"Riêng {region} có độ chênh nội vùng {selected_region.spread:.2f} điểm, nên trung bình vùng không kể hết câu chuyện của từng tỉnh.",
    label="Đọc hai tầng: vùng và tỉnh",
)

# ── Phân phối vùng ─────────────────────────────────────────────────────────────────────
layout.section_header(
    "Khác biệt không chỉ nằm ở mức trung bình",
    "Mỗi chấm là một tỉnh có dữ liệu. Hộp cho biết khoảng phân bố trong vùng, không phải thứ hạng hành chính.",
)

distribution_col, mean_col = st.columns([1.6, 1])
with distribution_col:
    with st.container(border=True):
        fig_distribution = charts.boxplot(
            snapshot, x="region", y=total_col, color="region", points="all",
            category_order=available_regions, color_map=config.REGION_COLORS,
            title=f"Phân phối {metric_label} giữa các vùng, {year}",
            subtitle="Chấm = một tỉnh có dữ liệu · hộp = phân bố nội vùng",
            source=None,
            height=470,
        )
        fig_distribution.update_layout(showlegend=False, margin=dict(l=16, r=24, t=82, b=94))
        fig_distribution.update_xaxes(
            tickvals=available_regions,
            ticktext=[REGION_TICK_LABELS[item] for item in available_regions],
            tickfont=dict(size=11), tickangle=0,
        )
        fig_distribution.update_traces(marker=dict(size=5, opacity=.78))
        layout.chart(fig_distribution)
        st.caption(config.SOURCE_DEFAULT)
        layout.ai_explain_button(
            "Phân phối điểm giữa các vùng",
            context={"data_scope": {"table": "prov_year", "score_column": total_col, "chart": "boxplot", "year": int(year)}},
            disabled=snapshot.empty,
        )

with mean_col:
    with st.container(border=True):
        plot_summary = summary.sort_values("mean_score")
        fig_means = go.Figure(go.Bar(
            x=plot_summary.mean_score,
            y=plot_summary.region.astype(str),
            orientation="h",
            marker_color=[config.REGION_COLORS[item] for item in plot_summary.region.astype(str)],
            text=plot_summary.mean_score,
            texttemplate="%{text:.2f}", textposition="outside",
            hovertemplate="%{y}: %{x:.2f} điểm<extra></extra>",
        ))
        charts.apply_owid(
            fig_means, title="Trung bình từng vùng",
            subtitle=f"{metric_label.capitalize()} · {year}", source=None, height=470,
        )
        lo = max(0, float(plot_summary.mean_score.min()) - 1.1)
        hi = float(plot_summary.mean_score.max()) + 1.5
        fig_means.update_layout(margin=dict(l=16, r=70, t=82, b=78), showlegend=False)
        fig_means.update_xaxes(range=[lo, hi])
        fig_means.update_yaxes(
            ticktext=[REGION_TICK_LABELS[item] for item in plot_summary.region.astype(str)],
            tickvals=plot_summary.region.astype(str), tickfont=dict(size=10.5),
        )
        layout.chart(fig_means)
        st.caption(config.SOURCE_DEFAULT)

# ── Drill-down vùng/tỉnh ───────────────────────────────────────────────────────────────
layout.section_header(
    f"{province} đứng ở đâu trong {region}?",
    "Đặt tỉnh cạnh trung bình vùng và toàn bộ các tỉnh có dữ liệu trong cùng năm, thay vì so sánh với một mốc không liên quan.",
)

rank_col, profile_col = st.columns([1.08, 1])
with rank_col:
    with st.container(border=True):
        rank_colors = [config.ACCENT if item == province else "#8FA8CB" for item in ranking.province_vi]
        fig_rank = go.Figure(go.Bar(
            x=ranking[total_col], y=ranking.province_vi, orientation="h",
            marker_color=rank_colors, text=ranking[total_col],
            texttemplate="%{text:.2f}", textposition="outside",
            hovertemplate="%{y}: %{x:.2f} điểm<extra></extra>",
        ))
        charts.apply_owid(
            fig_rank, title=f"Xếp hạng tỉnh trong {region}",
            subtitle=f"Tô đỏ: {province} · {year}", source=None,
            height=max(360, 37 * len(ranking) + 105),
        )
        fig_rank.update_layout(margin=dict(l=16, r=86, t=82, b=62))
        fig_rank.update_traces(cliponaxis=False)
        fig_rank.update_xaxes(range=[0, float(ranking[total_col].max()) + 1.4])
        fig_rank.update_yaxes(autorange="reversed")
        layout.chart(fig_rank)
        st.caption(config.SOURCE_DEFAULT)
        layout.note(
            f"{province} đứng thứ {int(ranking.loc[ranking.province_vi.eq(province), 'rank_region'].iloc[0])}/{len(ranking)} "
            f"trong số tỉnh có dữ liệu của vùng."
        )

with profile_col:
    with st.container(border=True):
        profile = provincial.dimension_benchmarks(
            d["prov_year"], year, region, province, cfg["dims"]
        )
        short_labels = dict(zip(d["dim_ind"].code, d["dim_ind"].short))
        short_labels.update({"D4": "Chống TN", "D7": "Môi trường", "D8": "QT điện tử"})
        categories = [short_labels[code] for code in cfg["dims"]]
        fig_profile = charts.radar_comparison(
            categories,
            [
                {"name": province, "values": profile.province_score, "color": config.ACCENT, "fill": "toself", "opacity": .35, "width": 3},
                {"name": "Trung bình vùng", "values": profile.region_mean, "color": "#4C6A9C", "width": 2.2},
                {"name": "Trung bình tất cả tỉnh", "values": profile.national_mean, "color": "#66717F", "width": 1.8},
            ],
            title=f"Profile lĩnh vực của {province}",
            subtitle="So với hai benchmark trong cùng năm", source=None,
            rng=(0, 10), height=max(390, 42 * len(categories) + 100),
        )
        fig_profile.update_layout(margin=dict(l=34, r=34, t=82, b=84))
        layout.chart(fig_profile)
        st.caption(config.SOURCE_DEFAULT)
        layout.ai_explain_button(
            f"Profile PAPI của {province}",
            context={"data_scope": {"table": "prov_year", "score_column": total_col, "year": int(year), "region": region, "province": province, "chart": "radar"}},
            disabled=profile.empty,
        )

comparison_word = "cao hơn" if benchmarks["vs_region"] >= 0 else "thấp hơn"
layout.insight(
    f"{province} {comparison_word} trung bình {region} {abs(benchmarks['vs_region']):.2f} điểm",
    f"So với trung bình tất cả tỉnh có dữ liệu, chênh lệch là {signed(benchmarks['vs_national'])} điểm. "
    "Radar dùng cùng năm và cùng phạm vi lĩnh vực đang chọn để tránh so sánh lệch kỳ.",
    label="Kết luận cho tỉnh đang chọn",
)
