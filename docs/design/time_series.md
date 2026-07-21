# Trang Diễn biến theo thời gian

## 1. Mục tiêu và ý nghĩa

Trang trả lời điểm quản trị thay đổi theo hướng nào, năm nào là điểm ngoặt, các vùng đổi vị trí ra sao
và lĩnh vực nào cải thiện/suy giảm mạnh nhất. Trọng tâm là **thời gian**, không xếp hạng tỉnh và không
phân tích nguyên nhân.

**Câu hỏi trung tâm:** Trong phạm vi được chọn, mặt bằng điểm biến động khi nào và cấu phần nào tạo ra
khác biệt đầu–cuối?

## 2. Filter và KPI

### Filter

- Phạm vi so sánh: 6 lĩnh vực gốc hoặc 8 lĩnh vực.
- Từ năm / đến năm: hai mốc hợp lệ, ít nhất cách nhau một năm.
- Focus tùy chọn: một vùng hoặc một tỉnh kế thừa từ trang khác.
- Trạng thái rõ: `Đang xem: 6 lĩnh vực · 2011–2024 · Toàn quốc`.

### KPI

| KPI đề xuất | Cách viết |
|---|---|
| Điểm đầu → cuối | Hiển thị hai số trên một card, không tách thành hai KPI |
| Tăng/giảm trong giai đoạn | `Tăng +…` hoặc `Giảm −…`, không dùng “thay đổi ròng” |
| Năm biến động mạnh nhất | Viết `so với năm trước`, không dùng YoY |
| Mức cao nhất | Giá trị và năm đạt đỉnh |

## 3. Bố cục

```text
┌──────────────────────────────┬──────────────────────────────┐
│ 01. Line chart               │ 02. Heatmap vùng × năm       │
│ Mức điểm theo thời gian      │ Nhịp tăng/giảm đồng thời     │
├──────────────────────────────┼──────────────────────────────┤
│ 03. Bump chart               │ 04. Slopegraph lĩnh vực      │
│ Thứ tự vùng thay đổi         │ Chênh lệch đầu–cuối          │
└──────────────────────────────┴──────────────────────────────┘
```

Line chart không chiếm toàn hàng. Card 01 và 02 dùng chung chiều cao 520–540 px; legend vùng của line
đặt trong plot hoặc dùng direct label để không làm hàng đầu lệch.

Cả bốn card có button phóng to ở góc phải header và dùng chung popup theo
[`chart_focus_mode.md`](chart_focus_mode.md). Chế độ mở rộng phải giữ unified hover, năm đang hover,
legend vùng và khoảng thời gian hiện tại.

## 4. Biểu đồ 01 — Line chart mức điểm theo năm

### Câu hỏi

Điểm trung bình các tỉnh tăng, giảm hay ổn định trong giai đoạn được chọn?

### Dữ liệu và mã hóa

- Dữ liệu: `totalSeries`, `regionalSeries`, `selectedSeries`.
- X: năm; Y: tổng điểm đúng theo phạm vi 6 hoặc 8 lĩnh vực.
- Đường chính: trung bình các tỉnh, màu ink/accent, width 3–3,5 px.
- Sáu vùng: width 1,5 px, opacity 45%; vùng active dùng màu vùng và width 2,5 px.
- Tỉnh active: marker hình thoi + đường warning; không thêm mọi tỉnh cùng lúc.
- Direct label cuối đường chỉ cho toàn bộ, vùng/tỉnh active; các vùng còn lại dùng legend toggle.

### Vì sao chọn line chart

Line chart tối ưu cho chuỗi liên tục 7–14 năm và giúp nhận điểm ngoặt. Chỉ trang này dùng line chart
đầy đủ; Tổng quan dùng waterfall để tránh lặp.

### Interaction

- `hovermode: x unified`; vertical guide line tại năm hover.
- Hover một đường làm đậm đường đó và mờ các đường khác.
- Click legend ẩn/hiện vùng; double-click cô lập một vùng.
- Click năm pin năm để liên kết heatmap và bump chart.
- Zoom/range selection chỉ hiện khi người dùng bật `Chọn khoảng`; mặc định modebar ẩn.

### Insight động

`Điểm {tăng/giảm} {net} từ {from} đến {to}; mức cao nhất {peak} xuất hiện năm {peak_year}.`

## 5. Biểu đồ 02 — Heatmap thay đổi năm-kề-năm theo vùng

### Câu hỏi

Năm nào nhiều vùng cùng tăng hoặc cùng giảm, và vùng nào biến động mạnh nhất?

### Dữ liệu và mã hóa

- Dữ liệu: `regionalYearOverYear`.
- X: năm đích; Y: sáu vùng; Z: điểm năm hiện tại trừ năm trước.
- Diverging scale có tâm 0 và domain đối xứng theo trị tuyệt đối lớn nhất.
- Ô hiển thị dấu `+/-` khi đủ diện tích; missing dùng hatch/xám.
- Sort vùng theo thứ tự địa lý cố định, không đổi thứ tự theo từng filter.

