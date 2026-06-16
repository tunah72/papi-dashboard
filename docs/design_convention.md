# Design convention — Dashboard PAPI (phong cách Our World in Data)

Tài liệu chốt quy ước thiết kế để bốn trang phân tích trông như một sản phẩm. Phần lớn
quy ước được **enforce bằng code** trong `app/lib/` và `.streamlit/config.toml`, nên thành
viên chủ yếu chỉ thêm nội dung, không tự đặt style.

## 1. Nguyên tắc
- Dashboard **thiết kế tổng quát**, không in câu hỏi lên màn hình. Câu hỏi định hướng
  (xem `dashboard_plan.md`) chỉ để dẫn dắt phân tích; người xem **quan sát biểu đồ để tự trả lời**.
- "Đẹp" = phục vụ đọc dữ liệu nhanh và trung thực, không trang trí.
- Ít biểu đồ nhưng to và rõ; nhiều khoảng trắng.

## 2. Phong cách OWID đã áp
- **Direct labeling**: line chart gắn nhãn series ngay cuối đường, bỏ legend box.
- **Bộ tiêu đề ba phần cho mỗi biểu đồ**: tiêu đề khẳng định (kết luận) → phụ đề mô tả (xám)
  → dòng nguồn ở chân.
- **Lưới tối giản**: chỉ gridline ngang nhạt (`#ECECEC`), không khung viền, không lưới dọc.
- **Nhận xét = văn xuôi** đặt dưới biểu đồ (không hộp callout).
- **Headline serif, body và biểu đồ sans.** Accent vermillion `#B13507`.
- Luôn ghi nguồn + lưu ý dữ liệu thiếu ở chân biểu đồ.

## 3. Hệ màu (đã vào code)
- **8 trục**: `dim_indicator.csv` (single source). D1 `#4C6A9C`, D2 `#E0A23B`, D3 `#578145`,
  D4 `#B13507`, D5 `#6D4C9C`, D6 `#2C8C99`, D7 `#8C6D3F`, D8 `#A63D57`. Một trục **một màu cố định** ở mọi trang.
- **6 vùng**: `config.REGION_COLORS`. **4 tier**: `config.TIER_COLORS`.
- **Sequential** (điểm thấp→cao, choropleth/bar tổng): `config.SEQ_SCALE`.
- **Diverging** (biến động giảm↔tăng): `config.DIV_SCALE`.

## 4. Khung trang (mọi trang theo)
```
Header chung + toggle scale (hạ tầng)        # app/main.py, không sửa
Sidebar filter (trái)                        # filters.* — mỗi trang chọn filter cần
layout.page_header(title, desc)              # tiêu đề serif + mô tả 1 dòng
layout.kpi_strip([...])                      # hàng số liệu nổi bật
layout.section_header("Chủ đề")              # section trung tính theo nội dung
layout.chart(charts.X(...), note_text="...") # biểu đồ đã style + nhận xét
... lặp lại theo số section ...
```

## 5. Hợp đồng cho thành viên
Một trang phân tích cơ bản chỉ cần:
1. `data.load_data()` và chọn filter qua `filters.*`.
2. Với mỗi chủ đề: `layout.section_header(...)` rồi `layout.chart(charts.<loại>(df, title=, subtitle=, source=), note_text=)`.
3. Viết tiêu đề (kết luận), phụ đề, và nhận xét.

Thành viên **được tự thêm biểu đồ** phù hợp trang của mình: ưu tiên dùng lại `charts.*`; nếu cần loại
mới thì dựng trong page (one-off) hoặc thêm hàm mới vào `charts.py` (chỉ thêm, không sửa hàm có sẵn).
Mọi biểu đồ tự dựng **phải gọi** `charts.apply_owid(fig, title=, subtitle=, source=)` để giữ đồng bộ
style OWID.

Không sửa: chữ ký hàm có sẵn trong `app/lib/`, `app/main.py`, theme `config.toml`, màu trong
`dim_indicator.csv` (tránh vỡ trang của người khác).

## 6. Quy ước nội dung và văn phong
- **Title trang mô tả nội dung cụ thể** (chủ đề + khoảng thời gian), không chung chung. Nhãn menu
  có thể ngắn, nhưng tiêu đề trên trang phải cho người xem hình dung nội dung.
