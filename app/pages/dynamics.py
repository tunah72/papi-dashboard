"""Hướng 4 — thay đổi và phân nhóm profile PAPI."""
import plotly.express as px
import streamlit as st
from lib import config, data, filters, layout
from analysis import dynamics

d=data.load_data()
layout.page_header("Tỉnh nào thay đổi, và thay đổi theo kiểu nào?", "Theo dõi mức thay đổi đầu-cuối, sau đó gom tỉnh có profile lĩnh vực tương đồng để đọc các kiểu quản trị.", eyebrow="Hướng 4 · Động lực và phân nhóm")
with st.container(border=True):
    a,b=st.columns([1.35,1])
    with a: mode=filters.scale_segmented("Phạm vi so sánh")
    cfg=config.scale_config(mode)
    with b: y0,y1=filters.year_range_inline(d,year_min=cfg["year_min"])
total_col=cfg["total_col"]
delta=dynamics.changes(d["prov_year"],total_col,y0,y1)
clusters=dynamics.cluster_profiles(d["prov_year"],y1,cfg["dims"],4)
if delta.empty or clusters.empty: st.warning("Không đủ dữ liệu cho lựa chọn hiện tại."); st.stop()
top, bottom=delta.iloc[0],delta.iloc[-1]
layout.kpi_cards([
 {"label":"Tỉnh tăng nhiều nhất", "value":top.province_vi,"big":False,"delta":(f"{top.change:+.2f} điểm","pos")},
 {"label":"Tỉnh giảm nhiều nhất", "value":bottom.province_vi,"big":False,"delta":(f"{bottom.change:+.2f} điểm","neg")},
 {"label":"Biên độ thay đổi", "value":f"{top.change-bottom.change:.2f}","delta":(f"{y0}–{y1}","neutral")},
 {"label":"Số profile PAPI", "value":str(clusters.cluster.nunique()),"delta":(f"{len(clusters)} tỉnh có dữ liệu","neutral")},])
layout.insight(f"{top.province_vi} tăng {top.change:+.2f} điểm, {bottom.province_vi} thay đổi {bottom.change:+.2f} điểm", f"So sánh dùng đúng hai mốc {y0} và {y1}; không suy diễn nguyên nhân từ mức thay đổi này.", label="Động lực thay đổi")
layout.section_header("Tỉnh nào thay đổi mạnh nhất?", "Mỗi thanh là chênh lệch điểm tổng giữa hai mốc đang chọn.")
with st.container(border=True):
    fig=px.bar(delta, x="change", y="province_vi", orientation="h", color="change", color_continuous_scale=config.DIV_SCALE, hover_data=["region"])
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(coloraxis_showscale=False, height=max(420,28*len(delta)+100), margin=dict(l=16,r=28,t=72,b=54), title=f"Thay đổi điểm tổng, {y0}–{y1}")
    layout.chart(fig); st.caption(config.SOURCE_DEFAULT)
layout.section_header("Bốn profile PAPI theo lĩnh vực", "KMeans chỉ gom các profile tương tự sau khi chuẩn hoá; cụm không phải xếp hạng tốt/xấu.")
with st.container(border=True):
    x,y=cfg["dims"][0],cfg["dims"][1]
    fig=px.scatter(clusters,x=x,y=y,color="cluster",hover_name="province_vi",hover_data=["region"], labels={x:config.DIM_LABELS[x],y:config.DIM_LABELS[y],"cluster":"Profile"})
    fig.update_layout(height=450,margin=dict(l=16,r=24,t=72,b=54),title=f"Profile tỉnh theo {config.DIM_LABELS[x]} và {config.DIM_LABELS[y]}")
    layout.chart(fig); st.caption(config.SOURCE_DEFAULT)
    layout.ai_explain_button("Phân nhóm profile PAPI",context={"data_scope":{"table":"prov_year","year":int(y1),"dimensions":cfg["dims"],"chart":"kmeans"}})
st.session_state["dash_context"]={"page":"Động lực và phân nhóm","filters":{"scale_mode":mode,"year_range":[int(y0),int(y1)]},"data_scope":{"tables":["prov_year"],"score_column":total_col}}
