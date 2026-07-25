# Tài liệu PAPI Dashboard

Đây là điểm vào chính cho tài liệu đang dùng. Khi có mâu thuẫn, ưu tiên mã nguồn và kết quả chạy hiện
tại, sau đó đến tài liệu dữ liệu, thiết kế và kiến trúc.

## Bắt đầu

1. [Kiến trúc](architecture.md) — luồng dữ liệu, React, FastAPI và Trợ lý AI.
2. [Cài đặt và vận hành](guides/getting-started.md) — lệnh cài đặt, chạy và kiểm tra.

## Nguồn sự thật theo chủ đề

### Dữ liệu

- [Nguồn, định nghĩa và giới hạn dữ liệu PAPI](data/README.md)
- [Nhật ký pipeline](data/processing-log.md)

### Giao diện

- [Thiết kế tổng thể và ma trận 20 biểu đồ](design/README.md)
- [Chế độ phóng to biểu đồ](design/chart_focus_mode.md)
- [Floating AI Assistant](design/floating_ai_assistant.md)
- Các đặc tả trang nằm cùng thư mục `design/`.

### AI

- [AI human-in-the-loop](ai/README.md)
- [Manual test cases](ai/manual-test-cases.md)

### Làm việc nhóm

- [Hướng dẫn thành viên](guides/team-guide.md)
- [Quy ước báo cáo và slides](notes/NOTES.md)

## Quy ước duy trì

- Thay đổi dữ liệu phải cập nhật `data/README.md` và để pipeline sinh `processing-log.md`.
- Thay đổi hành vi UI phải cập nhật đặc tả tương ứng trong `design/`.
- Thay đổi contract AI phải cập nhật `ai/README.md`, manual tests và OpenAPI schema.
