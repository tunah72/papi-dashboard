# CLAUDE.md — Đồ án cuối kỳ Trực quan hóa Dữ liệu (CSC10108)

Ngôn ngữ làm việc: **Tiếng Việt** (code/comment có thể tiếng Anh, nhưng giải thích cho người dùng bằng tiếng Việt).

## 1. Mục tiêu sản phẩm
Một **dashboard trực quan hóa + phân tích dữ liệu Việt Nam**, có **module AI human-in-the-loop**, trình bày trong buổi vấn đáp. Hai khối chính:
1. **Dashboard trực quan** — kể một câu chuyện từ dữ liệu (xu hướng theo thời gian, mối quan hệ giữa biến, kết luận).
2. **Module AI** — người dùng chat yêu cầu phân tích → AI sinh code + giải thích → người duyệt → thực thi local → hiển thị kết quả → ghi log.

## 2. Ràng buộc cứng về dữ liệu (KHÔNG được vi phạm)
- Dữ liệu **thật**, về **Việt Nam**, nguồn **đáng tin cậy & minh bạch** (luôn ghi nguồn).
- **≥ 7 biến độc lập**, **≥ 2000 dòng**, **> 50%** dữ liệu liên quan Việt Nam.
- Ghi rõ mọi bước xử lý dữ liệu (không bỏ sót / không xử lý ngầm).

## 3. Tech stack đã chốt
- **Streamlit** (Python, all-in-one): dashboard + chat AI + xem/sửa/duyệt code + hiển thị kết quả trong một app.
- Phân tích/visualize: pandas, matplotlib/plotly, seaborn.
- LLM: gọi qua API (Gemini/OpenAI) — **code thực thi luôn chạy LOCAL**, không thực thi online.
- 3 API logic (bắt buộc, có thể là module nội bộ trong Streamlit): **API AI**, **API Thực thi**, **API Logs**.

## 4. Quy tắc tích hợp AI (BẮT BUỘC theo đề bài)
Đây là phần bị chấm và bị hỏi trong vấn đáp — tuân thủ tuyệt đối:
- **Vai trò:** AI đề xuất ý tưởng + viết code + giải thích. **Con người định hướng, sửa, phê duyệt, ra quyết định.**
- **Không thực thi ngầm:** AI KHÔNG tự đổi dữ liệu gốc, KHÔNG tự chạy thuật toán.
- **Hiển thị code bắt buộc:** mọi code AI sinh ra phải hiện rõ cho người dùng.
- **Giải thích bằng ngôn ngữ tự nhiên:** ngay trên code, comment giải thích việc code làm (vd: "Đoạn này xóa 15 dòng NULL ở cột Doanh Thu bằng dropna()").
- **Luồng phê duyệt:** code AI sinh ra ở trạng thái **"Chờ duyệt"** → người dùng sửa tham số → **chấp nhận** → MỚI thực thi và trả kết quả.
- **Không tự thêm số liệu/hình ảnh:** AI chỉ trình bày số liệu/biểu đồ do con người/dữ liệu cung cấp.
- **Lưu trữ:** mọi yêu cầu, code, kết quả, giải thích phải được log lại để truy xuất.

## 5. Ba API bắt buộc
- **API AI:** nhận yêu cầu từ frontend + ngữ cảnh (cấu trúc dữ liệu) → trả về code + giải thích.
- **API Thực thi:** nhận code đã được người sửa & duyệt → chạy trên dữ liệu tại máy → thu biểu đồ/bảng/logs trả về.
- **API Logs:** lưu toàn bộ yêu cầu, mã nguồn, kết quả, giải thích.

## 6. Vấn đáp
- Chuẩn bị sẵn **≥ 4 câu hỏi phân tích** (= số thành viên), dùng module AI để trả lời.
- Có thể bị hỏi câu ngoài lề → AI cần đủ linh hoạt.

## 7. Báo cáo
- Template LaTeX HCMUS trong `report/` (`main.tex`, `content/`, `ref/`, `appendix/`).
- Phải có phần **tóm tắt quá trình dùng AI**: yêu cầu đã đặt, kết quả nhận, thay đổi đã làm, nhận xét về AI.

## 8. Nhóm 4 người
- 23120199 — Lê Xuân Trí
- 23120208 — Dương Tuấn Anh (người đang làm việc với Claude)
- 23122038 — Nguyễn Trần Trung Kiên
- 23122045 — Lê Đức Phúc
- GV: Thầy Bùi Tiến Lên, Thầy Trần Huy Bân, Thầy Võ Nhật Tân

## 9. Cách làm việc với Claude
- Tuân thủ tinh thần đề bài: **con người là người quyết định.** Khi sinh code phân tích, trình bày kèm giải thích, không tự ý chạy/đổi dữ liệu nếu chưa được duyệt.
- Luôn ghi nguồn dữ liệu khi dùng.
- Ưu tiên giải pháp đơn giản, kịp deadline; đẹp & tương tác là điểm cộng.
