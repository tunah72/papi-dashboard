# Trang Tổng quan

## 1. Mục tiêu và ý nghĩa

Trang Tổng quan giúp người xem hiểu trạng thái PAPI của năm được chọn trong khoảng 20–30 giây và biết
nên đi sâu vào hướng phân tích nào. Trang không làm lại ranking, correlation hoặc clustering đầy đủ;
bốn biểu đồ chỉ là bốn “cửa vào” tương ứng với không gian, thời gian, quan hệ và thay đổi.

**Câu hỏi trung tâm:** Bức tranh hiện tại nổi bật ở đâu, chuyển động thế nào và tín hiệu nào đáng xem
tiếp?

## 2. Filter và KPI

### Filter page-level

- `Phạm vi so sánh`: 6 lĩnh vực gốc hoặc 8 lĩnh vực.
- `Năm`: snapshot đang xem; khi chọn 8 lĩnh vực chỉ cho phép 2018–2024.
- Trạng thái: `Đang xem: Tổng PAPI 8 lĩnh vực · 2024 · 61 tỉnh có dữ liệu`.
- Click một tỉnh trên bản đồ thêm `province` vào URL nhưng không đổi toàn bộ snapshot.

### Bốn KPI

| KPI | Ý nghĩa |
|---|---|
| Số tỉnh có dữ liệu | Công bố mẫu thật, không mặc định 63 |
| Điểm trung bình | Mặt bằng của các tỉnh có dữ liệu |
| Tỉnh cao nhất | Cực trị trên cùng phạm vi/năm |
| Khoảng cách cao nhất–thấp nhất | Mức phân hóa trong snapshot |

KPI dùng bề mặt trung tính. Tên tỉnh cao/thấp không tô xanh/đỏ như đánh giá đạo đức; chỉ dùng accent
để nhấn đối tượng đang chọn.

## 3. Bố cục

```text
┌──────────────────────────────┬──────────────────────────────┐
│ 01. Choropleth               │ 02. Waterfall theo năm       │
│ Phân bố hiện tại             │ Nhịp thay đổi tổng           │
├──────────────────────────────┼──────────────────────────────┤
│ 03. Thanh chồng bốn góc      │ 04. Histogram delta tỉnh     │
│ Tín hiệu quan hệ             │ Phổ cải thiện/suy giảm       │
└──────────────────────────────┴──────────────────────────────┘
```

Bốn card 6 cột, cùng chiều cao. Map không được chiếm toàn hàng; hình Việt Nam fit trong viewport card
và dành đủ 56 px cho insight phía dưới.

Cả bốn card có button phóng to ở góc phải header và dùng chung popup theo
[`chart_focus_mode.md`](chart_focus_mode.md). Popup phải giữ đúng năm, scale, tỉnh đang chọn và insight
của card nguồn.

## 4. Biểu đồ 01 — Choropleth phân bố điểm

### Câu hỏi

Điểm PAPI cao và thấp tập trung ở những tỉnh nào trong năm đang chọn?

### Dữ liệu và mã hóa

- Dữ liệu: `overview.map.rows` và GeoJSON.
- Địa lý: tỉnh.
- Fill: tổng điểm theo sequential scale, cùng domain cho toàn snapshot.
- Stroke 2–3 px: tỉnh đang chọn; các tỉnh khác stroke trung tính 0,5 px.
- Missing: xám có hatch/nhãn trong tooltip, không nằm ở đáy color scale.

### Vì sao chọn choropleth

Đây là biểu đồ duy nhất cần trả lời trực tiếp câu hỏi địa lý. Bản đồ giúp nhận ra cụm không gian trước
khi người xem đọc ranking; nó không dùng ở trang Vùng & tỉnh để tránh lặp lại.

### Interaction

- Hover: tỉnh, vùng, điểm, hạng năm và trạng thái dữ liệu.
- Click tỉnh: pin selection, đồng bộ KPI phụ và CTA `Xem hồ sơ tỉnh`.
- Hover tỉnh làm nổi tỉnh và vùng liên quan; không lọc các chart khác cho đến khi click.
- Bàn phím: danh sách tỉnh tìm kiếm được bên dưới hoặc trong bảng tóm tắt.

### Insight động

`{leader} cao nhất với {max}; {last} thấp nhất với {min}, tạo khoảng cách {gap} điểm.`

Insight trả lời cực trị; không dùng câu “tỉnh tốt nhất/xấu nhất”.

## 5. Biểu đồ 02 — Waterfall thay đổi trung bình theo năm

### Câu hỏi

Mặt bằng điểm tăng hoặc giảm chủ yếu ở những năm nào?

### Dữ liệu và mã hóa

- Dữ liệu: `overview.storyCards.trend.rows`.
- X: năm; Y: chênh lệch so với năm trước.
- Thanh nổi: delta năm-kề-năm; đường baseline ở 0.
- Thanh đầu tiên là mức gốc, thanh cuối có annotation mức hiện tại.
- Màu tăng/giảm đi cùng dấu `+/-` và hướng thanh.

### Vì sao chọn waterfall

