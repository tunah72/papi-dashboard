---
date: 2026-07-21
scope: Conflict baseline before planning a new H2 branch from main
old_branch: feature/task/Tri
target_branch: main
---

# Conflict: feature/task/Tri vs main

## Verdict

Không merge hoặc rebase nguyên nhánh cũ. Nhánh cũ tách từ `34b0bae` (21/06), trong khi `main` ở `697f5b2` (17/07). Có conflict ở `app/pages/provincial.py`; `app/pages/ai_assistant.py` thay đổi ở cả hai nhánh. `api_logs.py` cũng đã diverge mạnh.

## File overlap có rủi ro

| Nhóm | File | Quyết định cho nhánh mới |
|---|---|---|
| H2 | `app/pages/provincial.py` | Lấy `main` làm nền; port chọn lọc map/top-bottom/slope/outlier từ nhánh cũ. |
| H2 logic | `src/analysis/spatial.py` vs `src/analysis/provincial.py` | Không đưa cả hai vào production; chuyển các helper được chọn vào `provincial.py` và test cùng module. |
| AI/log | `app/pages/ai_assistant.py`, `app/ai/api_logs.py` | Ngoài phạm vi H2 mới; không port để tránh ghi đè fix 17/07. Chỉ mở task riêng nếu nhóm chốt. |
| Tests | `tests/test_spatial.py`, `tests/test_provincial.py` | Chuyển test theo behavior được port; không giữ hai bộ test cho hai implementation. |
| Báo cáo | `report/**` | Port riêng sau khi số liệu H2 được tái tạo và kiểm chứng. |
| Dependency | `requirements.txt` | Không thêm pytest runtime; `requirements-dev.txt` đã chứa pytest. |

## Tác động đến kế hoạch mới

- Nhánh mới phải tạo trực tiếp từ `main` hiện tại, tên đề xuất: `feat/h2-provincial-completion`.
- Mỗi commit chỉ có một scope: logic/test H2, page H2, report H2, hoặc docs trạng thái.
- Không cherry-pick commit `90da9f9`; dùng nó chỉ như tài liệu tham khảo code.
- Chỉ coi feature hoàn tất sau khi test runtime, AppTest/smoke test, review và merge.

## Câu hỏi mở

- H2 có bắt buộc click choropleth để drill-down không, hay selectbox được chấp nhận?
