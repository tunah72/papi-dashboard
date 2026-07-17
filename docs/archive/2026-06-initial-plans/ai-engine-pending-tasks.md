# Kế hoạch hoàn thiện AI Engine

Tài liệu này là backlog kỹ thuật cho phần AI Engine của dashboard PAPI. Mục tiêu là làm rõ phần còn thiếu để module AI đạt yêu cầu vấn đáp: AI chỉ đề xuất, con người xem/sửa/duyệt, code chạy local, kết quả và toàn bộ quá trình được log lại.

## 0. Trạng thái hiện tại

Đã có:
- `app/ai/api_ai.py`: gọi Groq, parse phản hồi, nhận `context`.
- `app/ai/api_exec.py`: thực thi code đã duyệt trong namespace hạn chế.
- `app/ai/api_logs.py`: ghi/đọc log dạng JSONL.
- `app/pages/ai_assistant.py`: luồng sinh code -> xem/sửa -> duyệt -> chạy -> hiển thị -> log.
- 4 plugin thật trong `app/ai/techniques/`: trend classification, anomaly, insight, clustering.
- `time_trend.py` đã publish `st.session_state["dash_context"]` làm mẫu.

Chưa đạt:
- Chưa có live smoke test Groq nếu máy chưa cấu hình `GROQ_API_KEY`.
- Các page stub (`provincial.py`, `dimension.py`, `dynamics.py`) mới publish context tối thiểu, chưa có context phân tích thật vì nội dung dashboard chưa hoàn thiện.
- Chưa có biên bản stress-test thủ công 4 plugin với log/ảnh chụp phục vụ vấn đáp.

## 1. Nguyên tắc bất biến

- Không thực thi ngầm: chỉ chạy code khi người dùng bấm "Phê duyệt và thực thi".
- Code AI sinh ra phải luôn hiển thị rõ và có thể sửa trước khi chạy.
- AI không được sửa dữ liệu gốc; code chạy trên bản sao dữ liệu.
- Mọi request, code AI, code đã chạy, giải thích, context, lỗi/kết quả phải được log.
- Không bịa số liệu/hình ảnh; mọi kết quả hiển thị phải đến từ dữ liệu local hoặc code đã duyệt.
- Ưu tiên giải pháp đơn giản, demo được, dễ giải thích khi vấn đáp.

## 2. Definition of Done tổng thể

AI Engine được xem là hoàn thiện khi:
- Người dùng có thể chọn ít nhất 4 plugin, sinh code, xem/sửa code, duyệt, chạy local và nhận `result` hoặc `fig`.
- Log thể hiện rõ vai trò con người: request, code AI, code đã chạy, diff nếu có sửa, context dashboard, lỗi/kết quả.
- Từ ít nhất một biểu đồ dashboard, người dùng bấm "Giải thích biểu đồ này" để mở AI Assistant với prompt đã được seed theo chart/filter hiện tại.
- Context từ dashboard được đưa vào prompt AI ở các trang đã triển khai thực tế.
- Output quá dài không làm UI quá tải; lỗi thực thi hiển thị rõ, không làm mất log.
- Có test offline cho parse response, execution guard cơ bản, và AppTest mock luồng AI Assistant.
- Có biên bản stress-test thủ công cho 4 plugin để dùng trong vấn đáp/báo cáo.

## 3. WP-Frontend: minh bạch human-in-the-loop

### Task 1.1: Diff log code AI vs code đã chạy

Mục tiêu: chứng minh người dùng có thể can thiệp trước khi chạy, và hệ thống ghi nhận thay đổi đó.

File chính:
- `app/pages/ai_assistant.py`
- `app/ai/api_logs.py` nếu cần thêm field tóm tắt

