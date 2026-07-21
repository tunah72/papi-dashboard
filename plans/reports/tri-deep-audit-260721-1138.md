---
date: 2026-07-21
scope: Rà soát sâu nhánh feature/task/Tri và điểm tích hợp với main
method: So sánh ba chiều Git, đọc luồng H2/AI/log/report, kiểm tra build LaTeX trong bản archive tạm
---

# Rà soát sâu phần việc còn tồn tại của Lê Xuân Trí

## Kết luận điều hành

Phần H2, log AI và draft báo cáo của Trí **không phải thiếu code**; vấn đề chính là một deliverable lớn, làm trên baseline ngày 21/06, nằm trọn ở `feature/task/Tri` và chưa được tích hợp an toàn vào `main` ngày 17/07. Không được merge nguyên nhánh.

Nhánh có H2 gần đủ chức năng và report PAPI build được. Nhưng chưa có bằng chứng test/runtime trong môi trường hiện tại, chưa review/merge, chưa có demo AI live/log thật, và còn nhiều yêu cầu human-in-the-loop chưa được log đến mức event.

## Bằng chứng mới

- `git merge-tree` báo `app/pages/provincial.py` có conflict thật; `app/pages/ai_assistant.py` bị thay đổi ở cả hai nhánh. `api_logs.py` cũng bị thay đổi mạnh.
- Phần chênh giữa `main` và nhánh Trí: `api_logs.py` 181 thêm/2 xóa, `ai_assistant.py` 95 thêm/46 xóa, `provincial.py` 244 thêm/189 xóa. Đây không phải PR đơn chức năng.
- Bản report trên nhánh Trí đã được archive sang thư mục tạm và chạy `pdflatex → bibtex → pdflatex ×2`: build thành công, không còn warning/error ở pass cuối. Nhận định đúng là: **draft branch build được; source report trên main lại chưa input các section đó**.
- `pytest -q` ở interpreter audit không chạy do thiếu `pandas`/`numpy`; vì vậy không có xác nhận runtime mới cho main hoặc branch.

## Các vấn đề cần xử lý