Trang Diễn biến đã dùng line chart để đọc toàn chuỗi. Waterfall ở Tổng quan chỉ nêu năm nào đóng góp
vào thay đổi ròng, nên không lặp hình thức hoặc nội dung của trang chuyên sâu.

### Interaction

- Hover: năm, điểm hiện tại, điểm năm trước, delta và số tỉnh đóng góp.
- Click một năm: mở trang Diễn biến với khoảng năm kết thúc ở mốc đó.
- Highlight-on-hover một thanh; không animation lại toàn bộ chuỗi.

### Insight động

`Mức tăng lớn nhất xuất hiện năm {year_up} ({delta_up}); mức giảm mạnh nhất ở {year_down} ({delta_down}).`

## 6. Biểu đồ 03 — Thanh chồng 100% của cặp lĩnh vực nổi bật

### Câu hỏi

Các tỉnh phân bố thế nào trong bốn nhóm cao–cao, cao–thấp, thấp–cao và thấp–thấp của cặp lĩnh vực
liên hệ mạnh nhất?

### Dữ liệu và mã hóa

- Dữ liệu: `overview.storyCards.strongestPair.rows` và `pearsonR`.
- Một thanh ngang 100%, chia bốn segment theo tỷ lệ tỉnh trong bốn quadrant.
- Label trực tiếp: tên nhóm + số tỉnh; segment quá nhỏ chuyển label ra ngoài.
- Trên plot hiển thị `r` như annotation, không dùng gauge.
- Màu bốn nhóm dùng palette phân loại có tương phản, không dùng xanh = tốt, đỏ = xấu.

### Vì sao chọn thanh chồng

Scatter chi tiết được dành cho trang Mối quan hệ. Thanh chồng ở Tổng quan trả lời “cơ cấu các kiểu
kết hợp” thay vì mô phỏng lại đám mây điểm.

### Interaction

- Hover segment: số tỉnh, tỷ lệ và tối đa năm tên tỉnh mẫu.
- Click segment: mở trang Mối quan hệ với cặp X/Y và quadrant được chọn.
- Legend không cần nếu nhãn segment đọc được; trên màn hình hẹp chuyển thành legend hai cột.

### Insight động

`{pair_label} có r = {r}; nhóm {largest_quadrant} chiếm nhiều nhất với {n}/{total} tỉnh.`

Thêm hậu tố ngắn: `Đây là liên hệ quan sát, không phải quan hệ nhân quả.`

## 7. Biểu đồ 04 — Histogram mức thay đổi của tỉnh

### Câu hỏi

Phần lớn tỉnh cải thiện hay suy giảm so với mốc đầu của phạm vi?

### Dữ liệu và mã hóa

- Dữ liệu: toàn bộ `changeHighlights.rows`, chỉ gồm tỉnh đủ hai mốc.
- X: chênh lệch điểm; Y: số tỉnh.
- Bin width ổn định theo scale; trục X có baseline 0.
- Vertical line: median; marker/annotation: tỉnh tăng và giảm cực trị.
- Hai phía 0 có tint semantic nhẹ; dấu và nhãn vẫn là kênh chính.

### Vì sao chọn histogram

Trang Phân nhóm sẽ so từng tỉnh bằng dumbbell. Histogram ở Tổng quan cho biết hình dạng phân phối và
tỷ lệ tăng/giảm, không lặp danh sách top/bottom.

### Interaction

- Hover bin: khoảng delta, số tỉnh và tỷ lệ.
- Click bin: mở trang Thay đổi & phân nhóm với khoảng delta tương ứng nếu API hỗ trợ; nếu chưa hỗ trợ,
  chỉ pin và hiện danh sách tỉnh trong bảng tóm tắt.
- Brush chọn khoảng delta là enhancement, không phải điều kiện MVP.

### Insight động

`{pct_up}% tỉnh tăng điểm; trung vị thay đổi là {median}, trên {n} tỉnh đủ dữ liệu ở hai mốc.`

## 8. Cross-filter và drill-through

- Tỉnh chọn từ map được giữ khi mở Vùng & tỉnh, Diễn biến hoặc Trợ lý AI.
- Năm chọn từ waterfall được giữ khi mở Diễn biến.
- Cặp lĩnh vực từ thanh chồng được giữ khi mở Mối quan hệ.
- Khoảng năm của histogram theo đúng `year_min` của phạm vi, hiển thị rõ trong subtitle.
- CTA sau mỗi selection là text link; không thêm bốn nút cạnh tranh ở cuối trang.

## 9. Acceptance criteria

- Đúng bốn biểu đồ; bỏ ranking panel và ba story card trùng trang chuyên sâu hiện tại.
- Map, waterfall, stacked bar và histogram không dùng chung một encoding chính.
- Mỗi card có insight động, metadata và bảng thay thế.
- Cả bốn chart mở được trong popup xem riêng và đóng lại không làm mất filter/selection.
- Không gọi tổng 6 lĩnh vực là “Tổng PAPI”.
- Khi năm 2024 có 61 tỉnh hợp lệ, UI hiển thị 61 thay vì 63.