Cách làm:
- Tạo helper `render_diff(old_code, new_code)` trong `ai_assistant.py`.
- Dùng `difflib.unified_diff(old_code.splitlines(), new_code.splitlines(), fromfile="AI đề xuất", tofile="Đã chạy", lineterm="")`.
- Trong expander log, nếu `code_ai != code_run` thì hiển thị diff bằng `st.code(..., language="diff")`.
- Nếu không sửa, hiển thị "Người dùng không chỉnh sửa code trước khi duyệt."

Edge cases:
- Không mặc định `strip()` từng dòng trước khi diff, vì indentation là ngữ nghĩa trong Python. Nếu cần bỏ qua whitespace, chỉ dùng cho nhãn phụ như "chỉ khác khoảng trắng", không thay thế diff chính.
- Diff dài: đặt từng diff trong `st.expander("Xem thay đổi code")`, mặc định đóng.
- Log cũ thiếu `code_ai` hoặc `code_run`: bỏ qua diff và hiển thị "Log cũ không đủ dữ liệu để so sánh."

DoD:
- Sau khi người dùng sửa một dòng code rồi chạy, log hiển thị diff có dòng `-` và `+`.
- Sau khi chạy code không chỉnh sửa, log hiển thị rõ là không có sửa.
- Không làm hỏng việc đọc 10 log gần nhất.

### Task 1.2: Badge trạng thái code

Mục tiêu: trạng thái UI phản ánh đúng code đang ở giai đoạn nào.

File chính:
- `app/pages/ai_assistant.py`

Cách làm:
- Sau `st.text_area("Chỉnh sửa code trước khi duyệt", ...)`, so sánh `edited` với `st.session_state["ai_code"]`.
- Hiển thị một trong các trạng thái:
  - `Chờ duyệt - AI đề xuất` khi chưa sửa.
  - `Chờ duyệt - đã chỉnh sửa bởi người dùng` khi khác code AI.
  - `Đã thực thi` sau khi bấm duyệt và chạy xong.
- Lưu trạng thái thực thi gần nhất vào `st.session_state["ai_last_run_status"]` nếu cần.

Edge cases:
- Code chỉ khác newline cuối file: vẫn có thể xem là thay đổi nhẹ; không cần phức tạp hóa logic.
- Người dùng sinh code mới: reset trạng thái về "Chờ duyệt - AI đề xuất".

DoD:
- Sửa một ký tự trong text area làm badge đổi ngay sau rerun.
- Sinh code mới không giữ trạng thái "đã chỉnh sửa" của code cũ.
- Sau khi chạy, log vẫn ghi đúng `code_ai` và `code_run`.

### Task 1.3: Nút "Giải thích biểu đồ này"

Mục tiêu: liên kết dashboard và AI Assistant để AI hiểu người dùng đang hỏi về chart/filter nào.

File chính:
- `app/lib/layout.py`
- `app/pages/time_trend.py`
- `app/pages/ai_assistant.py`
- Các page dashboard còn lại khi đã có nội dung thật

Cách làm:
- Thêm helper `ai_explain_button(chart_id, description, context=None)` trong `layout.py`.
- Khi bấm:
  - set `st.session_state["ai_seed"]` bằng câu hỏi cụ thể, ví dụ: "Giải thích biểu đồ `<chart_id>`: `<description>`. Bám theo ngữ cảnh dashboard hiện tại..."
  - nếu có `context`, cập nhật `st.session_state["dash_context"]`.
  - gọi `st.switch_page("pages/ai_assistant.py")`.
- Trong `ai_assistant.py`, giá trị mặc định của ô request lấy từ `st.session_state.pop("ai_seed", default_req)`.

Edge cases:
- Không hiển thị nút nếu DataFrame nguồn rỗng hoặc chart không được render.
- `ai_seed` phải bị `pop` sau khi dùng để tránh quay lại AI Assistant bị lặp câu hỏi cũ.
- Nếu người dùng chọn plugin sau khi seed prompt, cần quyết định rõ: plugin override prompt, hoặc seed prompt ưu tiên. Đề xuất: seed prompt ưu tiên cho lần đầu vào trang; khi người dùng đổi plugin thì dùng `default_request` của plugin.

