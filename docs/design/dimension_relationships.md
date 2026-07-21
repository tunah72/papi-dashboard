# Trang Mối quan hệ giữa các lĩnh vực

## 1. Mục tiêu và ý nghĩa

Trang mô tả các lĩnh vực PAPI cùng biến thiên như thế nào giữa các tỉnh trong một năm, mức liên hệ
tuyến tính của một cặp và những tỉnh lệch khỏi xu hướng. Trang không trả lời nguyên nhân và không dùng
tương quan để khẳng định lĩnh vực này tác động lĩnh vực kia.

**Câu hỏi trung tâm:** Lĩnh vực nào có liên hệ quan sát mạnh, mối quan hệ của cặp đang chọn có hình dạng
ra sao và tỉnh nào là ngoại lệ?

## 2. Filter và KPI

### Filter

- Phạm vi: 6 hoặc 8 lĩnh vực.
- Năm snapshot.
- Lĩnh vực X và Y, luôn khác nhau.
- Tỉnh focus tùy chọn từ trang Vùng & tỉnh.

### KPI

| KPI | Ý nghĩa |
|---|---|
| Pearson r | Hướng và độ mạnh cùng biến thiên tuyến tính |
| R² | Tỷ lệ biến thiên tuyến tính được mô tả trong mẫu |
| Số tỉnh hợp lệ | Mẫu thực tế của cặp X/Y |
| Tỉnh lệch xu hướng nhất | Residual tuyệt đối lớn nhất |

KPI `r` và `R²` luôn kèm nhãn `mô tả, không nhân quả` ở detail.

## 3. Bố cục

```text
┌──────────────────────────────┬──────────────────────────────┐
│ 01. Correlation heatmap      │ 02. Scatter + regression     │
│ Toàn bộ cặp lĩnh vực         │ Cặp X/Y đang chọn            │
├──────────────────────────────┼──────────────────────────────┤
│ 03. Residual forest plot     │ 04. Mean ± SD range plot     │
│ Ngoại lệ của cặp             │ Mức phân tán từng lĩnh vực   │
└──────────────────────────────┴──────────────────────────────┘
```

Cả bốn card có button phóng to ở góc phải header và dùng chung popup theo
[`chart_focus_mode.md`](chart_focus_mode.md). Popup giữ cặp X/Y, năm, tỉnh focus, regression và trạng
thái selection của card nguồn.

## 4. Biểu đồ 01 — Correlation heatmap nửa dưới

### Câu hỏi

Cặp lĩnh vực nào liên hệ cùng chiều/ngược chiều mạnh nhất trong năm đang chọn?

### Dữ liệu và mã hóa

- Dữ liệu: `correlation.codes` và `matrix`.
- Chỉ hiển thị tam giác dưới; diagonal và nửa trên để trống.
- Diverging scale từ −1 đến +1, tâm 0 cố định giữa mọi filter.
- Mỗi ô có `r` hai chữ số; label dùng tên ngắn lĩnh vực, không chỉ mã D1–D8.
- Stroke/outline ô đang chọn rõ hơn màu.

### Vì sao chọn heatmap

Heatmap là hình thức hiệu quả nhất cho ma trận 6×6 hoặc 8×8. Nó cho toàn bộ cặp trong một card và
cho phép chọn cặp để drill sang scatter.

### Interaction

- Hover: hai lĩnh vực, r, hướng/độ mạnh và n cặp hợp lệ.
- Click ô: đổi X/Y, outline selection và cập nhật ba chart còn lại.
- Bàn phím: bảng ma trận có button tại từng cặp; arrow keys là enhancement.

### Insight động

`{pair_strongest} liên hệ mạnh nhất với r = {r}; không có bằng chứng nhân quả từ biểu đồ này.`

## 5. Biểu đồ 02 — Scatter plot với hồi quy

### Câu hỏi

Mối quan hệ của cặp X/Y có nhất quán giữa các tỉnh và vùng không?

### Dữ liệu và mã hóa

- Dữ liệu: `pair.rows` và `regression.rows`.
- X/Y: điểm hai lĩnh vực thật, cùng domain phù hợp 1–10.
- Mỗi dot là tỉnh; màu vùng, marker focus có viền đậm và label.
- Đường OLS màu ink; band tin cậy chỉ thêm nếu backend cung cấp đúng.
- Đường trung bình X/Y chia bốn quadrant; dùng dash mảnh.

### Vì sao chọn scatter

Scatter cho thấy hình dạng, cluster, ngoại lệ và độ phủ dữ liệu mà một hệ số r không thể hiện. Đây là
scatter theo giá trị thật; PCA scatter ở trang Phân nhóm có ý nghĩa hoàn toàn khác.

### Interaction

- Hover dot: tỉnh, vùng, X, Y, residual và quadrant.
- Hover vùng qua legend làm mờ các vùng khác; click legend ẩn/hiện vùng.
- Click tỉnh pin selection và liên kết residual plot.
- Lasso/box select chỉ bật trong modebar tùy chọn; kết quả selection không thay r toàn trang nếu chưa
  có nhãn rõ `r của tập được chọn`.

### Insight động

`{x_label} và {y_label} có r = {r}, R² = {r2}; {quadrant_largest} là nhóm đông nhất.`