### Vì sao chọn heatmap

Heatmap cho phép so 6 × 13 phép thay đổi trong một card mà không tạo thêm sáu đường. Nó dùng màu để
đọc nhịp đồng thời, khác với correlation heatmap của trang Quan hệ.

### Interaction

- Hover: vùng, hai năm, điểm đầu/cuối, delta và số tỉnh đóng góp.
- Click ô: pin vùng và năm, highlight trên line/bump.
- Hover cột năm tạo guide đồng bộ với line chart.
- Control `Hiện số trong ô` dành cho người cần đọc chính xác.

### Insight động

`Năm {year} có {k}/6 vùng cùng {tăng/giảm}; {region} biến động mạnh nhất với {delta}.`

## 6. Biểu đồ 03 — Bump chart thứ hạng vùng

### Câu hỏi

Thứ tự sáu vùng thay đổi ra sao trong giai đoạn, vùng nào lên hoặc xuống nhiều bậc nhất?

### Dữ liệu và mã hóa

- Backend bổ sung hạng vùng theo từng năm từ `regionalSeries`; frontend không tự định nghĩa hạng.
- X: năm; Y: hạng 1–6, đảo trục để hạng 1 ở trên.
- Một đường cho mỗi vùng, dùng màu vùng cố định.
- Marker tại mỗi năm; label trực tiếp ở mốc đầu và cuối.
- Tie dùng `rank(method="min")` và phải được ghi ở metadata.

### Vì sao chọn bump chart

Line chart cho mức điểm tuyệt đối; bump chart chỉ cho thay đổi thứ tự. Hai biểu đồ trả lời hai câu hỏi
khác nhau và tránh phải suy hạng từ các đường gần nhau.

### Interaction

- Hover vùng làm mờ năm vùng còn lại.
- Click vùng pin selection và cập nhật line/heatmap.
- Legend có thể bỏ nếu direct labels đọc rõ; bàn phím dùng dãy sáu toggle phía trên chart.

### Insight động

`{region_up} tăng {rank_gain} bậc từ đầu kỳ; {region_down} giảm nhiều nhất với {rank_loss} bậc.`

Nếu thứ tự không đổi: `Thứ tự vùng ổn định; không vùng nào thay đổi quá {n} bậc.`

## 7. Biểu đồ 04 — Slopegraph thay đổi theo lĩnh vực

### Câu hỏi

Lĩnh vực nào cải thiện hoặc suy giảm nhiều nhất giữa hai mốc?

### Dữ liệu và mã hóa

- Dữ liệu: `dimensionDeltas` gồm điểm đầu, điểm cuối, delta và số tỉnh đóng góp.
- Hai trục dọc song song: năm đầu và năm cuối; một đường nối cho mỗi lĩnh vực.
- Label trực tiếp tên lĩnh vực + điểm ở hai đầu.
- Màu lĩnh vực cố định; arrow/dấu delta thể hiện hướng thay đổi.
- Sort theo điểm năm cuối hoặc delta; quy tắc sort hiển thị ở chart control.

### Vì sao chọn slopegraph

Slopegraph thể hiện đồng thời mức đầu, mức cuối và hướng thay đổi. Nó thay heatmap mức điểm thứ hai và
diverging bar hiện tại, làm trang đa dạng hơn mà vẫn đọc được chính xác 6–8 lĩnh vực.

### Interaction

- Hover lĩnh vực làm đậm đường và hiện điểm đầu/cuối, delta, contributorN.
- Click lĩnh vực giữ `dimension` trong URL và mở CTA sang Mối quan hệ.
- Toggle `Sắp theo thay đổi / điểm cuối` không làm mất selection.

### Insight động

`{best_dimension} tăng mạnh nhất ({best_delta}); {worst_dimension} giảm mạnh nhất ({worst_delta}).`

## 8. Cảnh báo phương pháp

- Phạm vi 6 lĩnh vực dùng được 2011–2024; phạm vi 8 lĩnh vực chỉ 2018–2024.
- Không vẽ một đường tổng đổi từ 6 sang 8 lĩnh vực tại 2018.
- Mỗi điểm trung bình dùng các tỉnh có dữ liệu; tooltip và metadata phải hiện contributorN.
- Bump chart mô tả thứ tự tương đối, không cho biết khoảng cách điểm lớn hay nhỏ.
- Insight chỉ nói tăng/giảm quan sát được, không giải thích nguyên nhân.

## 9. Acceptance criteria

- Đúng bốn biểu đồ; loại heatmap mức điểm lĩnh vực thứ hai và dãy button delta trùng biểu đồ.
- Line chart có unified tooltip, vertical guide và highlight-on-hover.
- Bump chart dùng hạng backend đã test.
- Bốn insight cập nhật theo phạm vi, khoảng năm và focus tỉnh/vùng.
- Cả bốn chart mở được trong popup xem riêng; line/heatmap vẫn hỗ trợ guide và zoom trục phù hợp.
- Chart grid bắt đầu trong first fold ở 1440 × 900.
