# Đặc tả thiết kế lại PAPI Dashboard

Thư mục này là nguồn sự thật cho lần thiết kế lại năm trang Dashboard React. Đặc tả tập trung vào
kiến trúc thông tin, layout, lựa chọn biểu đồ, insight dưới biểu đồ và interaction; chưa phải bằng
chứng rằng giao diện đã được triển khai.

Tài liệu dữ liệu chuẩn: [`../data/README.md`](../data/README.md). Khi đặc tả và dữ liệu mâu thuẫn,
phải sửa đặc tả theo dữ liệu, không tự tạo thêm số liệu hoặc biến phân tích ở frontend.

## 1. Mục tiêu sản phẩm

Dashboard giúp người xem đi từ bức tranh chung đến bốn hướng phân tích:

1. **Diễn biến:** điểm thay đổi khi nào và theo hướng nào?
2. **Vùng và tỉnh:** khác biệt nằm ở đâu, một tỉnh đứng ở vị trí nào?
3. **Mối quan hệ lĩnh vực:** các lĩnh vực có cùng biến thiên không, tỉnh nào là ngoại lệ?
4. **Thay đổi và phân nhóm:** tỉnh nào chuyển biến mạnh và các profile PAPI khác nhau thế nào?

Trang Tổng quan chỉ tóm tắt bốn hướng bằng bốn hình thức trực quan ngắn. Nó không sao chép các biểu
đồ chi tiết của bốn trang phân tích.

## 2. Danh mục tài liệu

- [`layout_interaction.md`](layout_interaction.md): hệ layout, card, insight, màu, typography,
  interaction, accessibility và trạng thái.
- [`chart_focus_mode.md`](chart_focus_mode.md): nút phóng to trên mỗi chart card, popup xem riêng,
  responsive, accessibility và đồng bộ trạng thái.
- [`floating_ai_assistant.md`](floating_ai_assistant.md): launcher dùng chung, dialog/bottom sheet,
  state human-in-the-loop, URL, responsive và accessibility.
- [`overview.md`](overview.md): trang Tổng quan.
- [`time_series.md`](time_series.md): trang Diễn biến theo thời gian.
- [`regional_province.md`](regional_province.md): trang Khác biệt giữa vùng và tỉnh.
- [`dimension_relationships.md`](dimension_relationships.md): trang Mối quan hệ giữa các lĩnh vực.
- [`dynamics_clustering.md`](dynamics_clustering.md): trang Sự thay đổi và phân nhóm.

## 3. Ma trận 20 biểu đồ

| Trang | Biểu đồ 1 | Biểu đồ 2 | Biểu đồ 3 | Biểu đồ 4 |
|---|---|---|---|---|
| Tổng quan | Choropleth | Waterfall thay đổi năm | Thanh chồng 100% bốn góc | Histogram mức thay đổi tỉnh |
| Diễn biến | Line chart đa chuỗi | Heatmap thay đổi năm-kề-năm | Bump chart thứ hạng vùng | Slopegraph lĩnh vực |
| Vùng và tỉnh | Boxplot + beeswarm | Lollipop xếp hạng | Bullet benchmark | Radar profile |
| Quan hệ lĩnh vực | Correlation heatmap | Scatter + hồi quy | Residual forest plot | Mean ± SD range plot |
| Thay đổi và phân nhóm | Dumbbell đầu–cuối | Small multiples diverging bar | PCA trajectory scatter | Sankey chuyển profile |

Toàn bộ Dashboard dùng 16 hình thức trực quan khác nhau. Hai nhóm được lặp có chủ đích:

- **Heatmap:** trang Diễn biến mã hóa vùng × năm bằng mức thay đổi; trang Quan hệ mã hóa lĩnh vực ×
  lĩnh vực bằng tương quan. Hai ma trận có ngữ nghĩa và thang màu khác nhau.
- **Scatter:** trang Quan hệ dùng trục là điểm PAPI thật và đường hồi quy; trang Phân nhóm dùng trục
  PCA không có đơn vị và đoạn nối đầu–cuối. Hai biểu đồ không thể thay thế lẫn nhau.

## 4. Nguyên tắc chọn biểu đồ

1. Một biểu đồ chỉ tồn tại khi trả lời một câu hỏi phân tích xác định.
2. So sánh giá trị chính xác ưu tiên vị trí trên cùng một trục: dot, lollipop, bar, dumbbell.
3. Xu hướng theo thời gian ưu tiên line, bump hoặc waterfall; không dùng bar cho chuỗi dài 14 năm.
4. Ma trận hai chiều mới dùng heatmap; không dùng heatmap chỉ để tạo màu sắc.
5. Bản đồ chỉ xuất hiện một lần ở Tổng quan để trả lời câu hỏi địa lý.
6. Radar chỉ xuất hiện ở profile một tỉnh, tối đa ba chuỗi và 6–8 trục; luôn có bảng dữ liệu thay thế.
7. Sankey chỉ dùng vì dữ liệu có luồng chuyển profile thật giữa hai mốc; không dùng để trang trí.
8. Không dùng pie/donut, biểu đồ 3D, hai trục tung hoặc animation liên tục.

