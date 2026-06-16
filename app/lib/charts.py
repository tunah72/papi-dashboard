"""Thư viện biểu đồ plotly tái sử dụng. Mỗi hàm nhận dữ liệu + tham số, trả về một plotly Figure.
Page gọi hàm rồi st.plotly_chart(fig). Signature các hàm là contract dùng chung, không đổi tùy tiện."""
import plotly.express as px
import plotly.graph_objects as go

TEMPLATE = "plotly_white"


def choropleth(df, geojson, value_col, name_col="province_vi", title=None, color_scale="Blues"):
    """Choropleth 63 tỉnh. df cần cột `province_id` và `value_col`; join geojson theo
    properties.province_id."""
    fig = px.choropleth(
        df, geojson=geojson, locations="province_id",
        featureidkey="properties.province_id", color=value_col,
        hover_name=name_col, color_continuous_scale=color_scale, template=TEMPLATE,
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title=title, margin=dict(l=0, r=0, t=40, b=0))
    return fig


def line_trend(df, x="year", y="mean_score", color="code", color_map=None, labels=None, title=None):
    """Line chart, mặc định vẽ xu hướng điểm theo năm cho từng trục."""
    fig = px.line(df, x=x, y=y, color=color, color_discrete_map=color_map,
                  markers=True, labels=labels, template=TEMPLATE)
    fig.update_layout(title=title, hovermode="x unified")
    return fig


def bar_ranking(df, value_col, name_col, title=None, color="#1f77b4", ascending=False):
    """Horizontal bar xếp hạng (vd top/bottom tỉnh). Cao nhất ở trên cùng."""
    d = df.sort_values(value_col, ascending=ascending)
    fig = px.bar(d, x=value_col, y=name_col, orientation="h", template=TEMPLATE)
    fig.update_traces(marker_color=color)
    fig.update_layout(title=title, yaxis=dict(autorange="reversed"),
                      margin=dict(l=0, r=0, t=40, b=0))
    return fig


def radar(categories, values, name=None, title=None, color="#1f77b4", rng=(0, 10)):
    """Radar 8 trục cho một đối tượng (vd một tỉnh). categories và values cùng độ dài."""
    cats = list(categories); vals = list(values)
    fig = go.Figure(go.Scatterpolar(
        r=vals + vals[:1], theta=cats + cats[:1], fill="toself",
        name=name, line_color=color))
    fig.update_layout(title=title, template=TEMPLATE,
                      polar=dict(radialaxis=dict(range=list(rng))),
                      showlegend=name is not None)
    return fig


def heatmap(matrix, title=None, color_scale="RdBu_r", zmin=-1, zmax=1):
    """Heatmap, mặc định cho correlation matrix (giá trị -1..1)."""
    fig = px.imshow(matrix, text_auto=".2f", color_continuous_scale=color_scale,
                    zmin=zmin, zmax=zmax, aspect="auto", template=TEMPLATE)
    fig.update_layout(title=title)
    return fig


def boxplot(df, x, y, color=None, title=None, category_order=None):
    """Boxplot phân phối. category_order là thứ tự nhóm trên trục x."""
    orders = {x: category_order} if category_order else None
    fig = px.box(df, x=x, y=y, color=color, category_orders=orders, template=TEMPLATE)
    fig.update_layout(title=title)
    return fig


def slopegraph(df, label_col, year_col, value_col, year_start, year_end, title=None, color="#888"):
    """Slopegraph nối hai mốc năm cho mỗi đối tượng (vd tỉnh)."""
    d = df[df[year_col].isin([year_start, year_end])]
    fig = go.Figure()
    for label, g in d.groupby(label_col):
        g = g.set_index(year_col)
        if year_start in g.index and year_end in g.index:
            fig.add_trace(go.Scatter(
                x=[year_start, year_end],
                y=[g.loc[year_start, value_col], g.loc[year_end, value_col]],
                mode="lines+markers", name=str(label), showlegend=False,
                line=dict(color=color, width=1)))
    fig.update_layout(title=title, template=TEMPLATE,
                      xaxis=dict(tickvals=[year_start, year_end]))
    return fig
