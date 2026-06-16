"""Trang Tổng quan: KPI, bản đồ, xếp hạng, và link tới bốn hướng phân tích.
Chỉ đọc dữ liệu đã xử lý và hiển thị, không tính toán nặng."""
import streamlit as st

from lib import config, data, charts, filters

st.title("Tổng quan PAPI 2011-2024")
st.caption("Chỉ số Hiệu quả Quản trị và Hành chính công cấp tỉnh (PAPI). "
           "Nguồn: UNDP, CECODES, RTA. Điểm cao thể hiện người dân hài lòng hơn.")

d = data.load_data()
year = filters.select_year(d, label="Năm xem tổng quan", default=config.YEAR_MAX)

w = d["prov_year"]
wy = w[w.year == year].dropna(subset=["total_papi"])

# KPI
c1, c2, c3, c4 = st.columns(4)
c1.metric("Số tỉnh có dữ liệu", f"{len(wy)}/63")
c2.metric("Điểm PAPI trung bình", f"{wy.total_papi.mean():.2f}")
top = wy.loc[wy.total_papi.idxmax()]
bot = wy.loc[wy.total_papi.idxmin()]
c3.metric("Dẫn đầu", top.province_vi, f"{top.total_papi:.1f}")
c4.metric("Xếp cuối", bot.province_vi, f"{bot.total_papi:.1f}")

st.divider()

# Bản đồ + xếp hạng
left, right = st.columns([3, 2])
with left:
    st.subheader(f"Bản đồ tổng điểm PAPI năm {year}")
    st.plotly_chart(charts.choropleth(wy, d["geojson"], "total_papi"),
                    width="stretch")
with right:
    st.subheader("Xếp hạng")
    tab_top, tab_bot = st.tabs(["Top 10", "Bottom 10"])
    with tab_top:
        st.plotly_chart(charts.bar_ranking(wy.nlargest(10, "total_papi"),
                        "total_papi", "province_vi", color="#2ca02c"),
                        width="stretch")
    with tab_bot:
        st.plotly_chart(charts.bar_ranking(wy.nsmallest(10, "total_papi"),
                        "total_papi", "province_vi", color="#d62728"),
                        width="stretch")

st.divider()

# Link tới bốn hướng phân tích
st.subheader("Bốn hướng phân tích")
cols = st.columns(4)
cols[0].page_link("pages/time_trend.py", label="Diễn biến theo thời gian")
cols[1].page_link("pages/provincial.py", label="So sánh giữa các tỉnh")
cols[2].page_link("pages/dimension.py", label="Phân tích theo trục")
cols[3].page_link("pages/dynamics.py", label="Động lực thay đổi và phân nhóm")