## 6. Biểu đồ 03 — Residual forest plot

### Câu hỏi

Tỉnh nào cao hơn hoặc thấp hơn đáng kể so với giá trị dự đoán tuyến tính?

### Dữ liệu và mã hóa

- Dữ liệu: 12 tỉnh có `abs(residual)` lớn nhất từ `regression.rows`.
- Y: tỉnh; X: residual; baseline 0.
- Dot + stem từ 0 tạo forest/lollipop hai phía.
- Ký hiệu `+`/`−`, không chỉ màu; tỉnh focus có outline và label.
- Sort theo residual từ âm đến dương hoặc trị tuyệt đối theo control.

### Vì sao chọn forest plot

Biểu đồ tách ngoại lệ khỏi đám mây scatter và cho biết hướng sai lệch. Nó chính xác hơn bar dày, đồng
thời giảm trùng với các bar chart ở trang khác.

### Interaction

- Hover: giá trị thật, dự đoán, residual và vùng.
- Click tỉnh pin vào scatter và giữ khi chuyển sang trang Vùng & tỉnh.
- Toggle `Trị tuyệt đối / Hướng residual` thay sort, không đổi mẫu top 12 khi chưa xác nhận.

### Insight động

`{province} lệch xu hướng nhiều nhất: {y_label} {cao/thấp hơn} dự đoán {abs_residual} điểm.`

Không gọi tỉnh đó là “bất thường” theo nghĩa chất lượng dữ liệu nếu chưa có kiểm chứng.

## 7. Biểu đồ 04 — Range plot trung bình ± độ lệch chuẩn

### Câu hỏi

Lĩnh vực nào có mức điểm cao/thấp và khác biệt giữa các tỉnh lớn nhất?

### Dữ liệu và mã hóa

- Dữ liệu: `standardDeviation.rows`.
- Y: lĩnh vực; X: thang điểm 1–10.
- Dot: mean; line hai phía: mean ± 1 SD, cắt trong domain hiển thị nếu cần.
- Màu lĩnh vực cố định; direct label mean và SD.
- Sort theo SD mặc định, có toggle sort theo mean.

### Vì sao chọn range plot

Range plot kết hợp mặt bằng và độ phân tán trong một hình, giàu thông tin hơn bar SD hiện tại. Nó không
lặp heatmap vì chỉ so từng lĩnh vực độc lập.

### Interaction

- Hover: mean, SD, n, min/max nếu backend cung cấp.
- Click lĩnh vực đặt làm X; `Shift+click` hoặc control riêng đặt làm Y để đảm bảo accessibility.
- Focus chart control thể hiện rõ X/Y đang chọn.

### Insight động

`{most_variable} phân hóa mạnh nhất giữa các tỉnh (SD = {sd}); {highest_mean} có mức trung bình cao nhất.`

## 8. Cảnh báo phương pháp

- Pearson r và OLS chỉ mô tả liên hệ tuyến tính trong snapshot một năm.
- Không suy ra chiều tác động, cơ chế hoặc hiệu quả chính sách.
- r có thể thay đổi khi thiếu tỉnh; luôn dùng n của cặp hoàn chỉnh.
- Residual lớn không tự động là lỗi dữ liệu hoặc tỉnh “tốt/xấu”.
- Mean ± SD là mô tả phân tán, không phải khoảng tin cậy.

## 9. Acceptance criteria

- Chọn ô heatmap cập nhật X/Y và URL có thể chia sẻ.
- Scatter có đường hồi quy, quadrant, hover-dim và focus tỉnh rõ.
- Residual plot và scatter liên kết hai chiều.
- Range plot dùng cùng thang 1–10 và không gọi SD là sai số.
- Cả bốn chart mở được trong popup xem riêng; popup không thay đổi cặp X/Y hoặc tính lại mô hình.
- Tất cả insight có qualifier chống diễn giải nhân quả.

## 10. Contract triển khai

`GET /api/v1/dimensions` trả đúng artifact cho bốn card:

- `correlation.matrix`, `counts` và `strengths`: hệ số, cỡ mẫu hợp lệ và nhãn mức liên hệ của từng
  cặp. Snapshot giữ tỉnh có ít nhất một lĩnh vực; từng hệ số vẫn dùng pairwise-complete observations,
  vì vậy `n` có thể khác giữa các ô.
- `pair` và `regression`: điểm thật, vùng, quadrant, đường OLS, residual và R² của cặp X/Y đang chọn.
- `standardDeviation.rows`: mean, SD, min, max và `n` riêng cho từng lĩnh vực.
- `insights.correlation`, `pair`, `residual` và `variation`: bốn kết luận xác định từ cùng artifact đã
  xử lý, không phải nội dung do AI sinh.

Trang không lặp snapshot ở header, không đặt khối “Cách đọc đúng” và không thêm hướng dẫn dưới từng
biểu đồ. Control `Gán click: X/Y` là kênh truy cập được thay cho yêu cầu `Shift+click` ở range plot.
Mở trang, thay filter hoặc mở popup không gọi API AI và không thực thi code; luồng human-in-the-loop
của Trợ lý AI vẫn là code hiển thị ở trạng thái chờ duyệt, chỉ chạy local sau khi người dùng phê duyệt.
