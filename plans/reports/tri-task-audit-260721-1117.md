---
date: 2026-07-21
scope: Nhiệm vụ của Lê Xuân Trí (H2 so sánh tỉnh, plugin anomaly và phần việc liên quan AI/log)
evidence: main, feature/task/Tri, lịch sử Git và kiểm tra tĩnh
---

# Đánh giá tiến độ nhiệm vụ của Lê Xuân Trí

## Tóm tắt

- Tiến độ phần code do Trí thực hiện: khoảng **75%**. Nhánh `feature/task/Tri` có trang H2 đầy đủ hơn, module `spatial`, test và phần log AI/báo cáo.
- Tiến độ được tích hợp vào sản phẩm `main`: khoảng **35%** đối với phần do Trí sở hữu, vì commit `90da9f9` chỉ nằm trên `feature/task/Tri`, chưa là tổ tiên của `main`.
- Tiến độ H2 hiện có trên `main`: khoảng **65%** so với checklist phân công. Nó do Tuấn Anh triển khai lại phần lớn; không được quy thành đóng góp đã merge của Trí.

Các tỷ lệ là ước lượng theo checklist phân công, không phải số dòng code.

## Bằng chứng đã kiểm tra

- Phân công chính thức: `docs/guides/team-guide.md` và `docs/archive/2026-06-initial-plans/work-assignment.md` giao Trí H2, `spatial.py`, plugin `anomaly.py`.
- Nhánh `feature/task/Tri` chứa commit `90da9f9` ngày 13/07/2026; `git merge-base --is-ancestor 90da9f9 HEAD` trả về 1. Vì vậy nhánh chưa merge vào `main`.
- `main` hiện có `app/pages/provincial.py`, `src/analysis/provincial.py`, `tests/test_provincial.py`, nhưng `git blame` quy 229/233 dòng page và toàn bộ 86 dòng analysis cho Tuấn Anh.
- Kiểm tra cú pháp `python3 -m compileall -q app src tests` đạt. `pytest -q` không thu thập được do interpreter toàn cục thiếu `pandas`/`numpy`; chưa thể xác nhận test runtime.

## Hạng mục hoàn thành

| Hạng mục | Trạng thái | Nhận xét |
|---|---|---|
| H2 page trên nhánh Trí | Có | Có choropleth, top/bottom, boxplot vùng, outlier z-score, slopegraph, drill tỉnh, radar và `dash_context`. |
| Logic `spatial.py` trên nhánh Trí | Có | Có lọc năm/vùng, xếp hạng, top-bottom, summary vùng, outlier, pair hai mốc và profile tỉnh. |
| Unit test H2 trên nhánh Trí | Có | `tests/test_spatial.py` kiểm tra các helper và edge case chính. |
| Plugin `anomaly.py` | Có trên `main` | Prompt hướng dẫn z-score và yêu cầu `.copy()`; chưa có test riêng hiện hành. |
| H2 trên `main` | Có một phần | Có control, KPI, boxplot, trung bình vùng, ranking trong vùng, radar và nút AI; logic/test đã đổi tên sang `provincial.py`. |
| Đóng góp AI/log/báo cáo trong commit 90da9f9 | Có trên nhánh riêng | Chưa được merge; `main` đã có một chuỗi thay đổi log khác ngày 17/07. |

## Việc cần hoàn thành, theo thứ tự ưu tiên

1. **Quyết định tích hợp nhánh Trí.** Không merge thẳng: `feature/task/Tri` chạm 30 file, gồm H2, AI/log, báo cáo, requirements và nhiều tài liệu. Tách thành PR nhỏ hoặc cherry-pick chọn lọc sau khi so sánh với `main`.
2. **Chọn một implementation H2 làm nguồn thật duy nhất.** `main` và nhánh Trí có hai thiết kế/module khác nhau (`provincial.py` và `spatial.py`). Giữ một bản, port các tính năng còn thiếu có test từ bản kia; không để song song hai logic.
3. **Khép các gap H2 trên `main`:** bổ sung choropleth; top/bottom ở phạm vi phù hợp; slopegraph hai mốc; phát hiện outlier; drill từ bản đồ/biểu đồ theo đúng spec thay vì chỉ selectbox. Cập nhật test cho từng helper được port.
4. **Rà lại semantic của H2 hiện hành:** ranking hiện chỉ trong vùng đã chọn, không phải top/bottom toàn quốc như phân công ban đầu; cần chốt chủ ý UX và ghi rõ phạm vi trong nhãn/chart.
5. **Chạy test bằng môi trường dự án.** Cài dependencies theo `requirements-dev.txt` vào môi trường hợp lệ rồi chạy `pytest -q`; tiếp theo smoke test Streamlit với dữ liệu thật và ghi nhận H2 ở mode 6/8 lĩnh vực.
6. **Kiểm tra UI H2 thật.** Hiện không có AppTest/E2E cho page; cần kiểm tra filter năm, vùng, tỉnh, năm thiếu dữ liệu, 6/8 lĩnh vực, map và drill-down sau khi tích hợp.
7. **Sửa vệ sinh nhánh trước review.** `git diff --check main...feature/task/Tri` báo trailing whitespace ở bốn tài liệu. Các tài liệu báo cáo của nhánh cũng cần đối chiếu với report hiện tại để tránh đưa nội dung CO2 cũ vào báo cáo PAPI.
8. **Đồng bộ tài liệu nguồn sự thật.** `docs/project-status.md` và `docs/roadmap.md` đều vẫn mô tả H2 là stub/chưa làm, trái với code `main` hiện tại. Cập nhật chỉ sau khi đã chốt implementation và kiểm thử.
9. **Hoàn tất phần AI mà Trí chạm tới.** Nếu lấy phần log từ nhánh Trí, kiểm tra tương thích với các fix log ngày 17/07; không ghi đè cơ chế log proposal pending hiện tại. Cần log lifecycle và artifact/output theo roadmap, rồi chạy live smoke test có lưu bằng chứng.

## Rủi ro

- Merge commit lớn của nhánh Trí có khả năng ghi đè các cải tiến H2 và AI/log đã vào `main` sau 13/07.
- Không có test runtime đang chạy trong môi trường audit, nên không nên tuyên bố H2 hoặc AI đã pass.
- Báo cáo LaTeX hiện hành còn có nội dung CO2 không khớp đề tài PAPI; đây là blocker độc lập trước vấn đáp.

## Câu hỏi chưa giải quyết

- Nhóm muốn dùng H2 đầy đủ trên nhánh Trí làm nền hay giữ H2 hiện hành của Tuấn Anh và port chọn lọc tính năng?
- Các thay đổi AI/log và báo cáo trong nhánh Trí có được xem là nhiệm vụ chính thức của Trí hay là đóng góp bổ sung cần review riêng?