DoD:
- Từ ít nhất một chart trong `time_trend.py`, bấm nút sẽ mở AI Assistant với request đã điền sẵn.
- Reload/đi lại trang AI Assistant không còn giữ seed cũ sau khi đã lấy.
- Request sinh ra có nhắc chart/filter cụ thể, không phải câu hỏi chung chung.

## 4. WP-Context & Safety: ngữ cảnh và kiểm soát thực thi

### Task 2.1: Nhân rộng context-aware

Mục tiêu: AI nhận được filter/page/chart context đủ dùng, không chỉ schema dữ liệu.

File chính:
- `app/pages/overview.py`
- `app/pages/time_trend.py`
- `app/pages/provincial.py`
- `app/pages/dimension.py`
- `app/pages/dynamics.py`
- `app/ai/api_ai.py`

Cách làm:
- Chuẩn hóa schema context tối thiểu:
  - `page`: tên trang.
  - `filters`: dict các filter đang chọn, ví dụ `year`, `year_range`, `scale_mode`, `province`, `dimension`.
  - `data_scope`: mô tả bảng/cột chính đang dùng.
  - `chart_id`: optional, dùng khi bấm "Giải thích biểu đồ này".
- Mỗi page sau khi đọc filter phải set `st.session_state["dash_context"]`.
- Refactor `_format_context(context)` để xử lý linh hoạt:
  - dict lồng nhau.
  - list/tuple như `year_range`.
  - giá trị None.
  - log cũ có schema cũ (`scale_mode`, `total_col`, `dims` ở top-level).

Edge cases:
- Page stub chưa có chart/filter thật: chỉ publish context tối thiểu hoặc chưa cần làm cho đến khi page có nội dung.
- Stale context: cập nhật context ngay sau khi filter được chọn và trước khi render chart/nút AI.
- Context quá dài: chỉ đưa filter và mô tả bảng/cột liên quan, không dump DataFrame.

DoD:
- `time_trend.py` và `overview.py` có context thật.
- Các page đã hoàn thiện nội dung phải có context tương ứng trước khi demo.
- Unit test `_format_context` bao phủ: context rỗng, schema cũ, schema mới, `year` dạng int, `year_range` dạng list.

### Task 2.2: Giới hạn output thực thi

Mục tiêu: code AI không làm Streamlit bị nặng do `print()` quá dài hoặc kết quả quá lớn.

File chính:
- `app/ai/api_exec.py`
- `app/pages/ai_assistant.py`

Cách làm tối thiểu:
- Thêm hằng số `MAX_STDOUT_CHARS = 4000`.
- Sau khi chạy, nếu `stdout` dài hơn giới hạn thì cắt và thêm thông báo: `... [đã cắt stdout, xem log nếu cần]`.
- Khi hiển thị DataFrame quá lớn, chỉ render bằng `st.dataframe` bình thường nhưng thêm caption về số dòng/cột nếu `len(result)` lớn.

Cách làm tốt hơn nếu còn thời gian:
- Chạy code trong process riêng với timeout, ví dụ `multiprocessing`.
- Nếu quá timeout, terminate process và trả lỗi `TimeoutError`.
- Vẫn log request/code/error để chứng minh không thực thi ngầm và không mất dấu vết.

Edge cases:
- `while True: print(1)` không được giải quyết triệt để bằng cắt stdout nếu vẫn chạy trong cùng process. Cần timeout/process riêng nếu muốn kiểm soát kỹ thuật thật.
- Exception xảy ra trước khi gán `result`: vẫn phải trả `stdout` đã cắt và `error`.
- Code tạo `fig` lớn: hiển thị lỗi rõ nếu Plotly không render được.

DoD:
- `print("x" * 10000)` không làm UI hiển thị 10000 ký tự đầy đủ.
- Code lỗi vẫn log được `error`.
- Nếu triển khai timeout, `while True: pass` phải kết thúc bằng lỗi timeout thay vì treo app.

