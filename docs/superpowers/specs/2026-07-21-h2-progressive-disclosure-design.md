# H2 progressive-disclosure design

## Goal

Biến H2 từ một trang 8 biểu đồ thành luồng đọc ngắn, ưu tiên phản hồi ngay khi
chọn tỉnh và chỉ mở phân tích phụ khi người dùng cần.

## Layout

1. Controls, KPI, map và chip tỉnh đang chọn.
2. Drill-down của tỉnh được chọn: ranking vùng và radar, ngay sau map.
3. So sánh vùng: giữ boxplot; bỏ regional mean bar trùng KPI.
4. Tabs “Cực trị” và “Thay đổi”: top/bottom 5 + outlier; delta horizontal bar
   cho 7 tăng/giảm tuyệt đối lớn nhất. Không còn slopegraph toàn bộ tỉnh.

## Interaction

- Map click và selectbox đồng bộ region/province.
- URL lưu thước đo, năm, vùng và tỉnh để share/reload tái tạo được.
- Chip gần map xác nhận đối tượng đang xem; selected province được tô nổi bật
  ở ranking/radar, không suy diễn nguyên nhân từ dữ liệu.

## Constraints

- Chỉ đọc processed data, giữ contract H2 6/8 thước đo và missing-data policy.
- Không đổi AI/log/data pipeline hoặc public `app/lib` contract nếu không cần.
- TDD cho helper chọn delta và AppTest cho URL/default/tabs; test toàn bộ suite.
- Chrome DevTools inspect chạy headless qua Xvfb; không dùng Chrome profile/cookie.
