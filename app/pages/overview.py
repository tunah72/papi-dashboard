"""Trang Tổng quan: KPI, bản đồ, xếp hạng, và link tới bốn hướng phân tích.
Chỉ đọc dữ liệu đã xử lý và hiển thị, không tính toán nặng."""
import streamlit as st

from lib import config, data, charts, filters, layout

layout.page_header(
    "Tổng quan PAPI 2011-2024",
    "Chỉ số Hiệu quả Quản trị và Hành chính công cấp tỉnh. "
    "Điểm cao thể hiện người dân hài lòng hơn với quản trị địa phương.",
)

d = data.load_data()
year = filters.select_year(d, label="Năm xem tổng quan", default=config.YEAR_MAX)

# Publish trạng thái để AI Assistant dùng làm ngữ cảnh
st.session_state["dash_context"] = {
    "page": "Tổng quan",
    "year": int(year),
    "filters": {"year": int(year)},
    "data_scope": {"table": "prov_year", "score_column": "total_papi"},
}

w = d["prov_year"]
wy = w[w.year == year].dropna(subset=["total_papi"])
top = wy.loc[wy.total_papi.idxmax()]
bot = wy.loc[wy.total_papi.idxmin()]

layout.kpi_strip([
    ("Số tỉnh có dữ liệu", f"{len(wy)}/63"),
    ("Điểm PAPI trung bình", f"{wy.total_papi.mean():.2f}"),
    ("Dẫn đầu", top.province_vi, f"{top.total_papi:.1f}"),
    ("Xếp cuối", bot.province_vi, f"{bot.total_papi:.1f}"),
])

st.divider()

left, right = st.columns([3, 2])
with left:
    layout.chart(charts.choropleth(
        wy, d["geojson"], "total_papi",
        title=f"Bản đồ tổng điểm PAPI năm {year}",
        subtitle="Tổng 8 trục, thang 8–80 · tỉnh thiếu dữ liệu để trống",
    ))
    layout.ai_explain_button(
        f"Bản đồ PAPI năm {year}",
        context={"data_scope": {"table": "prov_year", "score_column": "total_papi", "chart": "choropleth"}},
        disabled=wy.empty,
    )
with right:
    layout.section_header("Xếp hạng")
    tab_top, tab_bot = st.tabs(["Top 10", "Bottom 10"])
    with tab_top:
        st.plotly_chart(charts.bar_ranking(
            wy.nlargest(10, "total_papi"), "total_papi", "province_vi",
            color=config.TIER_COLORS["Cao nhất"], source=None), width="stretch")
    with tab_bot:
        st.plotly_chart(charts.bar_ranking(
            wy.nsmallest(10, "total_papi"), "total_papi", "province_vi",
            color=config.ACCENT, source=None), width="stretch")

st.divider()

layout.section_header("Bốn hướng phân tích")
cols = st.columns(4)
cols[0].page_link("pages/time_trend.py", label="Diễn biến theo thời gian")
cols[1].page_link("pages/provincial.py", label="So sánh giữa các tỉnh")
cols[2].page_link("pages/dimension.py", label="Phân tích theo trục")
cols[3].page_link("pages/dynamics.py", label="Động lực thay đổi và phân nhóm")