### Task 2.3: Làm rõ prompt safety cho AI sinh code

Mục tiêu: giảm xác suất model sinh code nguy hiểm hoặc không chạy được trong sandbox.

File chính:
- `app/ai/api_ai.py`

Cách làm:
- Bổ sung vào system prompt:
  - Không dùng vòng lặp vô hạn.
  - Không in toàn bộ DataFrame; nếu cần xem mẫu thì dùng `.head()`.
  - Không import, không đọc/ghi file, không gọi mạng.
  - Luôn gán `result`; nếu có chart thì gán `fig`.
  - Nếu dữ liệu không đủ, trả `result` là DataFrame giải thích lý do thay vì crash.

DoD:
- Prompt có nhắc rõ các giới hạn trên.
- Các plugin default request không yêu cầu import hoặc thao tác file.

## 5. WP-Testing: kiểm thử tự động và nghiệm thu thủ công

### Task 3.1: Unit test cho AI API

File chính:
- `tests/test_api_ai.py`

Cần có thêm:
- Test `_format_context` cho schema cũ và mới.
- Test `_parse_response` với JSON/fence/text thuần đã có thì giữ.

DoD:
- `python -m pytest tests/test_api_ai.py -q` xanh trong môi trường đã cài dependencies.
- Test không gọi Groq, không cần API key.

### Task 3.2: Unit test cho execution guard

File chính:
- `tests/test_api_exec.py`

Test cases:
- Code hợp lệ gán `result`.
- Code lỗi trả `error`, không raise ra ngoài.
- `stdout` quá dài bị cắt.
- Dữ liệu gốc không bị mutate sau khi code sửa DataFrame trong sandbox.
- Nếu có timeout: code vòng lặp vô hạn trả timeout.

DoD:
- Test chạy offline.
- Ít nhất các guard tối thiểu xanh trước demo.

### Task 3.3: AppTest cho AI Assistant

File chính:
- `tests/test_ai_assistant.py`

Cách làm:
- Dùng `streamlit.testing.v1.AppTest`.
- Monkeypatch `ai.api_ai.generate` để không gọi mạng, trả code mẫu:
  - `result = prov_year.head()`
  - hoặc `fig = px.line(...)` nếu dữ liệu test đủ.
- Kiểm tra:
  - app boot không exception.
  - bấm "Sinh code" hiển thị code.
  - bấm "Phê duyệt và thực thi" hiển thị kết quả/log.

DoD:
- Test không cần `GROQ_API_KEY`.
- Test không phụ thuộc mạng.
- Nếu dữ liệu thật nặng/không có trong CI, dùng fixture nhỏ hoặc monkeypatch `data.load_data`.

### Task 3.4: Stress-test thủ công cho 4 plugin

Mục tiêu: có bằng chứng nghiệm thu thực tế để đưa vào vấn đáp/báo cáo.

Checklist:
- Trend classification:
  - khoảng năm 1 năm.
  - khoảng năm đủ 2011-2024.
  - thiếu một lĩnh vực hoặc dữ liệu NaN.
- Anomaly:
  - năm mới nhất.
  - cột điểm có NaN.
  - không có tỉnh vượt ngưỡng `|z| > 2`.
- Insight:
  - D4 mặc định.
  - đổi sang một lĩnh vực khác, ví dụ D8.
  - trường hợp lĩnh vực thiếu dữ liệu một số năm.
- Clustering:
  - `n_clusters=4` mặc định.
  - thử `k=1` và `k=10`; AI/code phải xử lý hoặc báo lỗi rõ nếu không phù hợp.
  - dữ liệu có NaN ở D1-D8.

Biên bản cần ghi:
- Request đã dùng.
- Code AI sinh ra.
- Người dùng sửa gì.
- Kết quả/lỗi.
- Ảnh chụp hoặc trích log.

