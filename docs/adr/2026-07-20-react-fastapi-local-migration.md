# ADR: Migration React TypeScript strict + FastAPI local

- **Trạng thái:** Accepted
- **Ngày:** 20/07/2026
- **Phạm vi:** quyết định kiến trúc và acceptance Phase 0; chưa khởi tạo FastAPI hoặc React.

## Thứ bậc authority

Khi có mâu thuẫn, ưu tiên theo thứ tự: **code/runtime/test hiện tại** → ADR và parity matrix
cho migration → status docs hiện hành → `docs/archive/`. Tài liệu archive không dùng để kết luận
tính năng đã triển khai; status docs là snapshot, không thay thế bằng chứng runtime/test.

## Bối cảnh

`app/main.py` hiện khai báo sáu trang Streamlit và sidebar trái. Dashboard chỉ dùng dữ liệu đã xử lý;
AI Assistant là human-in-the-loop. Migration cần tách UI/backend nhưng không được đổi số liệu, nguồn
dữ liệu hoặc quyền quyết định của người dùng.

## Quyết định

1. **UI đích:** React + TypeScript `strict`, tiếng Việt nhất quán. Sáu nhãn sidebar target, theo đúng
   thứ tự, là: **Tổng quan; Diễn biến theo thời gian; Vùng & tỉnh; Mối quan hệ lĩnh vực; Thay đổi &
   phân nhóm; Trợ lý AI**. Tên legacy Streamlit chỉ là baseline đối chiếu, không phải nhãn target.
2. **Backend đích:** FastAPI chạy local và bind `127.0.0.1`, là ranh giới HTTP cho dữ liệu đã xử lý và
   API AI, API Thực thi, API Logs. React không đọc `data/raw/`, secrets, hoặc tự tính/sửa dữ liệu nguồn.
   Logic trong `src/analysis/` phải được tái sử dụng/đối chiếu ở Python, không sao chép công thức sang UI.
3. **Vận hành:** development dùng Vite + Uvicorn. Bản demo production-like là một lệnh local, trong đó
   FastAPI phục vụ React `dist`; script/lệnh cụ thể được tạo ở **Phase 6**, không tạo trong Phase 0.
4. **OpenAPI semantic view-model:** response dành cho UI phải có, khi áp dụng, `source`, `unit`, số quan
   sát `n`, và `caveats`, cạnh dữ liệu/series/chart spec. Giá trị số không biểu diễn được
   (`NaN`, `Infinity`) phải được chuẩn hoá thành JSON `null`; UI không tự suy diễn giá trị thiếu.
5. **AI:** code và giải thích luôn hiển thị, ở trạng thái chờ duyệt trước khi chạy; chỉ thực thi local
   sau hành động phê duyệt rõ ràng. Executor vẫn chạy process con có timeout và giới hạn stdout; đây chỉ
   là guard demo local, **không phải public security sandbox**. API Logs lưu request, code, explanation,
   context, approval, kết quả hoặc lỗi; không lưu/hiển thị internal reasoning của model.
6. **Sidebar trái là invariant:** sáu route dùng cùng sidebar trái, có active state, không bị thay bằng
   top navigation. Ở màn hình hẹp sidebar có thể thu gọn, nhưng phải có nút mở lại có nhãn truy cập được
   và không làm mất route.
7. Streamlit ở `app/` là **legacy fallback frozen** đến cutover. Chỉ sửa lỗi tối thiểu để fallback chạy
   được; capability mới thuộc React/FastAPI sau phase được phê duyệt.

## Cutover và rollback

Cutover chỉ được phép khi toàn bộ acceptance trong `docs/react-fastapi-parity-matrix.md` đạt: content/
numeric parity trên cùng snapshot `data/processed/`, semantic view-model, responsive/sidebar/accessibility,
và AI không thực thi trước duyệt. Bản phát hành phải giữ Streamlit chạy độc lập và không đổi schema dữ
liệu/logs.

Nếu có sai khác số vượt tolerance, thiếu metadata/error-retry, mất AI context, vi phạm sidebar/approval,
hay lỗi ở viewport bắt buộc, dừng cutover và quay demo về Streamlit fallback. Rollback không migration
dữ liệu, không xóa log, không sửa dữ liệu đã xử lý; sửa UI/API mới rồi chạy lại ma trận trước cutover kế tiếp.

## Hệ quả

Hai bề mặt UI làm tăng chi phí đối chiếu, nhưng cho phép nâng UX có chủ đích mà vẫn bảo toàn nội dung,
nguồn và human-in-the-loop qua acceptance source cụ thể.
