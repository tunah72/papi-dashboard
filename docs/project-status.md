# Trạng thái dự án

Ngày rà soát: **17/07/2026**
Nhánh/commit được kiểm tra: `main` tại `265ebb858a61b1f71808ba0616cf9d151094418c`

Trạng thái dưới đây được suy ra từ code, dữ liệu và test trong repository; không lấy checkbox của các
kế hoạch cũ làm bằng chứng.

## Tóm tắt

| Khối | Trạng thái | Bằng chứng chính |
|---|---|---|
| Dữ liệu raw → processed | Hoàn thiện, có thể chạy lại | `src/build_dataset.py`, `src/papi_lib.py`, `data/processed/` |
| Data understanding và EDA | Hoàn thiện ở mức hiện tại | 3 notebook, 5 hình EDA, tài liệu trong `docs/data/` |
| Tổng quan dashboard | Đã triển khai | `app/pages/overview.py` |
| H1 — Diễn biến theo thời gian | Đã triển khai và có test logic | `app/pages/time_trend.py`, `src/analysis/trend.py` |
| H2 — So sánh tỉnh | Stub | `app/pages/provincial.py` chỉ hiển thị thông báo |
| H3 — Phân tích theo lĩnh vực | Stub | `app/pages/dimension.py` chỉ hiển thị thông báo |
| H4 — Động lực và phân nhóm | Stub | `app/pages/dynamics.py` chỉ hiển thị thông báo |
| AI Assistant | Đã có luồng chính, còn gap tuân thủ/log | `app/pages/ai_assistant.py`, `app/ai/` |
| Test offline | 45 test đạt | `.venv/bin/python -m pytest -q` |
| Báo cáo LaTeX | Khung ban đầu | `report/main.tex`, nội dung ngắn trong `report/content/` |
| Chuẩn bị vấn đáp | Chưa có bộ bằng chứng hoàn chỉnh | chưa có log/ảnh demo được tuyển chọn trong repo |

## Dữ liệu đã xác minh

- `fact`: 6.094 dòng × 4 cột.
- `prov_year`: 882 dòng (63 tỉnh × 14 năm) × 19 cột.
- `national`: 112 dòng (14 năm × 8 lĩnh vực) × 6 cột.
- 63 `province_id` duy nhất, năm từ 2011 đến 2024.
- 13 tỉnh-năm thiếu `total_papi`, được giữ là `NaN`.
- GeoJSON có 64 feature record nhưng chỉ 63 `province_id` duy nhất; ID `49` xuất hiện hai lần.

Số liệu xử lý chi tiết nằm trong [processing-log.md](data/processing-log.md). Việc lặp feature
GeoJSON chưa được sửa trong đợt tài liệu này vì đó là thay đổi dữ liệu cần được kiểm tra riêng.

## Dashboard đang chạy thật

Trang Tổng quan có bộ chọn năm, KPI, choropleth và top/bottom 10. Trang H1 có hai chế độ 6/8 lĩnh
vực, chọn khoảng năm, KPI, xu hướng tổng, so sánh trước/sau COVID, heatmap và click-to-drill.

H2–H4 vẫn được đăng ký trong menu nhưng mỗi file chỉ có 13 dòng, publish context `status: stub` và
hiển thị “Trang đang được phát triển”. Không nên trình bày đây là dashboard bốn hướng hoàn chỉnh.

## AI đang chạy thật

Đã có:

- gọi Groq và parse/chuẩn hóa code;
- hiển thị code và giải thích trước khi thực thi;
- cho phép người dùng sửa code và hiển thị diff trong log;
- chỉ thực thi khi bấm nút phê duyệt;
- process riêng, timeout 8 giây, giới hạn stdout;
- năm lựa chọn registry, trong đó bốn plugin tương ứng bốn hướng phân tích;
- context thật từ Overview và H1;
- test offline cho parser, executor, UI state và các guard chính.

Chưa đạt đầy đủ yêu cầu đề bài:

- yêu cầu/code chỉ sinh nhưng chưa thực thi chưa được log;
- log chưa lưu nội dung đầy đủ của bảng kết quả hoặc artifact biểu đồ;
- ba page stub chưa gửi context phân tích thật;
- chưa có live smoke test Groq được ghi nhận trong repo;
- executor là guard local, không phải sandbox bảo mật cho môi trường public;
- object không phải DataFrame, gồm GeoJSON, chưa được copy trước khi chạy code.

## Các rủi ro cần xử lý trước demo

1. **Phạm vi sản phẩm chưa đủ:** ba trong bốn hướng phân tích vẫn là stub.
2. **Bằng chứng human-in-the-loop chưa đủ:** log chưa bao phủ toàn bộ vòng đời và output đầy đủ.
3. **Dữ liệu bản đồ cần kiểm tra:** GeoJSON có một ID feature bị lặp.
4. **Báo cáo chưa theo kịp code:** nội dung LaTeX hiện quá ngắn và chưa mô tả quá trình dùng AI.
Thứ tự giải quyết và tiêu chí hoàn thành nằm trong [roadmap.md](roadmap.md).
