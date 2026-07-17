"""Helper bố cục dùng chung cho mọi trang — phong cách editorial civic data.

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
from html import escape

import streamlit as st


def inject_global_styles():
    """Nạp design tokens toàn cục một lần từ entry point Streamlit."""
    st.markdown(
        """
        <style>
          :root {
            --papi-ink: #18212D;
            --papi-muted: #5B6572;
            --papi-page: #F8F5EF;
            --papi-surface: #FFFDFC;
            --papi-border: #DED8CE;
            --papi-accent: #A8431F;
            --papi-accent-soft: #F6E5DD;
          }

          html { scroll-behavior: smooth; }
          .stApp { background: var(--papi-page); color: var(--papi-ink); }
          [data-testid="stAppViewContainer"] { background: var(--papi-page); }
          [data-testid="stMainBlockContainer"] {
            max-width: 82.5rem;
            padding: 2.25rem 3rem 4.5rem;
          }
          [data-testid="stSidebar"] {
            background: #F1ECE4;
            border-right: 1px solid var(--papi-border);
          }
          [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            padding-top: 1.2rem;
          }
          [data-testid="stSidebar"] a,
          [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
            border-radius: .45rem;
            color: var(--papi-ink);
            font-size: .97rem;
            font-weight: 520;
            margin: .13rem .35rem;
            min-height: 2.55rem;
            transition: background-color 160ms ease, color 160ms ease, transform 160ms ease;
          }
          [data-testid="stSidebar"] a:hover,
          [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
            background: #E8E0D6;
            color: var(--papi-accent);
            transform: translateX(2px);
          }
          [data-testid="stSidebar"] [aria-current="page"] {
            background: var(--papi-accent-soft);
            color: var(--papi-accent);
            font-weight: 700;
          }
          [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--papi-border);
            background: rgba(255, 253, 252, .76);
            box-shadow: 0 1px 0 rgba(24, 33, 45, .025);
          }
          [data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 1.1rem;
            border-bottom-color: var(--papi-border);
          }
          [data-testid="stTabs"] button[role="tab"] {
            color: var(--papi-muted);
            font-size: .93rem;
            font-weight: 650;
            padding: .45rem 0;
          }
          [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: var(--papi-accent);
          }
          [data-testid="stButton"] > button,
          [data-testid="stPageLink"] > a {
            border-radius: .42rem;
            font-weight: 650;
            min-height: 2.5rem;
            transition: background-color 160ms ease, border-color 160ms ease, transform 160ms ease;
          }
          [data-testid="stButton"] > button:hover,
          [data-testid="stPageLink"] > a:hover {
            transform: translateY(-1px);
          }
          button:focus-visible, a:focus-visible, input:focus-visible,
          [role="tab"]:focus-visible {
            outline: 3px solid rgba(168, 67, 31, .34) !important;
            outline-offset: 2px !important;
          }
          .papi-page-header { margin: .2rem 0 1.6rem; max-width: 70rem; }
          .papi-eyebrow {
            color: var(--papi-accent); font-size: .75rem; font-weight: 750;
            letter-spacing: .12em; margin-bottom: .6rem; text-transform: uppercase;
          }
          .papi-page-title {
            color: var(--papi-ink); font-family: Iowan Old Style, Palatino Linotype, Book Antiqua, Georgia, serif;
            font-size: clamp(2.2rem, 3.5vw, 3.15rem); font-weight: 700;
            letter-spacing: -.035em; line-height: 1.05; margin: 0; text-wrap: balance;
          }
          .papi-page-desc { color: var(--papi-muted); font-size: 1.04rem; line-height: 1.58; margin: .78rem 0 0; max-width: 66ch; }
          .papi-section-header { border-top: 1px solid var(--papi-border); margin: 2.6rem 0 1.2rem; padding-top: 1.1rem; }
          .papi-section-title {
            color: var(--papi-ink); font-family: Iowan Old Style, Palatino Linotype, Book Antiqua, Georgia, serif;
            font-size: clamp(1.45rem, 2.1vw, 1.85rem); letter-spacing: -.02em; line-height: 1.14; margin: 0;
          }
          .papi-section-desc { color: var(--papi-muted); font-size: .97rem; line-height: 1.55; margin: .35rem 0 0; }
          .papi-panel-heading { color: var(--papi-ink); font-family: Iowan Old Style, Palatino Linotype, Book Antiqua, Georgia, serif; font-size: 1.35rem; font-weight: 700; letter-spacing: -.015em; line-height: 1.18; margin: .1rem 0 .2rem; }
          .papi-panel-desc { color: var(--papi-muted); font-size: .9rem; line-height: 1.5; margin: 0 0 .85rem; }
          .papi-kpi-card {
            background: var(--papi-surface); border: 1px solid var(--papi-border); border-radius: .65rem;
            min-height: 7.4rem; padding: 1rem 1.05rem .9rem;
          }
          .papi-kpi-label { color: var(--papi-muted); font-size: .84rem; font-weight: 650; line-height: 1.35; margin-bottom: .48rem; }
          .papi-kpi-value { color: var(--papi-ink); font-size: 2rem; font-weight: 680; font-variant-numeric: tabular-nums; letter-spacing: -.03em; line-height: 1.05; }
          .papi-kpi-value--text { font-size: 1.1rem; font-weight: 700; letter-spacing: -.015em; line-height: 1.3; }
          .papi-kpi-footer { min-height: 1.35rem; margin-top: .55rem; }
          .papi-delta { border-radius: .26rem; display: inline-block; font-size: .77rem; font-weight: 700; padding: .17rem .48rem; }
          .papi-note { color: var(--papi-muted); font-size: .96rem; line-height: 1.62; margin: .6rem 0 .15rem; max-width: 78ch; }
          .papi-note strong { color: var(--papi-ink); }
          .papi-insight {
            background: linear-gradient(90deg, #F4E7DF 0%, rgba(244, 231, 223, .35) 70%, rgba(244, 231, 223, 0) 100%);
            border-left: 4px solid var(--papi-accent); margin: 1.35rem 0 1.8rem; padding: 1rem 1.15rem 1.05rem;
          }
          .papi-insight-label { color: var(--papi-accent); font-size: .75rem; font-weight: 750; letter-spacing: .1em; text-transform: uppercase; }
          .papi-insight-title { color: var(--papi-ink); font-family: Iowan Old Style, Palatino Linotype, Book Antiqua, Georgia, serif; font-size: 1.32rem; font-weight: 700; letter-spacing: -.015em; line-height: 1.2; margin-top: .32rem; }
          .papi-insight-body { color: var(--papi-muted); font-size: .96rem; line-height: 1.55; margin-top: .35rem; max-width: 76ch; }
          .papi-story-card { border-top: 2px solid var(--papi-ink); min-height: 10.5rem; padding: .85rem 0 .15rem; }
          .papi-story-index { color: var(--papi-accent); font-size: .78rem; font-weight: 750; letter-spacing: .1em; }
          .papi-story-title { color: var(--papi-ink); font-family: Iowan Old Style, Palatino Linotype, Book Antiqua, Georgia, serif; font-size: 1.25rem; font-weight: 700; line-height: 1.16; margin: .45rem 0; }
          .papi-story-desc { color: var(--papi-muted); font-size: .92rem; line-height: 1.5; margin-bottom: .55rem; }
          .papi-story-status { color: var(--papi-accent); font-size: .78rem; font-weight: 700; }
          @media (max-width: 56rem) {
            [data-testid="stMainBlockContainer"] { padding: 1.4rem 1.05rem 3.2rem; }
            .papi-page-title { font-size: 2.2rem; }
            .papi-kpi-card { min-height: auto; margin-bottom: .65rem; }
          }
          @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, desc=None, eyebrow="PAPI Dashboard"):
    """Tiêu đề lớn, có hierarchy rõ để đọc tốt trên màn hình trình chiếu."""
    desc_html = f"<p class='papi-page-desc'>{escape(desc)}</p>" if desc else ""
    st.markdown(
        f"<header class='papi-page-header'><div class='papi-eyebrow'>{escape(eyebrow)}</div>"
        f"<h1 class='papi-page-title'>{escape(title)}</h1>{desc_html}</header>",
        unsafe_allow_html=True,
    )


