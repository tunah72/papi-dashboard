# Trang Sự thay đổi và phân nhóm

## 1. Mục tiêu và ý nghĩa

Trang kết hợp hai lớp phân tích: thay đổi tổng điểm giữa hai mốc và thay đổi profile nhiều lĩnh vực.
Người xem cần phân biệt rõ `điểm tăng/giảm` với `chuyển profile`; một tỉnh có thể tăng điểm nhưng vẫn
ở cùng profile, hoặc đổi profile mà tổng điểm thay đổi ít.

**Câu hỏi trung tâm:** Tỉnh nào thay đổi mạnh, các profile khác nhau ở lĩnh vực nào và luồng chuyển
profile nào phổ biến?

## 2. Filter và KPI

### Filter

- Phạm vi: 6 hoặc 8 lĩnh vực.
- Mốc đầu / mốc cuối.
- Số profile K: `Tự chọn 2–6` hoặc K cụ thể.
- Profile/tỉnh focus là chart-level selection, không làm filter bar quá cao.

### KPI

| KPI | Ý nghĩa |
|---|---|
| Trung vị thay đổi | Mức thay đổi điển hình của tỉnh đủ hai mốc |
| Số profile được chọn | K và chế độ tự động/thủ công |
| Độ tách profile | Silhouette, kèm cách đọc ngắn |
| Tỉnh chuyển profile | Số/tỷ lệ assignment đổi nhãn ổn định |

## 3. Bố cục

```text
┌──────────────────────────────┬──────────────────────────────┐
│ 01. Dumbbell đầu–cuối        │ 02. Profile small multiples  │
│ Tỉnh thay đổi mạnh           │ Đặc trưng từng profile       │
├──────────────────────────────┼──────────────────────────────┤
│ 03. PCA trajectory scatter   │ 04. Sankey chuyển profile    │
│ Dịch chuyển trong không gian │ Luồng đầu → cuối             │
└──────────────────────────────┴──────────────────────────────┘
```

Loại hai bar tăng/giảm riêng và bảng nhiệt transition hiện tại khỏi bốn chart chính. Bảng đầy đủ tỉnh
vẫn nằm dưới grid trong `<details>` để kiểm chứng số liệu.

Cả bốn card có button phóng to ở góc phải header và dùng chung popup theo
[`chart_focus_mode.md`](chart_focus_mode.md). Popup giữ mốc đầu/cuối, K, profile, tỉnh hoặc luồng đang
chọn; mở popup không chạy lại KMeans/PCA.

## 4. Biểu đồ 01 — Dumbbell điểm đầu–cuối

### Câu hỏi

Tỉnh nào tăng hoặc giảm tổng điểm nhiều nhất giữa hai mốc?

### Dữ liệu và mã hóa

- Dữ liệu: `changes.rows`; mặc định hiển thị hợp nhất top 8 tăng và top 8 giảm, loại trùng.
- Y: tỉnh; X: tổng điểm.
- Dot rỗng: mốc đầu; dot đặc: mốc cuối; segment nối hai mốc.
- Arrow/delta label ở cuối segment; sort theo delta.
- Màu hướng tăng/giảm kèm ký hiệu, không tô màu tỉnh như một category vĩnh viễn.

### Vì sao chọn dumbbell

Dumbbell hiển thị đồng thời điểm đầu, điểm cuối và độ dài thay đổi trong một chart. Nó thay hai bar
top/bottom hiện tại, giảm trùng nội dung và trả lại một slot cho phân tích profile.

### Interaction

- Hover segment: tỉnh, vùng, điểm đầu/cuối, delta.
- Click tỉnh pin trên PCA và mở row tương ứng trong bảng kiểm chứng.
- Toggle `Cực trị / Tất cả` chuyển sang virtualized table hoặc chart scroll, không nhồi 63 hàng.
- Filter `Tăng / Giảm / Cả hai` là chart-level.

### Insight động

`{top_increase} tăng nhiều nhất ({delta_up}); {top_decrease} giảm nhiều nhất ({delta_down}).`