## 5. Luồng đọc thống nhất của mỗi trang

```text
Tên trang + mô tả một câu, không kèm lại phạm vi/năm/n đã có trong filter
    → bộ lọc gọn và trạng thái đang xem
    → bốn KPI cùng chiều cao
    → grid 2 × 2 gồm đúng bốn chart card
         ├── câu hỏi phân tích
         ├── nút phóng to mở chart trong popup xem riêng
         ├── biểu đồ, không thêm dòng hướng dẫn cách đọc
         ├── Insight động trả lời câu hỏi
         └── nguồn, đơn vị, n và lưu ý
    → bảng dữ liệu/progressive disclosure nếu cần
```

Không đặt một khối “Tín hiệu cần đọc” lớn trước grid. Bốn insight phải nằm ngay dưới bốn biểu đồ để
người xem không phải ghép kết luận với một hình ở vị trí khác.

Không đặt khối hoặc CTA “Bước đọc tiếp” ở cuối trang. Người dùng chuyển trang qua sidebar hoặc
interaction drill-through có ngữ cảnh ngay trên biểu đồ; Trợ lý AI mở từ floating launcher dùng chung.

## 6. Phạm vi implementation

- Giữ React + TypeScript strict, FastAPI local, React Router và Plotly.
- Frontend không tự sửa dữ liệu nguồn hoặc tính một định nghĩa nghiệp vụ mới.
- Insight động phải được backend/view-model trả về hoặc được tạo từ cùng artifact bằng hàm đã test;
  không hard-code một tỉnh/năm cụ thể.
- Các lựa chọn phải phản ánh trên URL để refresh, chia sẻ link và drill-through không mất ngữ cảnh.
- Module AI đứng ngoài bốn chart card và không làm đổi grid. Mọi code AI sinh ra phải hiển thị đầy đủ ở
  trạng thái chờ duyệt; revision sinh toàn bộ code mới và chỉ proposal mới nhất được chạy local sau duyệt.

### Khoảng trống cần xử lý khi triển khai

| Hạng mục | Hiện có | Cần bổ sung |
|---|---|---|
| Tổng quan | map, trend, strongest pair, toàn bộ delta tỉnh | annual delta summary, quadrant counts và histogram summary trong view-model |
| Diễn biến | total/regional series, vùng năm-kề-năm, delta lĩnh vực | hạng vùng theo năm cho bump chart và insight bốn chart |
| Vùng và tỉnh | distribution, ranking, benchmark, profile | `regionMeans.q1/q3/iqr`, range toàn mẫu và bốn insight nằm trong contract FastAPI |
| Quan hệ | matrix, pair, OLS, residual, mean/SD, min/max, n từng cặp và bốn insight | — đã đủ contract cho bốn card |
| Phân nhóm | change rows, centroid, PCA assignment/distance, transition/share, retention và bốn insight | — đã đủ contract cho bốn card |
| Chart component | click, hover/unhover, responsive, bảng fallback, `ChartInsight`, `ChartFocusDialog`, waterfall/polar/Sankey lazy bundle | selected/legend events chuyên biệt khi từng chart cần |

Các thống kê trên nên được tính ở `src/analysis`/FastAPI và có test. Frontend chỉ mã hóa artifact thành
biểu đồ và quản lý interaction; không sao chép công thức nghiệp vụ vào page component.

## 7. Tiêu chí hoàn thành cấp Dashboard

- Mỗi trang có đúng bốn biểu đồ chính và bốn insight tương ứng.
- Ở viewport 1440 × 900, người xem thấy header, filter, KPI và phần lớn hàng biểu đồ đầu tiên.
- Bốn card tạo thành hai hàng cân bằng; không có chart toàn chiều ngang đẩy nội dung còn lại xuống sâu.
- Mọi biểu đồ có tooltip, trạng thái hover/selected/focus và bảng tóm tắt truy cập được.
- Mọi chart card có nút phóng to; popup giữ nguyên filter, selection, insight, nguồn và `n`, đồng thời
  đóng được bằng bàn phím mà không làm mất vị trí đọc.
- Màu lĩnh vực/vùng nhất quán; tăng/giảm còn được phân biệt bằng dấu, nhãn hoặc kiểu nét.
- Không so tổng 6 lĩnh vực với tổng 8 lĩnh vực qua mốc 2018.
- Không diễn giải tương quan, hồi quy hoặc phân cụm thành quan hệ nhân quả hay xếp hạng chính thức.
