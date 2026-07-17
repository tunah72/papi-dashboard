"""Thư viện biểu đồ plotly tái sử dụng — phong cách Our World in Data.

Mỗi hàm nhận dữ liệu + tham số, trả về một plotly Figure đã được style sẵn:
gridline ngang nhạt, không khung viền, tiêu đề khẳng định + phụ đề mô tả + dòng nguồn,
và (với line) nhãn gắn trực tiếp cuối đường thay cho legend.

Thành viên chỉ cần gọi hàm với title/subtitle/source rồi st.plotly_chart(fig). Toàn bộ
style nằm trong file này, không cần chỉnh ở trang phân tích. Signature là contract dùng chung.
"""
import plotly.express as px
import plotly.graph_objects as go

from lib import config

TEMPLATE = "plotly_white"


def apply_owid(fig, title=None, subtitle=None, source=config.SOURCE_DEFAULT,
               cartesian=True, height=390):
    """Áp toàn bộ style OWID lên một figure: font, lề, tiêu đề + phụ đề, nguồn, lưới.
    cartesian=False cho biểu đồ không có trục x/y thường (choropleth, radar)."""
    title_obj = None
    if title:
        title_obj = dict(text=title, x=0, xanchor="left", y=0.98, yanchor="top",
                         font=dict(size=19, color=config.TITLE_COLOR, family="Iowan Old Style, Palatino Linotype, Georgia, serif"))
        if subtitle:
            title_obj["subtitle"] = dict(text=subtitle,
                                         font=dict(size=14, color=config.SUBTITLE_COLOR))
    top = (82 if subtitle else 58) if title else 16
    bottom = 62 if source else 16
    fig.update_layout(
        template=TEMPLATE, height=height,
        font=dict(family=config.FONT_FAMILY, size=14, color=config.INK),
        title=title_obj, paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=16, r=78, t=top, b=bottom),
    )
    if cartesian:
        fig.update_xaxes(showgrid=False, showline=False, zeroline=False, ticks="outside",
                         ticklen=4, tickcolor=config.GRID_COLOR,
                         tickfont=dict(color=config.AXIS_COLOR, size=12.5), title=None)
        fig.update_yaxes(showgrid=True, gridcolor=config.GRID_COLOR, gridwidth=1,
                         showline=False, zeroline=False,
                         tickfont=dict(color=config.AXIS_COLOR, size=12.5), title=None)
    if source:
        fig.add_annotation(text=source, xref="paper", yref="paper", x=0, y=-0.16,
                           showarrow=False, xanchor="left", yanchor="top",
                           font=dict(size=12, color=config.SOURCE_COLOR))
    return fig


def _add_end_labels(fig, color_map=None):
    """Gắn nhãn series ngay cuối đường (đặc trưng OWID), bỏ legend."""
    for tr in fig.data:
        ys = list(tr.y) if tr.y is not None else []
        xs = list(tr.x) if tr.x is not None else []
        idx = next((i for i in range(len(ys) - 1, -1, -1) if ys[i] is not None), None)
        if idx is None:
            continue
        col = (tr.line.color if tr.line and tr.line.color else None) \
            or (color_map or {}).get(tr.name)
        fig.add_annotation(x=xs[idx], y=ys[idx], text=f"  {tr.name}", showarrow=False,
                           xanchor="left", yanchor="middle",
                           font=dict(size=12.5, color=col))
    fig.update_layout(showlegend=False)


def line_trend(df, x="year", y="mean_score", color="code", color_map=None, labels=None,
               title=None, subtitle=None, source=config.SOURCE_DEFAULT,
               direct_labels=True, rangeslider=False, height=360,
               hovertemplate=None):
    """Line chart xu hướng theo năm. Mặc định gắn nhãn cuối đường thay cho legend.
    rangeslider=True bật thanh range zoom dưới trục thời gian.
    hovertemplate=None áp mẫu gọn mặc định; truyền chuỗi để ghi đè."""
    fig = px.line(df, x=x, y=y, color=color, color_discrete_map=color_map,
                  markers=True, labels=labels)
    fig.update_traces(line=dict(width=2.8), marker=dict(size=6))
    apply_owid(fig, title, subtitle, source, height=height)
    fig.update_layout(hovermode="x unified")
    # Áp hovertemplate mặc định gọn
    _ht = hovertemplate if hovertemplate is not None else "Năm %{x}: %{y:.2f} điểm<extra></extra>"
    fig.update_traces(hovertemplate=_ht)
    if rangeslider:
        fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.06))
    if direct_labels and color is not None:
        _add_end_labels(fig, color_map)
    return fig


