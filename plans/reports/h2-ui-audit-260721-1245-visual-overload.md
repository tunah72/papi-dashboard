# Audit H2 UI — tải nhận thức và lỗi hiển thị

**Ngày audit:** 2026-07-21
**Phạm vi:** `app/pages/provincial.py`, `app/lib/layout.py`
**Phương pháp:** `/ak:web-design-guidelines`, Chrome DevTools MCP probe, Streamlit AppTest và đọc source.

## Giới hạn công cụ

Chrome DevTools MCP không khởi động được vì môi trường thiếu X server
(`Missing X server to start the headful browser`). `agent-browser` cũng không
có trong môi trường. Vì vậy không có ảnh/DOM Chrome để xác nhận pixel-level
hay breakpoint thực tế. Các phát hiện được đánh dấu **code-verified** hoặc
**visual-confirmation-needed** tương ứng.

## Runtime đã xác minh

- H2 AppTest boot thành công, không exception.
- Trang mặc định render 8 Plotly charts, 10 captions, 2 select sliders, 2
  selectboxes và 71 phần tử nội dung.
- Con số này xác nhận single-page dashboard có tải thông tin quá cao.

## Phát hiện cần sửa trước

### P0 — Slopegraph 61 đường là biểu đồ spaghetti (**code-verified**)

`app/pages/provincial.py:245-262` đưa tất cả tỉnh đủ hai quan sát vào một
slopegraph cao 560 px. Khoảng 61 đường chồng chéo, không direct label/filter và
không làm rõ tỉnh thay đổi đáng chú ý.

**Khuyến nghị:** chỉ giữ top/bottom 5–7 theo `abs(delta)`; thêm chọn vùng/tỉnh
để xem chi tiết; phần còn lại dùng bảng hoặc histogram delta.

### P0 — Drill-down nằm sau bảy biểu đồ (**code-verified**)

Click map thay đổi `h2_region`/`h2_province` ở `:75-100`, nhưng ranking/radar
chỉ xuất hiện ở `:264-330`, sau map, KPI, boxplot, mean bar, top/bottom,
outlier và slopegraph. Người dùng click map phải cuộn rất xa mới thấy phản hồi.

**Khuyến nghị:** đưa selected-province summary/ranking/radar ngay sau map hoặc
dùng tab/expander “Tỉnh được chọn”.

### P1 — Chart lặp câu hỏi, không có thứ bậc kể chuyện (**code-verified**)

Map (`:59-73`), boxplot (`:143-173`), regional mean bar (`:175-201`), top 10
(`:211-219`), bottom 10 (`:220-228`), ranking vùng (`:270-294`) và KPI (`:124-133`)
đều tái diễn so sánh cao/thấp cho cùng snapshot năm.

**Khuyến nghị:**

1. Overview: KPI + map.
2. Compare: chỉ một trong boxplot hoặc regional mean bar.
3. Drill-down: ranking/radar tỉnh chọn.
4. Khám phá thêm: outlier + delta trong expander/tabs.

### P1 — Ba cột 450 px dễ nén nhãn (**visual-confirmation-needed**)

`app/pages/provincial.py:210-243` đặt top 10, bottom 10 và outlier trong ba
cột; hai chart 450 px có 10 tên tỉnh + số ngoài cột. Desktop hẹp/tablet/mobile
có nguy cơ label chật, cắt text hoặc cuộn quá dài.

**Khuyến nghị:** tabs “Top 10 / Bottom 10 / Ngoại lệ”, hoặc toggle; default chỉ
hiện top/bottom 5.

### P1 — Nguồn lặp lại tạo nhiễu thị giác (**code-verified**)

`st.caption(config.SOURCE_DEFAULT)` xuất hiện 9 lần ở
`app/pages/provincial.py:73,168,201,219,228,243,262,290,317`. Cùng một nguồn
PAPI không cần lặp sau mọi chart.

**Khuyến nghị:** ghi nguồn chung cuối section; caption riêng chỉ cho filter,
missing-data hoặc phạm vi khác biệt.

### P1 — Filter không deep-link được (**guideline, code-verified**)

`app/pages/provincial.py:36-45,91-100` giữ scale/year/pair/region/province
trong Streamlit state nhưng không phản ánh query parameters. Guidelines yêu cầu
stateful filter có URL tái tạo được.

**Khuyến nghị:** đồng bộ filter chính vào `st.query_params` hoặc thêm nút copy
link trạng thái hiện tại.

### P2 — Map chưa có selected-province indicator bền vững (**visual-confirmation-needed**)

Map nhận selection tại `:69-86` nhưng không có layer/outline rõ cho `province`
đang drill-down. Sau rerun, người dùng có thể mất liên hệ map với ranking/radar.

**Khuyến nghị:** marker/outline bền vững, chip “Đang xem: Tỉnh — Vùng”, và
auto-scroll/focus drill panel sau click.

### P2 — Copy/narrative đầu trang quá dày (**code-verified**)

Header, map description, 4 KPI, insight dài (`:135-141`) và section description
(`:143-147`) xuất hiện trước biểu đồ so sánh đầu tiên.

**Khuyến nghị:** rút insight còn một câu có số; để hướng dẫn dài trong expander
“Cách đọc”.

## Điểm đạt guideline

- `app/lib/layout.py:98-102` có `:focus-visible` cho keyboard focus.
- `app/lib/layout.py:153-155` tôn trọng `prefers-reduced-motion`.
- H2 có label controls và empty state cho snapshot/outlier/slope.

## Thứ tự cải thiện đề xuất

1. Thay slopegraph full-61 bằng delta chart có chọn lọc.
2. Đưa drill-down ngay sau map, thêm selected-province indicator.
3. Giảm overview còn 3 chart chính; secondary analysis vào tabs/expander.
4. Gom nguồn theo section; sau đó kiểm tra responsive bằng Chrome DevTools khi
   X server/browser bridge khả dụng.

## Câu hỏi chưa giải quyết

- Buổi vấn đáp ưu tiên laptop 1366 px hay màn hình rộng? Cần Chrome screenshot
  để chốt density/kích thước chart.
- H2 ưu tiên “tìm tỉnh để drill” hay “kể chuyện chênh vùng”? Quyết định này xác
  định map hay regional comparison đứng đầu.