| Mức | Vấn đề | Bằng chứng | Hành động cần làm |
|---|---|---|---|
| Blocker | Nhánh không thể merge nguyên khối | H2 conflict; AI Assistant changed-in-both; code branch dựa trên commit 34b0bae, sau đó main có chuỗi fix 17/07 | Tạo PR/commit nhỏ: (1) H2, (2) test H2, (3) report, (4) AI/log nếu còn cần. Resolve và review từng phần. |
| Blocker | Có hai H2 cạnh tranh | Nhánh Trí: `spatial.py` + map/top-bottom/slope/outlier; main: `provincial.py` + benchmark vùng/radar | Chốt owner/design: giữ H2 main rồi port feature có giá trị từ Trí, hoặc thay bằng H2 Trí sau review. Không duy trì hai module. |
| High | DoD “click bản đồ → drill tỉnh” chưa đạt | H2 nhánh Trí chỉ render map qua `layout.chart(fig_map)`; drill là `st.selectbox`; không có `on_select`/selection handler | Hoặc implement click-to-drill, hoặc chính thức sửa spec/DoD để selectbox là tương tác thay thế. |
| High | Không có UI test cho H2 | Có `tests/test_spatial.py` cho helper, nhưng không có `AppTest`/smoke test cho `provincial.py` | Thêm AppTest boot và case filter 6/8 lĩnh vực, vùng rỗng, tỉnh/năm thiếu dữ liệu; smoke Streamlit với data thật. |
| High | Nhật ký AI chưa đủ vòng đời | Nhánh Trí log generation và execution, nhưng không có event riêng khi user sửa code hoặc khi user phê duyệt; nếu sửa rồi rời trang, code sửa không được lưu | Log `edited` (kèm code/diff) và `approved` trước execution; test các đường không chạy/failed/reset. |
| High | Artifact biểu đồ chưa đạt yêu cầu truy xuất đã viết trong roadmap | Nhánh có path JSON Plotly theo `request_id`, nhưng không có checksum; main hiện chỉ log shape/type | Lưu artifact + checksum + metadata, hoặc giới hạn rõ scope demo. Đọc lại artifact từ log trong test. |
| High | AI executor vẫn nhận GeoJSON gốc không copy | `_make_globals` chỉ copy DataFrame, non-DataFrame được truyền reference; roadmap đã ghi rõ gap này | Deep-copy/loại GeoJSON khỏi executor; thêm test không thể mutate input. Đây là khoảng hở của khối AI Trí tham gia, dù không do commit H2 gây ra. |
| Medium | Chưa có bằng chứng yêu cầu AI khi vấn đáp | Không có live Groq log, log 4 plugin, case code sửa, case lỗi runtime hay dry-run nhóm | Chạy UI thật có kiểm soát, lưu JSONL/artifact/ảnh đã che secret; chuẩn bị 4 prompt và fallback rõ nguồn. |
| Medium | Offline proposal chỉ hợp lệ khi minh bạch | `demo_proposals.py` tạo code deterministic; UI branch có nhãn `offline_demo` | Giữ nhãn này ở mọi UI/log/report, không gọi đó là code sinh live hay dùng để bịa kết quả. |
| Medium | Số liệu H2 trong report chưa có test/artefact liên kết | `h2_provincial.tex` hard-code số liệu 2024; không có test snapshot hoặc figure/log gắn với các số đó | Tái tạo số liệu từ processed data bằng script/test, lưu bảng nguồn hoặc figure, rồi mới dùng trong report. |
| Medium | Tài liệu tiến độ trên nhánh tự mâu thuẫn và đã cũ | `progress_tracker.md` ghi nguồn thật là `main` 34b0bae, nhưng commit sau đó vẫn nằm riêng; `team-guide`/roadmap main cũng cũ so với code | Không dùng tracker của Trí làm nguồn thật. Sau khi tích hợp, cập nhật duy nhất `docs/project-status.md`, `docs/roadmap.md`, `docs/guides/team-guide.md`. |
| Low | Vệ sinh diff chưa đạt | `git diff --check main...feature/task/Tri` báo trailing whitespace ở 4 file docs | Sửa trước PR. |
| Low | Scope dependency không đúng | Nhánh thêm `pytest` vào `requirements.txt`, trong khi main đã đặt trong `requirements-dev.txt` | Giữ pytest ở dev requirements; không đưa test dependency vào runtime trừ khi có lý do rõ ràng. |

## H2 branch Trí: phần nào tốt để giữ

- `spatial.py` tách logic khỏi Streamlit, có validate input, tránh mutate khi lọc và có test edge case cho NaN, outlier variance bằng 0, mốc năm sai và top/bottom dataset nhỏ.
- Page có map, top/bottom, boxplot, outlier và slopegraph — các phần còn thiếu trong H2 main.
- `dash_context` mô tả filter, cột điểm và phương pháp outlier, tốt hơn context stub cũ.
- Report branch đã loại nội dung CO2 cũ và build PDF được; nên port bằng commit tài liệu riêng sau khi số liệu được tái xác nhận.

## Quy trình khép phần việc của Trí

1. Chốt thiết kế H2 trong một cuộc review ngắn, ghi quyết định.
2. Port chức năng H2 được chọn vào implementation duy nhất, giữ/viết test tương ứng.
3. Chạy test trong venv dự án và AppTest + smoke test H2.
4. Tích hợp log/artifact theo event lifecycle, không overwrite fix log 17/07.
5. Tái tạo số liệu report H2 từ data thật; port report và build PDF sạch.
6. Tạo bằng chứng demo AI thật, review chéo và merge PR nhỏ.
7. Cập nhật trạng thái/roadmap theo commit và test đã có, không theo checkbox tự khai.

## Câu hỏi cần chốt

- Có chấp nhận selectbox làm drill-down H2 hay bắt buộc click trực tiếp trên choropleth?
- Nhóm muốn dùng code H2 main hay H2 nhánh Trí làm nền tích hợp?
- Phần AI/log của Trí có nằm trong scope chính thức để port, hay chỉ giữ H2 và report?
