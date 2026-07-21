# Tài liệu PAPI Dashboard

Đây là điểm bắt đầu duy nhất cho tài liệu dự án. Tài liệu được chia theo mục đích để tránh nhầm kế
hoạch lịch sử với trạng thái code hiện tại.

## Thứ bậc authority

Khi có mâu thuẫn, ưu tiên **code/runtime/test hiện tại** → ADR và parity matrix migration → status docs
hiện hành → `archive/`. Các trang trạng thái là snapshot; archive chỉ để truy vết, không phải bằng chứng
về tính năng đang chạy.

## Đọc theo thứ tự

1. [Trạng thái dự án](project-status.md) — baseline code/test hiện tại và các khoảng trống trước cutover.
2. [Kiến trúc thực tế](architecture.md) — data flow, dashboard, AI và ranh giới kỹ thuật.
3. [Hướng dẫn cài đặt và phát triển](guides/getting-started.md) — lệnh chạy, test và quy trình sửa đổi.
4. [Roadmap migration](roadmap.md) — trạng thái và thứ tự Phase 0–6 đến cutover React + FastAPI.
5. [ADR migration React + FastAPI](adr/2026-07-20-react-fastapi-local-migration.md) — quyết định kiến trúc, cutover và rollback.
6. [Ma trận parity React + FastAPI](react-fastapi-parity-matrix.md) — acceptance source cho năm trang và floating assistant trước cutover.

## Theo chủ đề

### Dữ liệu và phân tích

- [Nguồn gốc, nội dung, cách thu thập, xử lý và kết quả dữ liệu PAPI](data/README.md)
- [Nhật ký pipeline gần nhất](data/processing-log.md)

### Dashboard và làm việc nhóm

- [Đặc tả thiết kế lại năm trang Dashboard](design/README.md)
- [Quy ước thiết kế legacy Streamlit](guides/design-system.md)
- [Hướng dẫn thành viên](guides/team-guide.md)

### AI

- [Thiết kế và trạng thái AI human-in-the-loop](ai/README.md)
- [Execution contract Floating AI Assistant](ai/floating-ai-assistant-execution.md)
- [Manual test cases](ai/manual-test-cases.md)

### Tài liệu lịch sử

Các kế hoạch/checklist tháng 06/2026 nằm trong [archive](archive/README.md). Chúng được giữ để truy
vết quyết định ban đầu, không phải nguồn sự thật về tiến độ hiện tại.

## Quy ước duy trì

- `project-status.md` phản ánh code trên `main` và phải được cập nhật khi một chức năng đổi trạng thái.
- `roadmap.md` giữ trạng thái từng phase migration và các việc chưa hoàn tất; không lặp lại backlog legacy đã có code.
- Nhật ký pipeline do `src/build_dataset.py` tạo; không sửa số liệu trong log bằng tay.
- Tài liệu đã hết hiệu lực chuyển vào `archive/`, không để song song với tài liệu hiện hành.
- README gốc chỉ là trang giới thiệu và đường dẫn; chi tiết kỹ thuật nằm trong `docs/`.
