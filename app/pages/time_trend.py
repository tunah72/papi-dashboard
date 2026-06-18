"""Hướng 1 — Diễn biến chỉ số PAPI cấp tỉnh, 2011–2024.

Bố cục: control bar → KPI cards (card tổng có sparkline) → hàng A (đường tổng | cột COVID)
        → heatmap → hàng C (diverging bar tương tác | đường chi tiết lĩnh vực được chọn).
Không dùng mã D1..D8 trên giao diện; mọi tên hiển thị qua config.DIM_LABELS.
Tương tác: bấm một thanh trên diverging bar → đường chi tiết lĩnh vực đó cập nhật ngay.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from lib import config, data, charts, filters, layout
from analysis import trend

d = data.load_data()
L = config.DIM_LABELS

# ── Tiêu đề trang ──────────────────────────────────────────────────────────────────────
layout.page_header(
    "Diễn biến chỉ số PAPI cấp tỉnh, 2011–2024",
    "Đánh giá của người dân về hiệu quả quản trị và hành chính công, "
    "tổng hợp từ tám lĩnh vực nội dung.",
)

# ── Control bar ────────────────────────────────────────────────────────────────────────
with st.container(border=True):
    c1, c2 = st.columns([1.3, 1])
    with c1:
        mode = filters.scale_segmented("Phạm vi so sánh")
    cfg = config.scale_config(mode)
    with c2:
        y0, y1 = filters.year_range_inline(d, year_min=cfg["year_min"])

# ── Chuẩn bị dữ liệu ──────────────────────────────────────────────────────────────────
w = d["prov_year"]
nat = d["national"]
total_col = cfg["total_col"]

# Publish trạng thái filter để AI Assistant dùng làm ngữ cảnh
st.session_state["dash_context"] = {
    "page": "Diễn biến theo thời gian",
    "scale_mode": mode, "total_col": total_col,
    "dims": {c: config.DIM_LABELS[c] for c in cfg["dims"]},
    "year_range": [int(y0), int(y1)],
    "filters": {
        "scale_mode": mode,
        "total_col": total_col,
        "year_range": [int(y0), int(y1)],
        "dims": {c: config.DIM_LABELS[c] for c in cfg["dims"]},
    },
    "data_scope": {"tables": ["prov_year", "national"], "score_column": total_col},
}

tot = trend.total_by_year(w, total_col, y0, y1)
dim_nat = nat[nat.code.isin(cfg["dims"]) & nat.year.between(y0, y1)]

if tot.empty or dim_nat.empty:
    st.warning("Không có dữ liệu cho khoảng năm đã chọn.")
    st.stop()

# Delta từng lĩnh vực (năm đầu → năm cuối trong khoảng đã lọc)
delta = trend.dim_deltas(nat, cfg["dims"], y0, y1)
up, down = delta.idxmax(), delta.idxmin()

# Tóm tắt chuỗi điểm tổng (hai đầu mút, mức ròng, đỉnh/đáy)
s = trend.summarize_total(tot, total_col)
first, latest = s["first"], s["latest"]
v_first, v_latest, net = s["v_first"], s["v_latest"], s["net"]

# Nhãn KPI tổng phụ thuộc chế độ (không gọi total_papi_6dim là "Tổng PAPI")
if total_col == "total_papi_6dim":
    total_label = f"Tổng 6 lĩnh vực gốc {latest}"
else:
    total_label = f"Tổng PAPI {latest}"

# ── KPI cards (4 ô có viền) — card tổng có sparkline ─────────────────────────────────
layout.kpi_cards([
    {
        "label": total_label,
        "value": f"{v_latest:.1f}",
        "spark": list(tot[total_col]),   # sparkline diễn biến tổng qua các năm
    },
    {"label": f"Thay đổi so với {first}", "value": f"{net:+.1f}",
     "tone": "pos" if net >= 0 else "neg"},
    {"label": "Lĩnh vực tăng nhiều nhất", "value": L[up], "big": False,
     "delta": (f"{delta[up]:+.2f}", "pos" if delta[up] >= 0 else "neg")},
    {"label": "Lĩnh vực giảm nhiều nhất", "value": L[down], "big": False,
     "delta": (f"{delta[down]:+.2f}", "pos" if delta[down] >= 0 else "neg")},
])

# ── Hàng A: đường tổng (trái) | cột COVID (phải) ──────────────────────────────────────
col_left, col_right = st.columns([1.5, 1])

with col_left:
    with st.container(border=True):
        # Sinh tiêu đề từ dữ liệu (peak/dip lấy từ summarize_total ở trên)
        peak_year, peak_val, dip_val = s["peak_year"], s["peak_val"], s["dip_val"]
        if dip_val < min(v_first, v_latest) - 0.3:
            trend_word = "giảm rồi hồi phục một phần"
        elif abs(net) < 1:
            trend_word = "dao động trong biên độ hẹp"
        else:
            trend_word = "tăng" if net > 0 else "giảm"
        not_peak = v_latest < peak_val - 0.05 and peak_year != latest
        title1 = (
            f"Điểm tổng {trend_word}"
            + (f", chưa vượt mức năm {peak_year}" if not_peak else "")
        )
        unit = (
            "tổng sáu lĩnh vực gốc" if total_col == "total_papi_6dim"
            else "tổng tám lĩnh vực"
        )
        fig1 = charts.line_trend(
            tot, x="year", y=total_col, color=None, direct_labels=False,
            title=title1,
            subtitle=f"Trung bình 63 tỉnh, {unit}",
            source=f"{config.SOURCE_DEFAULT}. Tỉnh thiếu dữ liệu để trống, không nội suy.",
        )
        if y0 <= 2021 <= y1:
            fig1.add_vline(
                x=2021, line_dash="dash", line_color="#cbb89a",
                annotation_text="COVID-19", annotation_position="top",
            )
        # Annotation giá trị điểm mới nhất tại điểm cuối
        fig1.add_annotation(
            x=latest, y=v_latest,
            text=f"<b>{v_latest:.1f}</b>",
            showarrow=False,
            xanchor="left", yanchor="middle",
            xshift=10,
            font=dict(size=12, color=config.TITLE_COLOR),
        )
        layout.chart(fig1)
        layout.ai_explain_button(
            "Diễn biến tổng điểm",
            context={"data_scope": {"table": "prov_year", "score_column": total_col, "chart": "line_trend"}},
            disabled=tot.empty,
        )

with col_right:
    with st.container(border=True):
        # Biểu đồ cột nhóm COVID — D6 và D8 (so sánh trước/sau đại dịch)
        cmp = trend.compare_periods(nat, ["D6", "D8"], [2018, 2019], [2021, 2022])
        dl = {code: cmp[code]["diff"] for code in cmp}
        rows = []
        for code in ["D6", "D8"]:
            rows += [
                {"Lĩnh vực": L[code], "Giai đoạn": "2018–2019", "Điểm": cmp[code]["before"]},
                {"Lĩnh vực": L[code], "Giai đoạn": "2021–2022", "Điểm": cmp[code]["after"]},
            ]
        covid = pd.DataFrame(rows)

        # Kiểm tra khoảng năm có phủ 2018–2022 không
        has_covid_range = (y0 <= 2019) and (y1 >= 2021)
        if not has_covid_range:
            st.caption(
                "Chọn khoảng năm bao gồm 2018–2022 để xem so sánh "
                "trước và sau đại dịch COVID-19."
            )
        elif covid["Điểm"].notna().any():
            title3 = (
                f"Quản trị điện tử {trend.classify_change(dl['D8'])}; "
                f"cung ứng dịch vụ công {trend.classify_change(dl['D6'])} sau đại dịch"
            )
            fig3 = px.bar(
                covid, x="Lĩnh vực", y="Điểm", color="Giai đoạn", barmode="group",
                color_discrete_sequence=["#9DB4D2", config.ACCENT],
            )
            charts.apply_owid(
                fig3, title=title3,
                subtitle="Trung bình 63 tỉnh, 2018–2019 so với 2021–2022",
            )
            fig3.update_layout(bargap=0.5, bargroupgap=0.12)
            layout.chart(fig3)
        else:
            st.caption("Không đủ dữ liệu để vẽ biểu đồ COVID.")

# ── Heatmap toàn cảnh (full width) ────────────────────────────────────────────────────
with st.container(border=True):
    nat_filt = nat[nat.code.isin(cfg["dims"]) & nat.year.between(y0, y1)].copy()
    nat_filt["Lĩnh vực"] = nat_filt["code"].map(L)
    if not nat_filt.empty:
        matrix = nat_filt.pivot_table(
            index="Lĩnh vực", columns="year", values="mean_score", observed=True
        )
        # Xác định zmin/zmax hợp lý từ dữ liệu (làm tròn 0.5 điểm)
        z_all = nat_filt["mean_score"].dropna()
        z_lo = max(0.0, (z_all.min() // 0.5) * 0.5)
        z_hi = ((z_all.max() // 0.5 + 1)) * 0.5
        # Luôn hiển thị giá trị trong ô (1 chữ số thập phân cho gọn, đọc được cả 6 và 8 lĩnh vực)
        text_fmt = ".1f"
        fig_hm = charts.heatmap(
            matrix,
            title="Toàn cảnh các lĩnh vực qua các năm",
            subtitle="Màu đậm là điểm cao · trung bình 63 tỉnh",
            color_scale=config.SEQ_SCALE,
            zmin=z_lo,
            zmax=z_hi,
            height=max(320, 45 * len(matrix) + 100),
            text_auto=text_fmt,
        )
        layout.chart(fig_hm)
    else:
        st.caption("Không đủ dữ liệu để vẽ heatmap.")

# ── Hàng C: diverging bar tương tác (trái) | đường chi tiết (phải) ───────────────────
# Chuẩn bị dữ liệu diverging bar
color_map = dict(zip(d["dim_ind"].code, d["dim_ind"].color))
div_rows = []
for code in cfg["dims"]:
    g = dim_nat[dim_nat.code == code].sort_values("year")
    if len(g) >= 2:
        d0_series = g[g.year == g.year.min()].mean_score.values
        d1_series = g[g.year == g.year.max()].mean_score.values
        
        if len(d0_series) > 0 and len(d1_series) > 0:
            d0 = d0_series[0]
            d1 = d1_series[0]
            if pd.notna(d0) and pd.notna(d1):
                div_rows.append({"Lĩnh vực": L[code], "Thay đổi": d1 - d0, "_code": code})

col_c_left, col_c_right = st.columns([1, 1])

if div_rows:
    div_df = pd.DataFrame(div_rows)
    fig_div = charts.diverging_bar(
        div_df,
        cat_col="Lĩnh vực",
        value_col="Thay đổi",
        title=f"Mức thay đổi từng lĩnh vực, {first}–{latest}",
        subtitle=f"Xanh = tăng, đỏ = giảm · trung bình 63 tỉnh, {first} so với {latest}",
        height=max(300, 44 * len(div_df) + 100),
    )

    with col_c_left:
        with st.container(border=True):
            # Dùng st.plotly_chart trực tiếp (không qua layout.chart) để hứng on_select
            ev = st.plotly_chart(
                fig_div,
                on_select="rerun",
                selection_mode="points",
                key="h1_divbar",
                config={"displayModeBar": False},
                width="stretch",
            )

    # Xác định lĩnh vực được chọn (mặc định = lĩnh vực tăng mạnh nhất)
    sel_name = L[up]
    try:
        pts = ev.selection.points          # ev là giá trị trả về của st.plotly_chart
        if pts:
            sel_name = pts[0]["y"]         # diverging bar ngang: category nằm ở trục y
    except Exception:
        pass

    with col_c_right:
        with st.container(border=True):
            st.caption("Bấm một thanh ở biểu đồ bên trái để xem chi tiết lĩnh vực.")
            # Tra code từ tên lĩnh vực được chọn
            label_to_code = {v: k for k, v in L.items()}
            sel_code = label_to_code.get(sel_name)
            if sel_code:
                sub = dim_nat[dim_nat.code == sel_code].copy()
                if not sub.empty:
                    # Lấy giá trị cẩn thận, tránh lỗi IndexError
                    d0_series = sub.loc[sub.year == sub.year.min(), "mean_score"].values
                    d1_series = sub.loc[sub.year == sub.year.max(), "mean_score"].values
                    if len(d0_series) > 0 and len(d1_series) > 0:
                        d0_val = d0_series[0]
                        d1_val = d1_series[0]
                        delta_chosen = d1_val - d0_val
                        verb = trend.classify_change(delta_chosen)
                        abs_delta = abs(delta_chosen)
                        # Tiêu đề data-driven
                        detail_title = f"{sel_name} {verb} {abs_delta:.2f} điểm, {first}–{latest}"
                        fig_drill = charts.line_trend(
                            sub, x="year", y="mean_score", color=None, direct_labels=False,
                            title=detail_title,
                            subtitle="Trung bình 63 tỉnh",
                            source=config.SOURCE_DEFAULT,
                            height=max(300, 44 * len(div_df) + 100),
                        )
                        # Tô màu đúng lĩnh vực
                        fig_drill.update_traces(
                            line=dict(color=color_map.get(sel_code, config.ACCENT))
                        )
                        # Vline COVID nếu khoảng năm phủ 2021
                        if y0 <= 2021 <= y1:
                            fig_drill.add_vline(
                                x=2021, line_dash="dash", line_color="#cbb89a",
                                annotation_text="COVID-19", annotation_position="top",
                            )
                        layout.chart(fig_drill)
                    else:
                        st.caption("Thiếu dữ liệu năm đầu/năm cuối để tính mức thay đổi.")
                else:
                    st.caption("Không có dữ liệu cho lĩnh vực này trong khoảng năm đã chọn.")
            else:
                st.caption("Chọn một lĩnh vực từ biểu đồ bên trái.")
else:
    with col_c_left:
        st.caption("Không đủ dữ liệu để tính mức thay đổi.")
    with col_c_right:
        st.caption("Không có dữ liệu để hiển thị.")
