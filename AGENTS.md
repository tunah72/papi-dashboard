# AGENTS.md — Đồ án cuối kỳ Trực quan hóa Dữ liệu (CSC10108)

Ngôn ngữ làm việc: **Tiếng Việt** (code/comment có thể tiếng Anh, nhưng giải thích cho người dùng bằng tiếng Việt).

## 1. Mục tiêu sản phẩm

Một **dashboard trực quan hóa + phân tích dữ liệu Việt Nam**, có **module AI human-in-the-loop**, trình bày trong buổi vấn đáp. Hai khối chính:
1. **Dashboard trực quan** — kể một câu chuyện từ dữ liệu (xu hướng theo thời gian, mối quan hệ giữa biến, kết luận).
2. **Module AI** — người dùng chat yêu cầu phân tích → AI sinh code + giải thích → người duyệt → thực thi local → hiển thị kết quả → ghi log.

## 2. Ràng buộc cứng về dữ liệu (KHÔNG được vi phạm)

- Dữ liệu **thật**, về **Việt Nam**, nguồn **đáng tin cậy & minh bạch** (luôn ghi nguồn).
- **≥ 7 biến độc lập**, **≥ 2000 dòng**, **> 50%** dữ liệu liên quan Việt Nam.
- Ghi rõ mọi bước xử lý dữ liệu (không bỏ sót / không xử lý ngầm).

## 3. Tech stack hiện tại

- **UI chính:** React + TypeScript `strict`; dashboard có năm trang phân tích và một floating AI Assistant dùng chung để chat, xem code, yêu cầu sửa bằng ngôn ngữ tự nhiên, duyệt và xem kết quả.
- **Backend:** FastAPI chạy **local**, là ranh giới HTTP cho dữ liệu đã xử lý và ba API bắt buộc: **API AI**, **API Thực thi**, **API Logs**.
- Phân tích/visualize giữ Python: pandas, matplotlib/plotly, seaborn. React chỉ hiển thị dữ liệu/figure do backend local trả về, không được tự thay đổi dữ liệu gốc.
- LLM gọi Groq qua API — **code thực thi luôn chạy LOCAL**, không thực thi online.
- **Streamlit là legacy fallback bị đóng băng:** `app/` chỉ còn là bề mặt demo dự phòng. Không thêm tính năng hay thay đổi hành vi ngoài sửa lỗi cần thiết để giữ fallback hoạt động.
- Sidebar điều hướng bên trái là bất biến sản phẩm; UI React chỉ có năm route phân tích trong sidebar. Trợ lý AI mở bằng launcher cố định trên cả năm trang, không phải mục điều hướng hoặc trang riêng.

## 4. Nguồn sự thật và bất biến thiết kế Dashboard

- **Nguồn dữ liệu chuẩn:** `docs/data/README.md`. Khi giao diện hoặc đặc tả mâu thuẫn với dữ liệu,
  sửa giao diện/đặc tả theo dữ liệu; không tự tạo số liệu, biến hoặc định nghĩa phân tích ở frontend.
- **Nguồn thiết kế chuẩn:** `docs/design/README.md` và các file `docs/design/*.md`. Tài liệu trong
  `docs/guides/design-system.md` chỉ còn áp dụng cho Streamlit legacy khi có ghi rõ.
- Dashboard React có **năm trang phân tích**: Tổng quan, Diễn biến theo thời gian, Vùng và tỉnh, Mối
  quan hệ lĩnh vực, Thay đổi và phân nhóm. Mỗi trang phải có **đúng 4 biểu đồ chính và 4 insight động
  tương ứng**; không thêm biểu đồ thứ năm để lấp chỗ hoặc lặp lại nội dung của trang khác.
- Desktop dùng grid 2 × 2 cân bằng; tablet/mobile chuyển một cột khi cần để giữ khả năng đọc. Header,
  filter và KPI phải gọn để hàng biểu đồ đầu xuất hiện sớm; không đặt khối “Tín hiệu cần đọc” lớn
  trước grid. Insight ngắn nằm ngay dưới biểu đồ mà nó trả lời.
- Không đặt khối hoặc CTA “Bước đọc tiếp” ở cuối các trang phân tích. Điều hướng giữa năm trang dùng
  sidebar; Trợ lý AI dùng floating launcher; drill-through chỉ xuất hiện tại interaction có ngữ cảnh ngay trên biểu đồ.
- Dùng đa dạng hình thức trực quan theo ma trận trong `docs/design/README.md`; không thay biểu đồ đã
  duyệt bằng pie/donut, 3D, hai trục tung hoặc animation liên tục nếu chưa cập nhật đặc tả.
- Mọi biểu đồ phải có tooltip tiếng Việt, hover highlight/dim, legend hoặc control tương đương,
  selection nhìn được ngoài màu, và bảng/fallback truy cập được bằng bàn phím. Filter và selection đã
  cam kết phải giữ trong URL để refresh, deep-link và drill-through không mất ngữ cảnh; hover chỉ là
  trạng thái tạm thời, không ghi vào URL.
- Màu vùng/lĩnh vực phải nhất quán giữa các trang. Tăng/giảm không chỉ dựa vào màu; phải có dấu, hướng,
  ký hiệu hoặc nhãn. Luôn công bố nguồn, đơn vị, `n` thực tế và caveat dữ liệu thiếu.
- Không so sánh trực tiếp tổng 6 lĩnh vực với tổng 8 lĩnh vực qua mốc 2018. Không diễn giải tương quan,
  hồi quy hoặc phân cụm thành quan hệ nhân quả hay xếp hạng chính thức.