## 5. Biểu đồ 02 — Small multiples diverging bar của profile

### Câu hỏi

Mỗi profile mạnh hoặc yếu tương đối ở những lĩnh vực nào?

### Dữ liệu và mã hóa

- Dữ liệu: `clusterModel.centroids.values` theo z-score và raw score.
- Một panel nhỏ cho mỗi profile A–F, tối đa 6 panel trong grid 2×K hoặc 3×2 bên trong card.
- Y: lĩnh vực; X: z-score, baseline 0.
- Bar sang phải: cao hơn mặt bằng năm; sang trái: thấp hơn.
- Label panel: `Profile A · n đầu / n cuối · descriptor`.
- Màu diverging semantic nhưng không gọi phải = tốt, trái = xấu; đây là tương đối so với mặt bằng năm.

### Vì sao chọn small multiples

Small multiples cho phép đọc từng profile như một “chữ ký” chính xác hơn radar nhiều lớp và tránh lặp
heatmap. Cùng baseline 0 giúp so profile nhanh.

### Interaction

- Hover bar: z-score, điểm gốc, lĩnh vực và n profile.
- Click panel pin profile, làm nổi tỉnh tương ứng trên PCA và Sankey.
- Click lĩnh vực có thể mở trang Mối quan hệ nhưng không thay K.
- Bàn phím: profile buttons A–F đi trước chart, có `aria-pressed`.

### Insight động

`Profile {active} nổi bật ở {strong_dims} và thấp hơn mặt bằng ở {weak_dims}; có {n_end} tỉnh tại mốc cuối.`

## 6. Biểu đồ 03 — PCA trajectory scatter

### Câu hỏi

Các tỉnh dịch chuyển bao xa và theo hướng nào trong không gian profile giữa hai mốc?

### Dữ liệu và mã hóa

- Dữ liệu: `clusterModel.assignments` và `pcaVariance`.
- X/Y: PC1 và PC2; subtitle ghi tổng tỷ lệ phương sai giải thích.
- Mốc đầu: circle-open; mốc cuối: diamond-solid; segment mảnh nối cùng tỉnh.
- Màu marker theo profile tại từng mốc; tỉnh focus có marker lớn và segment đậm.
- Không diễn giải PC1/PC2 như điểm tốt/xấu.

### Vì sao chọn PCA trajectory scatter

Đây là cách ngắn gọn để chiếu profile 6–8 chiều và thể hiện chuyển động cùng tỉnh. Scatter ở trang Quan
hệ dùng hai lĩnh vực thật; PCA scatter dùng tọa độ tổng hợp không đơn vị nên không trùng câu hỏi.

### Interaction

- Hover endpoint: tỉnh, vùng, profile đầu/cuối, đổi profile hay giữ profile.
- Hover segment làm mờ các tỉnh khác; click pin tỉnh.
- Lasso selection bật tùy chọn để liệt kê tỉnh gần nhau, không chạy lại KMeans tự động.
- Legend toggle profile; direct label chỉ cho tỉnh đang chọn.

### Insight động

`{changed}/{n} tỉnh đổi profile; {province_farthest} dịch chuyển xa nhất trong mặt phẳng PCA.`

Khoảng cách PCA chỉ là mô tả trên hai thành phần hiển thị.

## 7. Biểu đồ 04 — Sankey luồng chuyển profile

### Câu hỏi

Luồng chuyển profile nào phổ biến nhất và bao nhiêu tỉnh giữ nguyên profile?

### Dữ liệu và mã hóa

- Dữ liệu: `clusterModel.transitions`.
- Node trái: profile mốc đầu; node phải: profile mốc cuối.
- Link width: số tỉnh; link cùng profile dùng màu profile, link chuyển profile dùng màu trung tính với
  opacity 45–60% để tránh cầu vồng.
- Node label: profile + n; thứ tự node ổn định A→F.
- Chỉ dùng Sankey khi K ≤ 6 và có transition thật; đây là trường hợp dữ liệu phù hợp.

