# Hướng dẫn làm việc nhóm

## Nguồn sự thật

- Trạng thái code: [project-status.md](../project-status.md).
- Việc tiếp theo: [roadmap.md](../roadmap.md).
- Kiến trúc: [architecture.md](../architecture.md).
- Quy ước giao diện: [design-system.md](design-system.md).
- Kế hoạch tháng 06/2026 chỉ dùng để tham khảo lịch sử trong `docs/archive/`.

Không đánh dấu một hạng mục “xong” chỉ vì file hoặc plugin đã tồn tại. Một trang chỉ hoàn thiện khi có
nội dung thật, test logic, boot được và được kiểm tra bằng dữ liệu thực.

## Phân công theo vertical slice

| Thành viên | Hướng | Page | Analysis module | AI technique | Trạng thái 17/07 |
|---|---|---|---|---|---|
| Dương Tuấn Anh | H1 Xu hướng | `time_trend.py` | `trend.py` | `trend_classification.py` | Page + logic + plugin đã có |
| Lê Xuân Trí | H2 So sánh tỉnh | `provincial.py` | `spatial.py` | `anomaly.py` | Page/module chưa có; plugin đã có |
| Nguyễn Trần Trung Kiên | H3 Theo lĩnh vực | `dimension.py` | `dimension.py` | `insight.py` | Page/module chưa có; plugin đã có |
| Lê Đức Phúc | H4 Động lực/phân nhóm | `dynamics.py` | `dynamics.py` | `clustering.py` | Page/module chưa có; plugin đã có |

Các module H2–H4 trong bảng là đích cần tạo, không phải file đang tồn tại.

## Definition of Done cho một trang phân tích

- Có câu hỏi phân tích rõ và dùng đúng grain dữ liệu.
- Có control/filter phù hợp, KPI và ít nhất ba biểu đồ có vai trò khác nhau.
- Tiêu đề/nhận xét bám số liệu; luôn ghi nguồn và xử lý dữ liệu thiếu.
- Tên lĩnh vực hiển thị đầy đủ, palette và layout theo design system.
- Logic thống kê/phân tích được tách khỏi Streamlit và có unit test.
- Có ít nhất một tương tác có ý nghĩa.
- Publish `dash_context` đủ cụ thể để AI Assistant hiểu page/filter/chart.
- Page boot sạch và toàn bộ test repository vẫn đạt.
- `project-status.md`/`roadmap.md` được cập nhật theo bằng chứng thực tế.

## Phạm vi file

Mỗi vertical slice ưu tiên sửa page và analysis module của mình. Chỉ sửa `app/lib/`, theme hoặc bảng
lookup dùng chung khi thay đổi đã được thống nhất và có kiểm tra hồi quy. Không đổi chữ ký helper đang
được page khác dùng nếu chưa cập nhật tất cả call site.

## Git và review

- Một branch cho một mục tiêu nhỏ: `feat/<scope>` hoặc `docs/<scope>`.
- Commit file liên quan trực tiếp; không đưa secrets, log phiên hay cache vào commit.
- PR mô tả dữ liệu dùng, hành vi trước/sau, test đã chạy và hạn chế còn lại.
- Reviewer kiểm tra code/data/UI thật; không dựa vào checkbox hoặc ảnh chụp duy nhất.
