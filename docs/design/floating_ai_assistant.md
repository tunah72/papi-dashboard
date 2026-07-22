# Floating AI Assistant

## 1. Vai trò và vị trí

React có năm trang phân tích và một Trợ lý AI nổi dùng chung. Sidebar chỉ điều hướng năm trang; route
cũ `/ai-assistant` redirect đến `/overview?assistant=open`. Mở assistant không đổi trang, không gọi AI,
không chạy code và không thay đổi kích thước chart grid.

Launcher xuất hiện ở góc dưới bên phải trên `/overview`, `/time-trend`, `/provincial`, `/dimension` và
`/dynamics`. Accessible name là `Mở Trợ lý AI`, tooltip là `Hỏi Trợ lý AI`.

## 2. Desktop và mobile

- Desktop: launcher tròn 56×56 px, `right/bottom: 24px`; panel rộng 420–460 px, cao tối đa 680 px hoặc
  `calc(100dvh - 112px)`, nằm trên launcher và không có backdrop.
- Mobile: launcher cách mép 16 px cộng `env(safe-area-inset-bottom)`; panel rộng gần toàn màn hình,
  cao 80–88dvh; header và composer cố định trong panel, hội thoại cuộn độc lập.
- Màu dùng teal/navy và token civic editorial hiện hành; không gradient tím/xanh, glow hoặc animation
  liên tục. `prefers-reduced-motion` tắt chuyển động không cần thiết.

## 3. State và nội dung

Hai trạng thái hiển thị là `open` và `hidden`; launcher là điểm mở lại duy nhất nên không có thêm nút
Thu nhỏ hoặc pill trùng chức năng. Trong trạng thái `open`, kích thước là `default` hoặc `maximized`.
Đóng chỉ ẩn panel và giữ phiên trong `sessionStorage`; action “Cuộc trò chuyện mới” mới xóa state UI.

Dialog gồm header, context trang, nút `+` (accessible name “Bắt đầu cuộc trò chuyện mới”)/Phóng to
hoặc Khôi phục/Đóng, conversation, proposal code read-only, result và composer. Câu hỏi kiến thức có
nguồn. Proposal có nhãn `CHỜ DUYỆT`, giải thích, toàn bộ code, action
`Yêu cầu chỉnh lại` và `Đồng ý và chạy local`. Proposal cũ hiện lịch sử nhưng bị đánh dấu đã thay thế.

Phóng to mở rộng panel trong vùng viewport còn lại trên desktop và gần toàn màn hình trên mobile,
không thay đổi kích thước chart grid. `Esc` ở trạng thái phóng to chỉ khôi phục kích thước; `Esc` tiếp
theo mới đóng panel và trả focus về launcher.

## 4. Human-in-the-loop

```text
idle → sending → answer | clarification | pending_approval
pending_approval → revising → pending_approval
pending_approval → approving → succeeded | failed
```

Frontend không gửi code đến API execution. FastAPI đối chiếu `sessionId`, `proposalId` và checksum,
chỉ chạy proposal mới nhất đang chờ duyệt. Revision chỉ nhận mô tả tự nhiên và phải trả toàn bộ code mới.

## 5. Accessibility và acceptance

- Launcher và header action có vùng bấm ít nhất 44×44 px, focus ring rõ và tên truy cập được.
- Đóng và `Esc` ở kích thước mặc định trả focus về launcher; click ngoài không đóng hoặc làm mất state.
- Dialog non-modal trên desktop nên không inert dashboard; chart focus dialog native luôn nằm lớp trên.
- Code và bảng có vùng cuộn riêng; bảng có caption, header và trạng thái truncation.
- Kiểm ở 1440×900, 1024×768, 390×844, keyboard-only, zoom 200%, reduced motion và không horizontal overflow.
