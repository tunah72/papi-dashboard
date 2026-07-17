"""Hướng 3 — quan hệ giữa các lĩnh vực PAPI trong cùng một năm."""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import charts, config, data, filters, layout
from analysis import dimensions

d = data.load_data()
layout.page_header("Các lĩnh vực PAPI có đi cùng nhau?",
    "Đọc tương quan giữa các tỉnh trong cùng năm, sau đó kiểm tra từng cặp lĩnh vực thay vì suy diễn từ điểm tổng.",
    eyebrow="Hướng 3 · Mối liên hệ giữa lĩnh vực")

with st.container(border=True):
    c1, c2 = st.columns([1.35, 1])
    with c1: mode = filters.scale_segmented("Phạm vi so sánh")
    cfg = config.scale_config(mode)
    with c2: year = filters.year_inline(d, "Năm so sánh", year_min=cfg["year_min"])

dims = cfg["dims"]
snapshot = dimensions.snapshot_for_year(d["prov_year"], year, dims)
if snapshot.empty:
    st.warning("Không đủ dữ liệu cho năm và phạm vi đang chọn.")
    st.stop()

labels = config.DIM_LABELS
code_from_label = {labels[c]: c for c in dims}
with st.container(border=True):
    x_col, y_col = st.columns(2)
    with x_col: x_label = st.selectbox("Lĩnh vực trục X", list(code_from_label), index=min(1, len(dims)-1), key="h3_x")
    with y_col:
        choices = [label for label in code_from_label if label != x_label]
        y_label = st.selectbox("Lĩnh vực trục Y", choices, index=0, key="h3_y")
x_code, y_code = code_from_label[x_label], code_from_label[y_label]
pair, x_mean, y_mean, corr = dimensions.pair_snapshot(snapshot, x_code, y_code)
summary = dimensions.summaries(snapshot, dims)
corr_matrix = dimensions.correlation_matrix(snapshot, dims)

st.session_state["dash_context"] = {"page":"Phân tích theo lĩnh vực", "year":int(year), "scale_mode":mode,
    "filters":{"year":int(year), "scale_mode":mode, "x_dimension":x_label, "y_dimension":y_label},
    "data_scope":{"tables":["prov_year"], "dimensions":{c:labels[c] for c in dims}, "chart":"correlation/scatter"}}

top_mean, low_mean = summary.loc[summary.mean_score.idxmax()], summary.loc[summary.mean_score.idxmin()]
strongest = corr_matrix.where(~__import__('numpy').eye(len(dims), dtype=bool)).stack().abs().idxmax()
strongest_value = corr_matrix.loc[strongest[0], strongest[1]]
layout.kpi_cards([
    {"label":"Lĩnh vực có điểm TB cao nhất", "value":labels[top_mean.code], "big":False, "delta":(f"{top_mean.mean_score:.2f} điểm", "pos")},
    {"label":"Lĩnh vực có điểm TB thấp nhất", "value":labels[low_mean.code], "big":False, "delta":(f"{low_mean.mean_score:.2f} điểm", "neg")},
    {"label":"Tương quan cặp đang chọn", "value":f"r = {corr:+.2f}", "delta":(f"{len(pair)} tỉnh có dữ liệu", "neutral")},
    {"label":"Cặp có |r| lớn nhất", "value":f"{labels[strongest[0]]} · {labels[strongest[1]]}", "big":False, "delta":(f"r = {strongest_value:+.2f}", "neutral")},
])

word = "đồng biến" if corr >= .3 else "nghịch biến" if corr <= -.3 else "liên hệ tuyến tính yếu"
layout.insight(f"{x_label} và {y_label} có {word} trong năm {year}",
    f"Hệ số Pearson r = {corr:+.2f} trên {len(pair)} tỉnh. Đây là mối liên hệ quan sát, không chứng minh quan hệ nhân quả.", label="Đọc tương quan đúng cách")

layout.section_header("Bản đồ quan hệ của các lĩnh vực", "Ô màu cho biết các lĩnh vực cùng cao/thấp ở các tỉnh; chỉ đọc nửa dưới đường chéo để tránh lặp lại.")
with st.container(border=True):
    named = corr_matrix.rename(index=labels, columns=labels)
    fig_hm = charts.heatmap(named, title=f"Tương quan giữa các lĩnh vực, {year}",
                            subtitle="Pearson r theo tỉnh · xanh = đồng biến, đỏ = nghịch biến", zmin=-1, zmax=1,
                            height=max(420, 52 * len(dims) + 100), text_auto=".2f")
    layout.chart(fig_hm)
    st.caption(config.SOURCE_DEFAULT)

layout.section_header("Kiểm tra một cặp lĩnh vực", "Đường ngang/dọc là trung bình các tỉnh có dữ liệu. Màu sắc chỉ phần tư, không phải xếp hạng tốt/xấu.")
with st.container(border=True):
    fig = px.scatter(pair, x=x_code, y=y_code, color="quadrant", hover_name="province_vi", hover_data={"region":True, "quadrant":True},
                     color_discrete_map={"Cao–cao":"#2C8C99", "Thấp–thấp":"#B13507", "Cao–thấp":"#6D4C9C", "Thấp–cao":"#E0A23B"})
    charts.apply_owid(fig, title=f"{x_label} và {y_label} theo tỉnh", subtitle=f"r = {corr:+.2f} · {year}", source=None, height=470)
    fig.add_vline(x=x_mean, line_dash="dot", line_color="#7A8490")
    fig.add_hline(y=y_mean, line_dash="dot", line_color="#7A8490")
    fig.update_layout(legend=dict(orientation="h", y=-.2), margin=dict(l=16,r=24,t=82,b=88))
    layout.chart(fig)
    st.caption(config.SOURCE_DEFAULT)
    layout.ai_explain_button("Mối liên hệ giữa hai lĩnh vực", context={"data_scope":{"table":"prov_year","year":int(year),"x":x_code,"y":y_code,"chart":"scatter"}})

layout.section_header("Lĩnh vực nào phân hoá mạnh nhất giữa các tỉnh?", "Độ lệch chuẩn lớn hơn nghĩa là chênh lệch giữa các tỉnh lớn hơn trong cùng thang điểm.")
with st.container(border=True):
    ordered = summary.sort_values("std_score")
    fig_std = go.Figure(go.Bar(x=ordered.std_score, y=[labels[c] for c in ordered.code], orientation="h", marker_color=config.ACCENT,
                               text=ordered.std_score, texttemplate="%{text:.2f}", textposition="outside"))
    charts.apply_owid(fig_std, title=f"Độ phân tán điểm theo lĩnh vực, {year}", subtitle="Độ lệch chuẩn giữa các tỉnh", source=None, height=max(340, 48*len(dims)+100))
    fig_std.update_traces(cliponaxis=False); fig_std.update_yaxes(autorange="reversed"); fig_std.update_xaxes(range=[0,float(ordered.std_score.max())+0.25]); fig_std.update_layout(margin=dict(l=16,r=70,t=82,b=58))
    layout.chart(fig_std); st.caption(config.SOURCE_DEFAULT)
