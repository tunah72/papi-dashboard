# Roadmap migration React + FastAPI

Roadmap này điều phối migration theo ADR và parity matrix. Khi có mâu thuẫn, ưu tiên
**code/runtime/test** → ADR/parity → status docs → archive. Không dùng roadmap để hạ cấp capability
legacy đã có code thành backlog chưa làm.

## Baseline legacy đã triển khai

Streamlit có sáu route: Tổng quan, H1 diễn biến, H2 vùng/tỉnh, H3 mối quan hệ lĩnh vực, H4 thay đổi/
phân nhóm và AI Assistant. H2–H4 đã có page + analysis; storytelling route/context AI, event pending
log và execution/reset log cũng đã có. Đây là baseline để đối chiếu content, không phải hạng mục lặp lại
trong các phase bên dưới.

## Phase 0 — Docs baseline và gate

**Trạng thái:** implementation hoàn tất; chỉ được gọi hoàn tất chính thức sau review gate.

- Chốt ADR React TypeScript strict + FastAPI local, sidebar trái và fallback Streamlit frozen.
- Chốt matrix năm trang phân tích và capability AI, numeric/content parity tách với UX improvements, semantic view-model và cutover/rollback.
- Đồng bộ current docs theo code/test baseline, xóa bốn artifact untracked bị bác bỏ.
- Gate: python3 -m pytest -q, git diff --check, audit vùng cấm và review độc lập.

## Phase 1 — FastAPI local

**Trạng thái:** implementation hoàn tất, chờ review gate cùng bằng chứng runtime.

- Tạo API local bind 127.0.0.1 cho metadata, dashboard data/view-model và lỗi chuẩn hoá.
- Tái sử dụng/đối chiếu analysis Python; không cho API/UI đọc raw data hoặc secrets.
- Chốt OpenAPI semantic view-model: source, unit, n, caveats; chuẩn hoá NaN/Infinity thành null.
- Thêm contract/unit test cho response, numeric parity, lỗi filter, null/GeoJSON và KMeans deterministic.
- Giữ scope data/dashboard: API AI, API thực thi và API logs qua HTTP là Phase 5; không có React scaffold
  trong phase này. Contract OpenAPI có tại `/openapi.json`; Phase 2 sẽ sinh TypeScript types từ đó.

## Phase 2 — React shell và Tổng quan

**Trạng thái:** implementation hoàn tất, chờ review gate.

- Tạo React TypeScript strict shell; sidebar ban đầu có sáu mục, đến Phase 5 được chuẩn hóa còn năm route và floating assistant.
- Implement /overview với content/numeric parity và map-linked ranking.
- Bổ sung loading/empty/error/retry, metadata semantic, keyboard/focus và responsive theo matrix.
- Giữ Streamlit Overview làm fallback độc lập.

## Phase 3 — H1 và H2

**Trạng thái:** implementation và local gate hoàn tất; chưa cutover.

- Implement /time-trend: trend/COVID/heatmap parity, dumbbell và linked selection.
- Implement /provincial: distribution/ranking/benchmark parity, dot plot thay radar.
- Kiểm fixture numeric, source/unit/n/caveats, viewport và interaction cho hai route.

## Phase 4 — H3 và H4

**Trạng thái:** implementation và local gate hoàn tất; chưa cutover.

- Implement /dimension: lower-triangle correlation heatmap click sang scatter, cặp X/Y hợp lệ.
- Implement /dynamics: delta/KMeans parity, top/bottom 8, full table và hồ sơ A–D/profile view.
- Kiểm deterministic clustering (random_state=42), missing endpoint và full responsive/accessibility cases.

## Phase 5 — AI qua HTTP

**Trạng thái:** đã triển khai floating assistant cơ bản trên năm trang React; chờ review/runtime gate trước cutover.

- API AI, API Thực thi và API Logs đã có contract FastAPI local, giữ human approval bằng proposal ID/checksum.
- Câu hỏi kiến thức trả answer; tính mới trả code read-only; revision bằng ngôn ngữ tự nhiên sinh toàn bộ code mới.
- Executor vẫn là process con timeout/stdout guard local, không được mô tả là sandbox public.
- Log pending có request/code/explanation/context; execution có bounded result (500 hàng), Plotly JSON,
  stdout/error/shape; không hiển thị internal reasoning.

## Phase 6 — QA, one-command demo và cutover

- Tạo script/lệnh local production-like: FastAPI phục vụ React dist; development dùng Vite + Uvicorn.
- Chạy browser QA ở 1440/1280/1024/900/768/390, sidebar/keyboard/focus/no-horizontal-scroll và state lỗi.
- Đính kèm evidence numeric/content parity, semantic response, UX improvements và AI pending/approved log.
- Cutover chỉ sau toàn bộ matrix pass; rollback quay về Streamlit fallback, không migration data hoặc xóa log.

## Ngoài scope migration nhưng chưa hoàn tất

- Full result artifact không giới hạn và hardening executor ở cấp OS vẫn là việc thật sự còn lại.
- Browser QA/cutover evidence chỉ được tạo ở Phase 6.
- Notebook cross-check, rehearsal vấn đáp và báo cáo thuộc công việc dự án rộng hơn;
  không được sửa report/ trong migration này.