def choropleth(df, geojson, value_col, name_col="province_vi", title=None, subtitle=None,
               source=config.SOURCE_DEFAULT, color_scale=None, range_color=None, height=420):
    """Choropleth 63 tỉnh. df cần `province_id` và `value_col`; join theo properties.province_id."""
    fig = px.choropleth(
        df, geojson=geojson, locations="province_id",
        featureidkey="properties.province_id", color=value_col,
        hover_name=name_col, color_continuous_scale=color_scale or config.SEQ_SCALE,
        range_color=range_color,
    )
    fig.update_geos(fitbounds="locations", visible=False)
    apply_owid(fig, title, subtitle, source, cartesian=False, height=height)
    fig.update_layout(margin=dict(l=0, r=0, t=48 if title else 8, b=40 if source else 0),
                      coloraxis_colorbar=dict(title="Điểm", thickness=12, len=0.7))
    return fig


def bar_ranking(df, value_col, name_col, title=None, subtitle=None,
                source=config.SOURCE_DEFAULT, color=config.ACCENT, ascending=False, height=360):
    """Horizontal bar xếp hạng (vd top/bottom tỉnh). Cao nhất ở trên cùng."""
    d = df.sort_values(value_col, ascending=ascending)
    fig = px.bar(d, x=value_col, y=name_col, orientation="h")
    fig.update_traces(marker_color=color)
    apply_owid(fig, title, subtitle, source, height=height)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig


def radar(categories, values, name=None, title=None, subtitle=None,
          source=config.SOURCE_DEFAULT, color=config.ACCENT, rng=(0, 10), height=380):
    """Radar 8 trục cho một đối tượng (vd một tỉnh). categories và values cùng độ dài."""
    cats = list(categories); vals = list(values)
    fig = go.Figure(go.Scatterpolar(
        r=vals + vals[:1], theta=cats + cats[:1], fill="toself",
        name=name, line_color=color))
    apply_owid(fig, title, subtitle, source, cartesian=False, height=height)
    fig.update_layout(polar=dict(radialaxis=dict(range=list(rng))),
                      showlegend=name is not None)
    return fig


def heatmap(matrix, title=None, subtitle=None, source=config.SOURCE_DEFAULT,
            color_scale=None, zmin=-1, zmax=1, height=380, text_auto=".2f"):
    """Heatmap, mặc định cho correlation matrix (giá trị -1..1).
    text_auto: định dạng số trong ô (vd '.2f'), False để ẩn số khi có nhiều cột."""
    fig = px.imshow(matrix, text_auto=text_auto,
                    color_continuous_scale=color_scale or config.DIV_SCALE,
                    zmin=zmin, zmax=zmax, aspect="auto")
    apply_owid(fig, title, subtitle, source, height=height)
    fig.update_xaxes(showgrid=False); fig.update_yaxes(showgrid=False)
    fig.update_traces(hovertemplate="%{y} · %{x}: %{z:.2f} điểm<extra></extra>")
    return fig


def diverging_bar(df, cat_col, value_col, title=None, subtitle=None,
                  source=config.SOURCE_DEFAULT,
                  pos_color="#4C6A9C", neg_color=config.ACCENT, height=360):
    """Bar ngang phân kỳ: dương màu pos_color, âm màu neg_color, sắp xếp theo giá trị.
    Dùng để hiển thị mức thay đổi (delta) theo từng lĩnh vực."""
    import plotly.graph_objects as go

    d = df.sort_values(value_col)
    colors = [pos_color if v >= 0 else neg_color for v in d[value_col]]
    fig = go.Figure(go.Bar(
        x=d[value_col],
        y=d[cat_col],
        orientation="h",
        marker_color=colors,
        hovertemplate="%{y}: %{x:+.2f}<extra></extra>",
    ))
    apply_owid(fig, title, subtitle, source, height=height)
    fig.update_layout(
        xaxis=dict(zeroline=True, zerolinecolor="#9CA3AF", zerolinewidth=1.5),
    )
    return fig


def boxplot(df, x, y, color=None, title=None, subtitle=None, source=config.SOURCE_DEFAULT,
            category_order=None, color_map=None, height=360):
    """Boxplot phân phối. category_order là thứ tự nhóm trên trục x."""
    orders = {x: category_order} if category_order else None
    fig = px.box(df, x=x, y=y, color=color, category_orders=orders,
                 color_discrete_map=color_map)
    apply_owid(fig, title, subtitle, source, height=height)
    return fig


def slopegraph(df, label_col, year_col, value_col, year_start, year_end, title=None,
               subtitle=None, source=config.SOURCE_DEFAULT, color="#9CA3AF", height=420):
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
    apply_owid(fig, title, subtitle, source, height=height)
    fig.update_layout(xaxis=dict(tickvals=[year_start, year_end]))
    return fig
