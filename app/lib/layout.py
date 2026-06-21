"""Helper bố cục dùng chung cho mọi trang — phong cách Our World in Data.

Mục tiêu: trang phân tích của thành viên chỉ còn nội dung. Header, section, KPI, block
nhận xét, và cách hiển thị biểu đồ đều gọi từ đây nên bốn trang trông như một sản phẩm.

Dùng điển hình trong một trang:
    from lib import layout, charts, data, filters
    layout.page_header("Diễn biến theo thời gian", "Mô tả ngắn một dòng.")
    layout.kpi_strip([("Tổng PAPI 2024", "39,3"), ("So với 2011", "+2,3")])
    layout.section_header("Xu hướng tổng thể")
    layout.chart(charts.line_trend(df, title="...", subtitle="...", source="..."),
                 note="Nhận xét về biểu đồ.")
"""
import streamlit as st


def page_header(title, desc=None):
    """Tiêu đề trang (serif theo theme) + mô tả một dòng."""
    st.title(title)
    if desc:
        st.caption(desc)


def section_header(title, desc=None):
    """Mở một section nội dung. Trung tính theo chủ đề, không in câu hỏi lên dashboard."""
    st.markdown(f"#### {title}")
    if desc:
        st.caption(desc)


def kpi_strip(items):
    """Hàng số liệu nổi bật. items: list các tuple (label, value) hoặc (label, value, delta)."""
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        label, value = item[0], item[1]
        delta = item[2] if len(item) > 2 else None
        col.metric(label, value, delta)


_KPI_TONE = {"neutral": "var(--color-text-primary)", "pos": "#2F7D4F", "neg": "#B13507"}
_KPI_PILL = {"pos": ("#E6F1EA", "#2F7D4F", "↑"), "neg": ("#FBEAEA", "#B13507", "↓")}


def _spark_svg(values):
    """Tạo sparkline SVG nhỏ từ list số. Trả về chuỗi SVG inline."""
    vals = [v for v in values if v is not None]
    n = len(vals)
    if n < 2:
        return ""
    lo, hi = min(vals), max(vals)
    # Guard hi == lo (tất cả bằng nhau)
    rng = hi - lo if hi != lo else 1.0
    pts = " ".join(
        f"{i / (n - 1) * 100:.1f},{22 - (v - lo) / rng * 20:.1f}"
        for i, v in enumerate(vals)
    )
    return (
        "<svg viewBox='0 0 100 22' width='100%' height='22'"
        " preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg'"
        " style='display:block;margin-top:4px'>"
        f"<polyline points='{pts}' fill='none' stroke='#4C6A9C' stroke-width='1.5'"
        " stroke-linejoin='round' stroke-linecap='round'/>"
        "</svg>"
    )


def kpi_cards(items):
    """Hàng KPI, mỗi ô là card viền cao bằng nhau. Mỗi item là dict:
      label: nhãn nhỏ phía trên.
      value: giá trị (số hoặc tên lĩnh vực).
      tone:  'neutral' | 'pos' | 'neg' — màu của value (mặc định neutral).
      big:   True = value cỡ lớn (số); False = cỡ vừa, xuống dòng được (tên dài).
      delta: tuple (text, 'pos'|'neg') — pill màu dưới value, hoặc None.
      spark: list số — nếu có, render sparkline SVG nhỏ thay cho ô trống delta.
    """
    cols = st.columns(len(items))
    for col, it in zip(cols, items):
        vsize = "26px" if it.get("big", True) else "16px"
        vcolor = _KPI_TONE[it.get("tone", "neutral")]
        delta = it.get("delta")
        spark = it.get("spark")
        if delta:
            bg, fg, arrow = _KPI_PILL[delta[1]]
            bottom_html = (f"<div style='margin-top:6px'><span style='font-size:11.5px;"
                           f"padding:1px 8px;border-radius:10px;background:{bg};color:{fg}'>"
                           f"{arrow} {delta[0]}</span></div>")
        elif spark:
            # Sparkline SVG thay cho ô delta trống, cùng chiều cao ~26px
            svg = _spark_svg(spark)
            bottom_html = f"<div style='margin-top:4px;height:22px'>{svg}</div>"
        else:
            bottom_html = "<div style='margin-top:6px;height:19px'></div>"
        html = (
            f"<div style='min-height:84px'>"
            f"<div style='font-size:12.5px;color:var(--color-text-secondary);margin-bottom:4px'>{it['label']}</div>"
            f"<div style='font-size:{vsize};font-weight:500;line-height:1.2;color:{vcolor}'>{it['value']}</div>"
            f"{bottom_html}</div>"
        )
        with col:
            with st.container(border=True):
                st.markdown(html, unsafe_allow_html=True)


def note(text):
    """Block nhận xét dạng văn xuôi đặt dưới biểu đồ (editorial OWID)."""
    st.markdown(
        f"<div style='color:#5f5f5f;font-size:0.92rem;line-height:1.6;margin:0.1rem 0 0.4rem'>"
        f"<strong>Nhận xét.</strong> {text}</div>",
        unsafe_allow_html=True,
    )


def chart(fig, note_text=None):
    """Hiển thị một figure đã style sẵn (ẩn thanh công cụ plotly), kèm nhận xét tuỳ chọn."""
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    if note_text:
        note(note_text)


def ai_explain_button(chart_name, description="phân tích giúp tôi các điểm nổi bật", context=None, disabled=False):
    """Nút bấm nhỏ dưới biểu đồ để chuyển sang AI Assistant với câu hỏi mẫu."""
    key = "ai_btn_" + "".join(ch if ch.isalnum() else "_" for ch in chart_name)
    if st.button(f"Giải thích {chart_name}", key=key, disabled=disabled):
        chart_context = dict(st.session_state.get("dash_context") or {})
        if context:
            chart_context.update(context)
        chart_context["chart_id"] = chart_name
        st.session_state["dash_context"] = chart_context
        st.session_state["ai_seed"] = f"Hãy {description} của biểu đồ '{chart_name}' dựa trên ngữ cảnh hiện tại."
        st.switch_page("pages/ai_assistant.py")
