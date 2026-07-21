# Trang Khác biệt giữa vùng và tỉnh

## 1. Mục tiêu và ý nghĩa

Trang giúp người xem hiểu mức phân hóa giữa sáu vùng, vị trí của từng tỉnh trong vùng và lĩnh vực nào
làm hồ sơ tỉnh khác benchmark. Bản đồ không lặp lại ở đây; trang ưu tiên các biểu đồ so sánh chính xác
hơn sau khi người xem đã chọn tỉnh từ Tổng quan.

**Câu hỏi trung tâm:** Tỉnh đang chọn đứng ở đâu so với các tỉnh cùng vùng và khác mặt bằng vùng/toàn
bộ mẫu ở những lĩnh vực nào?

## 2. Filter và KPI

### Filter

- Phạm vi so sánh: 6 hoặc 8 lĩnh vực.
- Năm snapshot.
- Vùng.
- Tỉnh; danh sách tỉnh phụ thuộc vùng và chỉ gồm tỉnh có tổng hợp lệ.
- Trạng thái: `Đang xem: Quảng Ninh · Đồng bằng sông Hồng · 2024 · 8 lĩnh vực`.

### KPI

| KPI | Ý nghĩa |
|---|---|
| Điểm của tỉnh | Giá trị tổng của tỉnh đang chọn |
| Hạng trong vùng | `hạng / số tỉnh có dữ liệu` |
| So với trung bình vùng | Chênh lệch có dấu |
| So với trung bình toàn bộ mẫu | Chênh lệch có dấu và `n` |

Không dùng KPI “vùng tốt nhất” vì chart 01 đã trả lời phân phối vùng; tránh lặp nội dung.

## 3. Bố cục

```text
┌──────────────────────────────┬──────────────────────────────┐
│ 01. Boxplot + beeswarm       │ 02. Lollipop ranking         │
│ Phân phối sáu vùng           │ Thứ hạng trong vùng          │
├──────────────────────────────┼──────────────────────────────┤
│ 03. Bullet benchmark         │ 04. Radar profile            │
│ Tỉnh – vùng – toàn mẫu       │ Cấu trúc 6–8 lĩnh vực        │
└──────────────────────────────┴──────────────────────────────┘
```

Bốn card cùng chiều cao. Tỉnh được chọn dùng cùng một stroke/marker trên cả bốn chart; màu vùng chỉ
dùng khi cần phân biệt sáu nhóm.

Cả bốn card có button phóng to ở góc phải header và dùng chung popup theo
[`chart_focus_mode.md`](chart_focus_mode.md). Popup giữ đồng bộ tỉnh, vùng, năm và benchmark đang bật
trên card nguồn.

## 4. Biểu đồ 01 — Boxplot kết hợp beeswarm theo vùng

### Câu hỏi

Vùng nào có mặt bằng cao/thấp và vùng nào phân hóa nhiều nhất giữa các tỉnh?

### Dữ liệu và mã hóa

- Dữ liệu: `distribution.rows`.
- Y: sáu vùng; X: tổng điểm cùng một năm/phạm vi.
- Boxplot: median, Q1–Q3 và whisker; overlay jittered dot cho từng tỉnh.
- Tỉnh đang chọn: marker lớn hơn, viền ink và nhãn trực tiếp.
- Vùng active có opacity 100%; các vùng khác 55–70%, không biến mất.

### Vì sao chọn boxplot + beeswarm

Boxplot cho mặt bằng và độ phân tán; beeswarm giữ từng tỉnh thật, tránh che mất kích thước mẫu nhỏ của
một số vùng. Nó thay bản đồ hiện tại và bổ sung thông tin phân phối mà bản đồ không thể hiện.

### Interaction

- Hover dot: tỉnh, điểm, hạng năm và vùng.
- Hover box: median, Q1, Q3, min/max hợp lệ và n.
- Click dot: đổi tỉnh nhưng giữ năm/phạm vi; click vùng: đổi vùng và chọn tỉnh mặc định có giải thích.
- Bàn phím dùng danh sách tỉnh song song, không yêu cầu chọn dot bằng chuột.

### Insight động

`{highest_region} có trung vị cao nhất ({median}); {widest_region} phân hóa rộng nhất với IQR {iqr}.`

## 5. Biểu đồ 02 — Lollipop xếp hạng tỉnh trong vùng

### Câu hỏi

Tỉnh đang chọn đứng thứ bao nhiêu trong vùng và cách tỉnh dẫn đầu bao xa?

### Dữ liệu và mã hóa

- Dữ liệu: `ranking.rows`.
- Y: tỉnh sắp giảm dần; X: tổng điểm.
- Stem mảnh từ baseline hợp lý đến dot; dot được chọn lớn hơn và có direct label.
- Chỉ hiển thị một vùng, tối đa 14 tỉnh nên không cần top/bottom tab.
- Trục bắt đầu từ domain có khoảng đệm, không bắt buộc từ 0 vì dot plot mã hóa vị trí, nhưng domain và
  khoảng thực phải ghi rõ để tránh phóng đại.

### Vì sao chọn lollipop

