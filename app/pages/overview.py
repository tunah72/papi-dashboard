"""Trang Tổng quan: KPI, bản đồ, xếp hạng, và link tới bốn hướng phân tích.
Chỉ đọc dữ liệu đã xử lý và hiển thị, không tính toán nặng."""
import streamlit as st

from lib import config, data, charts, filters, layout

layout.page_header(
    "Tổng quan PAPI theo tỉnh",
    "Chỉ số Hiệu quả Quản trị và Hành chính công cấp tỉnh. "
    "Điểm cao thể hiện người dân hài lòng hơn với quản trị địa phương.",
    eyebrow="Bức tranh quản trị cấp tỉnh · 2011–2024",
)

d = data.load_data()
with st.container(border=True):
    mode_col, year_col = st.columns([1.3, 1])
    with mode_col:
        mode = filters.scale_segmented("Phạm vi so sánh")
    cfg = config.scale_config(mode)
    with year_col:
        year = filters.year_inline(
            d, label="Năm xem tổng quan", default=config.YEAR_MAX, year_min=cfg["year_min"]
        )

total_col = cfg["total_col"]
is_six_dim = total_col == "total_papi_6dim"
measure_label = "Tổng 6 lĩnh vực gốc" if is_six_dim else "Tổng PAPI (8 lĩnh vực)"
map_measure_label = "tổng 6 lĩnh vực gốc" if is_six_dim else "tổng PAPI (8 lĩnh vực)"
score_range = (d["prov_year"][total_col].min(), d["prov_year"][total_col].max())
scale_subtitle = (
    "Tổng 6 lĩnh vực gốc, thang 6–60 · tỉnh thiếu dữ liệu để trống"
    if is_six_dim
    else "Tổng 8 lĩnh vực, thang 8–80 · tỉnh thiếu dữ liệu để trống"
)

# Publish trạng thái để AI Assistant dùng làm ngữ cảnh
st.session_state["dash_context"] = {
    "page": "Tổng quan",
    "scale_mode": mode,
    "total_col": total_col,
    "year": int(year),
    "filters": {"scale_mode": mode, "total_col": total_col, "year": int(year)},
    "data_scope": {"table": "prov_year", "score_column": total_col},
}

w = d["prov_year"]
wy = w[w.year == year].dropna(subset=[total_col])
if wy.empty:
    st.warning("Không có dữ liệu cho thước đo và năm đã chọn.")
    st.stop()

top = wy.loc[wy[total_col].idxmax()]
bot = wy.loc[wy[total_col].idxmin()]

layout.kpi_cards([
    {"label": "Số tỉnh có dữ liệu", "value": f"{len(wy)}/63"},
    {"label": f"Điểm trung bình — {measure_label}", "value": f"{wy[total_col].mean():.2f}"},
    {"label": "Dẫn đầu", "value": f"{top.province_vi} ({top[total_col]:.1f})", "big": False},
    {"label": "Xếp cuối", "value": f"{bot.province_vi} ({bot[total_col]:.1f})", "big": False},
])

gap = top[total_col] - bot[total_col]
layout.insight(
    f"{top.province_vi} dẫn đầu, {bot.province_vi} xếp cuối trong năm {year}",
    f"Khoảng cách giữa hai tỉnh là {gap:.1f} điểm theo {measure_label}. "
    "Chọn năm và phạm vi so sánh để kiểm tra mức độ phân hoá theo thời gian.",
    label=f"Snapshot {year}",
)

layout.section_header(
    "Bức tranh theo tỉnh",
    "Bản đồ cho biết vị trí phân bố; xếp hạng giúp đọc nhanh các cực trị của cùng một thước đo.",
)

left, right = st.columns([1.55, 1])
with left:
    with st.container(border=True):
        layout.chart(charts.choropleth(
            wy, d["geojson"], total_col,
            title=f"Bản đồ {map_measure_label} năm {year}",
            subtitle=scale_subtitle,
            range_color=score_range,
        ))
        layout.ai_explain_button(
            f"Bản đồ {map_measure_label} năm {year}",
            context={"data_scope": {"table": "prov_year", "score_column": total_col, "chart": "choropleth"}},
            disabled=wy.empty,
        )
with right:
    with st.container(border=True):
        layout.panel_heading(
            f"Xếp hạng theo {map_measure_label}",
            "Chuyển tab để xem hai đầu của phân phối điểm.",
        )
        tab_top, tab_bot = st.tabs(["Top 10", "Bottom 10"])
        with tab_top:
            st.plotly_chart(charts.bar_ranking(
                wy.nlargest(10, total_col), total_col, "province_vi",
                title="Mười tỉnh có điểm cao nhất", source=None, height=445,
                color=config.TIER_COLORS["Cao nhất"]), width="stretch")
        with tab_bot:
            st.plotly_chart(charts.bar_ranking(
                wy.nsmallest(10, total_col), total_col, "province_vi",
                title="Mười tỉnh có điểm thấp nhất", source=None, height=445,
                color=config.ACCENT), width="stretch")

layout.section_header(
    "Đi từ toàn cảnh đến lời giải thích",
    "Bốn hướng dưới đây nối các phát hiện theo thời gian, tỉnh, lĩnh vực và động lực thay đổi.",
)
stories = [
    ("HƯỚNG 1", "Diễn biến theo thời gian", "Theo dõi các lĩnh vực cải thiện, suy giảm và mốc COVID-19.", "Đã có nội dung", "pages/time_trend.py"),
    ("HƯỚNG 2", "So sánh giữa các tỉnh", "Đặt khác biệt vùng, độ phân tán và vị trí từng tỉnh cạnh nhau.", "Đã có nội dung", "pages/provincial.py"),
    ("HƯỚNG 3", "Phân tích theo lĩnh vực", "Kiểm tra mối liên hệ và phân hoá giữa các lĩnh vực.", "Đã có nội dung", "pages/dimension.py"),
    ("HƯỚNG 4", "Động lực thay đổi và phân nhóm", "Xem tỉnh nào thay đổi và các hồ sơ PAPI nổi bật.", "Đã có nội dung", "pages/dynamics.py"),
]
for row in (stories[:2], stories[2:]):
    cols = st.columns(2)
    for col, (index, title, desc, status, page) in zip(cols, row):
        with col:
            layout.story_card(index, title, desc, status)
            st.page_link(page, label="Mở hướng phân tích")
