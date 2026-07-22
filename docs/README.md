# Tài liệu PAPI Dashboard

Đây là điểm vào chính cho tài liệu đang dùng. Khi có mâu thuẫn, ưu tiên code/runtime/test hiện tại,
sau đó đến tài liệu dữ liệu và thiết kế, kiến trúc, rồi mới đến tài liệu lịch sử trong `archive/`.

## Bắt đầu

1. [Trạng thái dự án](project-status.md) — capability và bằng chứng kiểm thử hiện tại.
2. [Kiến trúc](architecture.md) — luồng dữ liệu, React, FastAPI, AI và Streamlit fallback.
3. [Cài đặt và phát triển](guides/getting-started.md) — lệnh chạy, test và quy tắc sửa đổi.
4. [Hướng dẫn demo/vấn đáp](dashboard-handoff.md) — mạch trình bày và checklist trước demo.

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
- [Design system Streamlit legacy](guides/design-system.md)
- [Quy ước báo cáo và slides](notes/NOTES.md)

### Quyết định và lịch sử

- [ADR React + FastAPI local](adr/2026-07-20-react-fastapi-local-migration.md)
- [Tài liệu lịch sử](archive/README.md) — chỉ dùng để truy vết, không dùng làm trạng thái hiện tại.

## Quy ước duy trì

- `project-status.md` chỉ ghi trạng thái đã kiểm chứng và kết quả test gần nhất.
- Thay đổi dữ liệu phải cập nhật `data/README.md` và để pipeline sinh `processing-log.md`.
- Thay đổi hành vi UI phải cập nhật đặc tả tương ứng trong `design/`.
- Thay đổi contract AI phải cập nhật `ai/README.md`, manual tests và OpenAPI schema.
- Tài liệu kế hoạch đã hoàn tất được tóm tắt trong `archive/`, không để lẫn với tài liệu vận hành.
