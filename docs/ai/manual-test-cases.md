# Manual test cases — Floating AI Assistant

## 1. Mở panel không gọi AI

1. Mở từng route phân tích và click launcher `Mở Trợ lý AI`.
2. Kiểm tra panel mở tại chỗ, chart grid không đổi kích thước và Network không có POST assistant.
3. Thu nhỏ thành pill, mở lại, Đóng rồi mở lại; câu hỏi/kết quả cũ phải còn.
4. Mở `/ai-assistant`; URL phải thành `/overview?assistant=open` và panel mở.

## 2. Câu hỏi kiến thức

Gửi `Chỉ số PAPI là gì?`. Kỳ vọng response là answer, không có code/action thực thi, có dòng
`Nguồn: UNDP Việt Nam · CECODES · RTA` và log có request + answer.

## 3. Proposal, revision và approval

1. Gửi `Lĩnh vực nào có điểm trung bình cao nhất trong năm 2024?`.
2. Xác nhận explanation và toàn bộ code ở trạng thái `CHỜ DUYỆT`; chưa có execution log/result.
3. Chọn `Yêu cầu chỉnh lại`, nhập `Chỉ tính cho các tỉnh thuộc Tây Nguyên và trả thêm biểu đồ cột`.
4. Xác nhận code mới hiển thị đầy đủ, code cũ mang nhãn đã thay thế và không còn nút chạy.
5. Duyệt code mới; chỉ lúc này mới có approval, execution và result/figure hoặc lỗi rõ ràng.

## 4. Context và câu hỏi mơ hồ

Mở `/time-trend?scale=six&from=2015&to=2024`, hỏi `Yếu tố nào cao nhất?`. Context header và request log
phải giữ đúng trang/range. Nếu chưa rõ phạm vi, AI chỉ hỏi tối đa một câu làm rõ; lượt sau phải trả answer
hoặc proposal.

## 5. Responsive và accessibility

Kiểm ở 1440×900, 1024×768, 390×844, keyboard-only, zoom 200% và reduced motion. Launcher/panel không
gây horizontal overflow; mobile có safe area; header/composer còn nhìn thấy; conversation cuộn độc lập.
`Esc` đóng panel và trả focus về launcher. Click ngoài không làm mất hoặc đóng state.
