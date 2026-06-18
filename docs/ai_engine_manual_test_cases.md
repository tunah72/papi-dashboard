# Manual test cases cho AI Engine

Ngày cập nhật: 2026-06-19

Mục tiêu: kiểm tra luồng AI human-in-the-loop trong trang `AI Assistant`, đặc biệt các thay đổi mới:

- Chọn kỹ thuật phân tích sẽ tự reset code/kết quả cũ.
- Câu hỏi gợi ý có thể chỉnh sửa và được gửi làm yêu cầu chính.
- Yêu cầu phân tích bổ sung được ghép vào prompt AI, không thay thế câu hỏi chính.
- AI phải ưu tiên câu hỏi người dùng đã chỉnh, không quay về default của plugin.

## Test case 1: Đổi chủ đề trong cùng kỹ thuật và thêm góp ý

**Mục tiêu:** xác nhận AI dùng câu hỏi gợi ý đã chỉnh sửa, không dùng default của kỹ thuật.

**Bước thực hiện:**

1. Mở `http://localhost:8501/ai_assistant`.
2. Ở `Chọn kỹ thuật phân tích`, chọn `Gom nhóm tỉnh theo hồ sơ lĩnh vực`.
3. Trong ô `Câu hỏi gợi ý (có thể chỉnh sửa)`, thay toàn bộ nội dung bằng:

   ```text
   Hãy gom nhóm các tỉnh miền Nam thành 3 cụm dựa trên điểm của 8 lĩnh vực PAPI trong năm mới nhất, sau đó vẽ scatter plot so sánh giữa D1 và D8.
   ```

4. Trong ô `Yêu cầu phân tích bổ sung (tuỳ chọn)`, nhập:

   ```text
   Chỉ dùng region thật trong dữ liệu. Nếu sau khi lọc không đủ tỉnh để gom nhóm thì trả về bảng giải thích thay vì báo lỗi.
   ```

5. Bấm `Sinh code (AI đề xuất)`.
6. Đọc phần `Code phân tích — Chờ duyệt`.
7. Nếu code hợp lý, bấm `Phê duyệt và thực thi`.

**Kỳ vọng đạt:**

- Code dùng `n_clusters=3`, không phải `4`.
- Code vẽ trục `D1` và `D8`, không quay về default `D4` và `D8`.
- Code lọc miền Nam bằng region thật, ưu tiên `Đông Nam Bộ` và `Đồng bằng sông Cửu Long`.
- Code có guard khi dữ liệu rỗng hoặc không đủ dòng trước `StandardScaler`/`KMeans`.
- Khi chạy, không xuất hiện lỗi `Found array with 0 sample(s)`.
- Nhật ký phiên AI ghi đúng request đã chỉnh và phần yêu cầu bổ sung.

**Dấu hiệu lỗi:**

- Code vẫn dùng `n_clusters=4`.
- Code vẫn dùng `D4` dù câu hỏi đã đổi sang `D1`.
- Code lọc bằng nhãn không có thật như `Miền Đông Nam Bộ`, `Miền Tây Nam Bộ`.
- Kết quả thực thi báo lỗi từ `StandardScaler` hoặc `KMeans` do DataFrame rỗng.

## Test case 2: Đổi kỹ thuật phải reset trạng thái cũ

**Mục tiêu:** xác nhận khi đổi kỹ thuật, app không giữ code/kết quả của kỹ thuật trước.

**Bước thực hiện:**

1. Mở `AI Assistant`.
2. Chọn `Phát hiện tỉnh bất thường`.
3. Giữ câu hỏi gợi ý mặc định hoặc chỉnh nhẹ, bấm `Sinh code (AI đề xuất)`.
4. Bấm `Phê duyệt và thực thi` để tạo kết quả.
5. Đổi `Chọn kỹ thuật phân tích` sang `Gom nhóm tỉnh theo hồ sơ lĩnh vực`.

**Kỳ vọng đạt:**

- Vùng `Code phân tích` và `Kết quả thực thi` của kỹ thuật cũ biến mất.
- Ô `Câu hỏi gợi ý` được nạp prompt mặc định của kỹ thuật gom nhóm.
- Ô `Yêu cầu phân tích bổ sung` trở về rỗng.
- Bấm `Sinh code` sau đó sẽ sinh code cho kỹ thuật gom nhóm, không còn code phát hiện bất thường.

**Dấu hiệu lỗi:**

- Code hoặc kết quả cũ vẫn còn hiển thị sau khi đổi kỹ thuật.
- Ô câu hỏi vẫn giữ prompt của kỹ thuật trước.
- AI sinh code theo kỹ thuật cũ dù dropdown đã đổi.

## Test case 3: Câu hỏi ngoài default của plugin insight

**Mục tiêu:** xác nhận AI suy luận theo câu hỏi đã chỉnh, không bị khóa vào lĩnh vực default của plugin.

**Bước thực hiện:**

1. Mở `AI Assistant`.
2. Chọn `Phân tích insight theo lĩnh vực`.
3. Trong ô `Câu hỏi gợi ý`, đổi nội dung thành:

   ```text
   Hãy phân tích và nhận xét các điểm nổi bật của lĩnh vực D8 (Quản trị điện tử) trong năm mới nhất, so sánh các tỉnh có điểm cao nhất và thấp nhất.
   ```

4. Trong ô `Yêu cầu phân tích bổ sung`, nhập:

   ```text
   Trả về bảng top 10 tỉnh cao nhất và top 10 tỉnh thấp nhất, kèm biểu đồ cột nếu phù hợp.
   ```

5. Bấm `Sinh code (AI đề xuất)`.
6. Kiểm tra code trước khi duyệt, sau đó bấm `Phê duyệt và thực thi`.

**Kỳ vọng đạt:**

- Code phân tích cột `D8`, không dùng default `D4`.
- `result` có nhóm tỉnh điểm cao và thấp theo D8.
- Nếu có biểu đồ, trục/nhãn thể hiện D8 hoặc Quản trị điện tử.
- Nhật ký phiên AI ghi cả câu hỏi chính về D8 và yêu cầu bổ sung top 10.

**Dấu hiệu lỗi:**

- Code vẫn dùng `D4` hoặc “Kiểm soát tham nhũng”.
- Kết quả không có top cao/thấp như yêu cầu bổ sung.
- AI trả code thiếu `result` hoặc thiếu `fig` trong khi có yêu cầu biểu đồ.