def section_header(title, desc=None):
    """Mở section với hierarchy rõ, không biến nội dung thành callout rời rạc."""
    desc_html = f"<p class='papi-section-desc'>{escape(desc)}</p>" if desc else ""
    st.markdown(
        f"<section class='papi-section-header'><h2 class='papi-section-title'>{escape(title)}</h2>{desc_html}</section>",
        unsafe_allow_html=True,
    )


def panel_heading(title, desc=None):
    """Tiêu đề gọn trong card/chart, không tạo thêm đường phân cách section."""
    desc_html = f"<p class='papi-panel-desc'>{escape(desc)}</p>" if desc else ""
    st.markdown(
        f"<div class='papi-panel-heading'>{escape(title)}</div>{desc_html}",
        unsafe_allow_html=True,
    )


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
        vclass = "" if it.get("big", True) else " papi-kpi-value--text"
        vcolor = _KPI_TONE[it.get("tone", "neutral")]
        delta = it.get("delta")
        spark = it.get("spark")
        if delta:
            bg, fg, arrow = _KPI_PILL[delta[1]]
            bottom_html = (f"<div class='papi-kpi-footer'><span class='papi-delta' style='background:{bg};color:{fg}'>"
                           f"{arrow} {escape(str(delta[0]))}</span></div>")
        elif spark:
            # Sparkline SVG thay cho ô delta trống, cùng chiều cao ~26px
            svg = _spark_svg(spark)
            bottom_html = f"<div class='papi-kpi-footer'>{svg}</div>"
        else:
            bottom_html = "<div class='papi-kpi-footer'></div>"
        html = (
            f"<article class='papi-kpi-card'>"
            f"<div class='papi-kpi-label'>{escape(str(it['label']))}</div>"
            f"<div class='papi-kpi-value{vclass}' style='color:{vcolor}'>{escape(str(it['value']))}</div>"
            f"{bottom_html}</article>"
        )
        with col:
            st.markdown(html, unsafe_allow_html=True)


def note(text):
    """Block nhận xét dạng văn xuôi đặt dưới biểu đồ (editorial OWID)."""
    st.markdown(
        f"<div class='papi-note'><strong>Nhận xét.</strong> {escape(text)}</div>",
        unsafe_allow_html=True,
    )


def insight(title, body, label="Điểm đáng chú ý"):
    """Dải insight dùng cho kết luận có số liệu, không thay thế biểu đồ bằng văn xuôi."""
    st.markdown(
        f"<aside class='papi-insight'><div class='papi-insight-label'>{escape(label)}</div>"
        f"<div class='papi-insight-title'>{escape(title)}</div>"
        f"<div class='papi-insight-body'>{escape(body)}</div></aside>",
        unsafe_allow_html=True,
    )


def story_card(index, title, desc, status):
    """Nội dung dẫn hướng cho mỗi hướng phân tích trên Overview."""
    st.markdown(
        f"<article class='papi-story-card'><div class='papi-story-index'>{escape(index)}</div>"
        f"<div class='papi-story-title'>{escape(title)}</div>"
        f"<div class='papi-story-desc'>{escape(desc)}</div>"
        f"<div class='papi-story-status'>{escape(status)}</div></article>",
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
