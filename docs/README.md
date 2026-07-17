# Tài liệu PAPI Dashboard

Đây là điểm bắt đầu duy nhất cho tài liệu dự án. Tài liệu được chia theo mục đích để tránh nhầm kế
hoạch lịch sử với trạng thái code hiện tại.

## Đọc theo thứ tự

1. [Trạng thái dự án](project-status.md) — phần nào chạy thật, phần nào là stub, các khoảng trống.
2. [Kiến trúc thực tế](architecture.md) — data flow, dashboard, AI và ranh giới kỹ thuật.
3. [Hướng dẫn cài đặt và phát triển](guides/getting-started.md) — lệnh chạy, test và quy trình sửa đổi.
4. [Roadmap](roadmap.md) — thứ tự công việc còn lại trước demo/vấn đáp.

## Theo chủ đề

### Dữ liệu và phân tích

- [Tổng quan tài liệu dữ liệu](data/README.md)
- [Tìm hiểu 14 file PAPI nguồn](data/data-understanding.md)
- [Schema dataset đã xử lý](data/processed-dataset.md)
- [Nhật ký pipeline gần nhất](data/processing-log.md)
- [Phát hiện EDA](data/eda-findings.md)

### Dashboard và làm việc nhóm

- [Quy ước thiết kế](guides/design-system.md)
- [Hướng dẫn thành viên](guides/team-guide.md)

### AI

- [Thiết kế và trạng thái AI human-in-the-loop](ai/README.md)
- [Manual test cases](ai/manual-test-cases.md)

### Tài liệu lịch sử

Các kế hoạch/checklist tháng 06/2026 nằm trong [archive](archive/README.md). Chúng được giữ để truy
vết quyết định ban đầu, không phải nguồn sự thật về tiến độ hiện tại.

## Quy ước duy trì

- `project-status.md` phản ánh code trên `main` và phải được cập nhật khi một chức năng đổi trạng thái.
- `roadmap.md` chỉ giữ công việc chưa hoàn tất hoặc đang thực hiện.
- Nhật ký pipeline do `src/build_dataset.py` tạo; không sửa số liệu trong log bằng tay.
- Tài liệu đã hết hiệu lực chuyển vào `archive/`, không để song song với tài liệu hiện hành.
- README gốc chỉ là trang giới thiệu và đường dẫn; chi tiết kỹ thuật nằm trong `docs/`.