### Vì sao chọn Sankey

Sankey thể hiện quy mô luồng đầu→cuối trực quan hơn ma trận khi mục tiêu là “đi đâu”. Ma trận/bảng số
vẫn nằm trong fallback để đọc chính xác và hỗ trợ accessibility.

### Interaction

- Hover link: profile đầu, profile cuối, số/tỷ lệ và danh sách tỉnh rút gọn.
- Click link pin luồng, lọc highlight trên PCA và danh sách tỉnh; không thay mô hình.
- Hover node làm nổi toàn bộ link đi/đến node.
- Dùng component Plotly Sankey lazy-load riêng; không tăng bundle Cartesian của trang khác.

### Insight động

`{retention_pct}% tỉnh giữ profile; luồng chuyển lớn nhất là {from_profile} → {to_profile} với {n_flow} tỉnh.`

## 8. Phương pháp phải công bố

- Chỉ tỉnh đủ dữ liệu ở cả hai mốc mới vào phân tích thay đổi và cluster transition.
- Chuẩn hóa z-score riêng trong từng năm trước khi pool hai mốc.
- K tự động chọn trong 2–6 theo silhouette; người dùng có thể phê duyệt K cụ thể.
- KMeans dùng `n_init=50`, `random_state=42`.
- Nhãn A–F chỉ ổn định trong truy vấn hiện tại, không phải xếp hạng.
- PCA chỉ là phép chiếu; PC1/PC2 không thay thế dữ liệu 6–8 lĩnh vực.
- Profile mô tả tương đồng, không chứng minh nguyên nhân hay mô hình quản trị chính thức.

## 9. Bảng kiểm chứng

Dưới grid có một `<details>` duy nhất:

- search tỉnh;
- sort tỉnh, điểm đầu, điểm cuối, delta, profile đầu/cuối;
- highlight tỉnh/luồng đang chọn;
- export không thuộc MVP nếu chưa có yêu cầu;
- bảng không được tính là biểu đồ thứ năm.

## 10. Acceptance criteria

- Đúng bốn chart chính; hợp nhất hai bar tăng/giảm thành dumbbell.
- Small multiples dùng z-score cùng domain, không dùng màu lĩnh vực lẫn với màu profile.
- PCA công bố phương sai giải thích và không gán ý nghĩa tốt/xấu cho trục.
- Sankey chỉ dùng transition thật và có bảng fallback.
- Cả bốn chart mở được trong popup xem riêng; thao tác mở không chạy lại KMeans/PCA.
- Insight phân biệt rõ thay đổi tổng điểm, dịch chuyển PCA và đổi profile.

## 11. Contract triển khai

`GET /api/v1/dynamics` trả đúng artifact cho bốn card:

- `changes.rows/top8/bottom8`: điểm hai mốc và delta dùng để hợp nhất thành dumbbell cực trị.
- `clusterModel.centroids`: z-score, điểm gốc và cỡ mẫu đầu/cuối cho small multiples.
- `clusterModel.assignments`: profile, tọa độ hai mốc và `pcaDistance` của từng tỉnh.
- `clusterModel.transitions`: số tỉnh, tỷ lệ `share` và danh sách tỉnh của từng luồng thật.
- `clusterModel.changedN/changedPct`, `retainedN/retentionPct`, `farthestProvince/farthestDistance`
  cùng `insights.change/profiles/pca/transition`: thống kê và bốn kết luận xác định từ artifact đã xử lý.

Sankey dùng bundle Plotly riêng được lazy-load, không đưa trace flow vào bundle Cartesian của bốn trang
còn lại. Profile, tỉnh, luồng và popup được giữ trong URL; mở popup hoặc thay selection chỉ mã hóa lại
artifact đã nhận, không chạy lại KMeans/PCA. Trang không có khối “Bước đọc tiếp”; điều hướng nằm ở
sidebar. Mở trang không gọi API AI và không thực thi code.