- **Tiêu đề biểu đồ = kết luận đo lường, bám số liệu** (dùng động từ trung lập tăng/giảm/không đổi).
  Tiêu đề phải khớp với biểu đồ; nếu được, sinh tự động từ dữ liệu để không lệch.
- **Không hiển thị mã viết tắt** trên UI (không "D1", "D6"). Dùng tên đầy đủ qua `config.DIM_LABELS`.
  Gọi "lĩnh vực" (lần đầu có thể ghi "lĩnh vực nội dung") thay cho "trục".
- **Văn phong khoa học, trung tính**: không hook cảm tính, không in hoa nhấn mạnh, accent đỏ chỉ cho
  phần tử điều khiển (không cho câu chữ). Để biểu đồ truyền tải, hạn chế văn xuôi.
- **Số**: điểm 2 chữ số thập phân; tổng 1 chữ số. Đơn vị ghi ở phụ đề (thang 1–10, 6–60, 8–80).
- **Dữ liệu thiếu**: để trống, không nội suy; nêu ở dòng nguồn.
- **Nhãn điểm tổng theo chế độ**: khi dùng 8 lĩnh vực → "Tổng PAPI {năm}"; khi dùng 6 lĩnh vực gốc
  → "Tổng 6 lĩnh vực gốc {năm}" — TUYỆT ĐỐI không gọi `total_papi_6dim` là "Tổng PAPI" vì giá trị
  (~36 điểm) không phải Tổng PAPI chính thức (~43 điểm).
- **Mốc 6/8 lĩnh vực**: bộ chọn gọi là "Phạm vi so sánh" (không gọi "Thước đo"). Mặc định 6 lĩnh vực
  gốc (`total_papi_6dim`, liền mạch 2011–2024); không so tổng vắt qua mốc 2018.
- **Bản chất dữ liệu**: PAPI đo **đánh giá chủ quan của người dân** về hiệu quả quản trị và hành chính
  công. Phụ đề biểu đồ nên nhắc rõ "điểm do người dân đánh giá; cao hơn = hài lòng hơn". Ghi "trung
  bình 63 tỉnh" thay cho "trung bình cả nước" khi dùng aggregation cấp tỉnh.

## 6b. Vị trí filter và tương tác (đặt theo phạm vi tác động)
- **Page-level** (ảnh hưởng cả trang: thước đo, khoảng năm) → top control bar `st.container(border=True)`
  với `filters.scale_segmented()` + `filters.year_range_inline()`. Không giấu trong sidebar.
- **Chart-level** (chỉ ảnh hưởng một biểu đồ: chọn lĩnh vực) → đặt ngay trên biểu đồ đó bằng
  `filters.dimension_pills()`.
- **Điểm dữ liệu** (hover, range zoom) → trong biểu đồ: `rangeslider=True`, `hovermode="x unified"`.
- **Sidebar** → chỉ giữ điều hướng giữa các trang.

## 7. Tương tác nâng cao (Hướng 1)

- **Click-to-drill qua diverging bar:** `st.plotly_chart(fig, on_select="rerun", selection_mode="points", key=...)` trả về
  object có `.selection.points`. Guard bằng `try/except` để trạng thái mặc định (không có click) không lỗi.
  Diverging bar ngang → tên lĩnh vực lấy từ `pts[0]["y"]`. Biểu đồ tương tác này gọi `st.plotly_chart` trực tiếp,
  **không qua `layout.chart`** (vì cần hứng giá trị trả về).
- **Sparkline KPI:** `layout.kpi_cards` chấp nhận khóa `spark` (list số) trong item. Nếu có, render sparkline SVG nhỏ
  (cao 22 px, `preserveAspectRatio='none'`) thay cho ô delta trống. Card tổng ở Hướng 1 dùng tính năng này.
- **Hovertemplate chuẩn:** `charts.line_trend` có tham số `hovertemplate` (default = `"Năm %{x}: %{y:.2f} điểm<extra></extra>"`).
  `charts.heatmap` áp `"%{y} · %{x}: %{z:.2f} điểm<extra></extra>"` tự động. Mọi biểu đồ đều có hover gọn, tiếng Việt.
- **Annotation điểm cuối:** đường tổng ở Hàng A dùng `fig.add_annotation` để hiện giá trị mới nhất tại điểm cuối chuỗi.

## 8. Tham chiếu
Trang mẫu hoàn chỉnh: `app/pages/time_trend.py` (Hướng 1) và `app/pages/overview.py`.
Ba thành viên còn lại copy khung từ đây.