Lollipop nhẹ hơn bar chart khi có 5–14 tỉnh, giữ thứ tự rõ và giảm lượng mực. Nó dành riêng cho thứ
hạng trong vùng; Tổng quan không hiển thị ranking chart.

### Interaction

- Hover: điểm, hạng và chênh lệch với tỉnh ngay trên/dưới.
- Click dot/label: đổi tỉnh và đồng bộ bullet/radar.
- Toggle `Giá trị / Thứ hạng` chỉ đổi label, không đổi trật tự.

### Insight động

`{province} đứng {rank}/{region_total}, thấp hơn tỉnh dẫn đầu {gap_to_leader} điểm.`

Nếu dẫn đầu: `{province} dẫn đầu vùng, cao hơn vị trí thứ hai {gap_second} điểm.`

## 6. Biểu đồ 03 — Bullet chart benchmark tổng điểm

### Câu hỏi

Điểm của tỉnh cao hay thấp hơn trung bình vùng và toàn bộ mẫu bao nhiêu?

### Dữ liệu và mã hóa

- Dữ liệu: `benchmark` cùng min/max từ `distribution`.
- Một horizontal range từ min đến max toàn bộ mẫu.
- Marker chính: điểm tỉnh; marker phụ khác hình: trung bình vùng và trung bình toàn bộ mẫu.
- Dải nền có thể biểu thị Q1–Q3 toàn bộ mẫu nếu backend cung cấp; không dùng tier màu như đánh giá tốt/xấu.
- Direct label cho cả ba marker; cùng một trục điểm.

### Vì sao chọn bullet chart

Bullet chart trả lời chính xác khoảng cách giữa ba benchmark trong không gian nhỏ hơn ba KPI rời rạc.
Nó không lặp radar vì chỉ so tổng điểm, còn radar so cấu trúc lĩnh vực.

### Interaction

- Hover marker: giá trị, delta với tỉnh và n của benchmark.
- Click marker vùng/toàn mẫu đổi đường benchmark active trên radar.
- Focus bằng bàn phím theo thứ tự tỉnh → vùng → toàn mẫu.

### Insight động

`{province} {cao/thấp hơn} vùng {abs(vs_region)} điểm và {cao/thấp hơn} toàn bộ mẫu {abs(vs_national)} điểm.`

## 7. Biểu đồ 04 — Radar profile lĩnh vực

### Câu hỏi

Tỉnh mạnh/yếu tương đối ở lĩnh vực nào so với vùng và toàn bộ mẫu?

### Dữ liệu và mã hóa

- Dữ liệu: `profile.rows`.
- 6 hoặc 8 trục lĩnh vực, cùng domain 1–10.
- Ba chuỗi tối đa: tỉnh (fill 12–16%, stroke 3 px), vùng (dash), toàn mẫu (dot).
- Màu không đổi theo lĩnh vực trong radar vì mỗi polygon là một benchmark; tên lĩnh vực nằm trực tiếp
  ở trục. Nếu cần màu lĩnh vực, dùng marker nhỏ theo token nhưng không đổi stroke polygon.
- Thứ tự lĩnh vực cố định D1→D8 để shape có thể so giữa filter.

### Vì sao chọn radar

Radar được dùng duy nhất tại đây để đọc “hình dáng hồ sơ” của một tỉnh qua 6–8 lĩnh vực. Nó phù hợp vì
số trục ít và chỉ có ba chuỗi; bảng bên dưới vẫn là kênh đọc chính xác.

### Interaction

- Hover vertex: điểm tỉnh, vùng, toàn mẫu, delta và n cho lĩnh vực.
- Legend toggle từng benchmark; tỉnh luôn bật mặc định.
- Click lĩnh vực mở trang Mối quan hệ với lĩnh vực đó làm X và giữ tỉnh trong URL.
- Bảng tóm tắt bắt buộc để khắc phục hạn chế đọc chính xác của radar.

### Insight động

`{province} vượt vùng nhiều nhất ở {strong_dimension} ({delta_strong}); thấp hơn nhiều nhất ở {weak_dimension} ({delta_weak}).`

## 8. Cảnh báo phương pháp

- So sánh phải cùng năm và cùng phạm vi 6/8 lĩnh vực.
- Benchmark dùng đúng các tỉnh có dữ liệu; luôn công bố n vùng và n toàn mẫu.
- Hạng không thể hiện ý nghĩa thống kê của chênh lệch nhỏ.
- Radar mô tả shape, không cộng diện tích polygon để tạo thêm chỉ số.
- Không gọi vùng/tỉnh “tốt” hoặc “xấu”; dùng cao/thấp theo đánh giá PAPI.

## 9. Acceptance criteria

- Không lặp choropleth; bản đồ chỉ nằm ở Tổng quan.
- Bốn chart liên kết cùng tỉnh nhưng trả lời bốn câu hỏi khác nhau.
- Box/beeswarm và lollipop chọn tỉnh được bằng cả chuột lẫn control bàn phím.
- Radar có tối đa ba series, domain cố định và bảng thay thế.
- Cả bốn chart mở được trong popup xem riêng; radar vẫn có bảng thay thế và tối đa ba series.
- Insight công bố giá trị, chênh lệch và n thích hợp.