- Thống kê, insight động và định nghĩa nghiệp vụ phải được tính trong `src/analysis`/FastAPI hoặc từ
  cùng artifact bằng hàm đã test. React chỉ mã hóa view-model thành giao diện và quản lý interaction;
  không sao chép công thức nghiệp vụ vào page component.

### Chế độ phóng to biểu đồ

- Cả 20 chart card có button `Phóng to biểu đồ` ở góc trên bên phải, vùng bấm tối thiểu 44 × 44 px và
  accessible name chứa tên biểu đồ.
- Click button mở cùng biểu đồ trong semantic dialog gần toàn màn hình trên desktop và toàn màn hình
  trên mobile. Popup phải giữ nguyên filter, selection, legend, tooltip, insight, nguồn, đơn vị và `n`;
  không fetch lại hoặc tính ra một câu trả lời khác chỉ vì đổi kích thước.
- Popup đóng được bằng nút đóng, `Esc` và Back khi dùng query `focus={chart_id}`; khi đóng phải trả focus
  về button đã mở, giữ vị trí cuộn và mở khóa body. Nội dung nền phải `inert` khi dialog mở.
- Zoom/pan trục chỉ bật khi có ý nghĩa với dạng biểu đồ và không thay thế chế độ phóng to. Mở popup
  không chạy code AI, không chạy lại KMeans/PCA và không thay đổi dữ liệu.
- Contract, responsive states, accessibility và acceptance criteria chi tiết nằm tại
  `docs/design/chart_focus_mode.md`; không tạo implementation riêng lệch hành vi ở từng page.

## 5. Quy tắc tích hợp AI (BẮT BUỘC theo đề bài)

Đây là phần bị chấm và bị hỏi trong vấn đáp — tuân thủ tuyệt đối:
- **Vai trò:** AI đề xuất ý tưởng + viết code + giải thích. **Con người định hướng, sửa, phê duyệt, ra quyết định.**
- **Không thực thi ngầm:** AI KHÔNG tự đổi dữ liệu gốc, KHÔNG tự chạy thuật toán.
- **Hiển thị code bắt buộc:** mọi code AI sinh ra phải hiện rõ cho người dùng.
- **Giải thích bằng ngôn ngữ tự nhiên:** ngay trên code, comment giải thích việc code làm (vd: "Đoạn này xóa 15 dòng NULL ở cột Doanh Thu bằng dropna()").
- **Luồng phê duyệt:** code AI sinh ra ở trạng thái **"Chờ duyệt"** → người dùng mô tả yêu cầu sửa bằng ngôn ngữ tự nhiên → AI sinh toàn bộ code mới → **chấp nhận bản mới nhất** → MỚI thực thi và trả kết quả.
- **Không tự thêm số liệu/hình ảnh:** AI chỉ trình bày số liệu/biểu đồ do con người/dữ liệu cung cấp.
- **Lưu trữ:** mọi yêu cầu, code, kết quả, giải thích phải được log lại để truy xuất.

## 6. Ba API bắt buộc

- **API AI:** nhận yêu cầu từ frontend + ngữ cảnh (cấu trúc dữ liệu) → trả về code + giải thích.
- **API Thực thi:** chỉ nhận `sessionId`, `proposalId`, `approved: true`; server xác nhận proposal mới nhất đã duyệt rồi chạy code đã lưu trên dữ liệu tại máy → thu biểu đồ/bảng/logs trả về.
- **API Logs:** lưu toàn bộ yêu cầu, mã nguồn, kết quả, giải thích.

## 7. Vấn đáp

- Chuẩn bị sẵn **≥ 4 câu hỏi phân tích** (= số thành viên), dùng module AI để trả lời.
- Có thể bị hỏi câu ngoài lề → AI cần đủ linh hoạt.

## 8. Báo cáo

- Template LaTeX HCMUS trong `report/` (`main.tex`, `content/`, `ref/`, `appendix/`).
- Phải có phần **tóm tắt quá trình dùng AI**: yêu cầu đã đặt, kết quả nhận, thay đổi đã làm, nhận xét về AI.

## 9. Nhóm 4 người

- 23120199 — Lê Xuân Trí
- 23120208 — Dương Tuấn Anh (người đang làm việc với Codex)
- 23122038 — Nguyễn Trần Trung Kiên
- 23122045 — Lê Đức Phúc
- GV: Thầy Bùi Tiến Lên, Thầy Trần Huy Bân, Thầy Võ Nhật Tân

## 10. Cách làm việc với Codex

- Tuân thủ tinh thần đề bài: **con người là người quyết định.** Khi sinh code phân tích, trình bày kèm giải thích, không tự ý chạy/đổi dữ liệu nếu chưa được duyệt.
- Luôn ghi nguồn dữ liệu khi dùng.
- Ưu tiên giải pháp đơn giản, kịp deadline; đẹp & tương tác là điểm cộng.
- Khi triển khai hoặc review Dashboard, phải đối chiếu cả code và runtime hiện tại với
  `docs/design/*.md`; test pass không tự chứng minh giao diện đã đạt yêu cầu.
- Kiểm tra tối thiểu ở 1440 × 900, 1024 × 768, mobile, keyboard-only, zoom trình duyệt 200%,
  `prefers-reduced-motion`, loading, empty, error và partial-data states.
- Không sửa `data/` hoặc `report/` khi làm UI/UX nếu người dùng không mở rộng phạm vi rõ ràng.