DoD:
- Có ít nhất 1 lần chạy thành công cho mỗi plugin.
- Có ít nhất 1 tình huống lỗi được xử lý rõ ràng và log lại.

## 6. WP-Logs & báo cáo

### Task 4.1: Log đủ dữ liệu phục vụ báo cáo

File chính:
- `app/ai/api_logs.py`
- `app/pages/ai_assistant.py`

Field tối thiểu trong mỗi record:
- `time`
- `request`
- `context`
- `code_ai`
- `code_run`
- `explanation`
- `stdout_preview`
- `error`
- `has_result`
- `has_fig`
- `result_shape` nếu `result` là DataFrame/Series
- `fig_type` nếu có `fig`

DoD:
- Log mới đủ field tối thiểu.
- Log cũ vẫn đọc được.
- Không ghi API key hoặc secret vào log.

### Task 4.2: Chuẩn bị bằng chứng vấn đáp

Deliverables:
- 4 câu hỏi demo tương ứng 4 plugin.
- 1 câu hỏi context-aware từ dashboard qua nút "Giải thích biểu đồ này".
- 1 ví dụ người dùng sửa code trước khi chạy, có diff log.
- 1 ví dụ code lỗi được hệ thống bắt và log.

DoD:
- Có thể trình bày rõ vai trò AI và con người trong từng ví dụ.
- Có thể chỉ vào log để chứng minh không thực thi ngầm.

## 7. Lộ trình ưu tiên

| Phase | Mục tiêu | Task | Lý do ưu tiên |
|---|---|---|---|
| P0 | Làm demo không bị vỡ | 2.2 stdout limit, 2.3 prompt safety | Giảm rủi ro treo UI/lỗi khó giải thích |
| P1 | Chứng minh human-in-the-loop | 1.1 diff log, 1.2 badge, 4.1 log fields | Đây là phần dễ bị hỏi trong vấn đáp |
| P2 | Tích hợp dashboard-AI | 1.3 smart link, 2.1 context đa trang | Tạo điểm cộng và trải nghiệm liền mạch |
| P3 | Kiểm thử | 3.1, 3.2, 3.3 | Chốt độ tin cậy trước demo |
| P4 | Nghiệm thu/báo cáo | 3.4, 4.2 | Chuẩn bị bằng chứng cuối kỳ |

Nếu thiếu thời gian:
- Không cắt: P0, P1, ít nhất 4 câu hỏi demo.
- Có thể giảm scope: context chỉ phủ `overview.py` và `time_trend.py` nếu các page khác còn stub.
- Có thể làm timeout là "nêu giới hạn" nếu chưa kịp process isolation, nhưng phải nói trung thực khi vấn đáp.

## 8. Thứ tự thực thi đề xuất

1. Cập nhật `api_exec.py` để cắt `stdout`; thêm test guard cơ bản.
2. Cập nhật `ai_assistant.py` để có badge, diff log, log field bổ sung.
3. Thêm `ai_explain_button` và nối từ ít nhất một chart trong `time_trend.py`.
4. Refactor `_format_context` và publish context cho `overview.py`.
5. Viết AppTest mock `api_ai.generate`.
6. Chạy stress-test 4 plugin, lưu bằng chứng vào log và ghi tóm tắt cho báo cáo.

## 9. Checklist trước vấn đáp

- [ ] `python -m pytest tests/test_api_ai.py tests/test_api_exec.py -q` xanh.
- [ ] AppTest AI Assistant xanh hoặc đã ghi rõ lý do không chạy được.
- [ ] Chạy thành công 4 plugin qua UI thật.
- [ ] Có log cho ít nhất 4 request demo.
- [ ] Có một log thể hiện người dùng sửa code trước khi chạy.
- [ ] Có một ví dụ lỗi runtime được hiển thị và log.
- [ ] Có nút "Giải thích biểu đồ này" hoạt động từ dashboard sang AI Assistant.
- [ ] Không có secret/API key trong log hoặc repo.
