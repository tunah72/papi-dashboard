# Tóm tắt migration React + FastAPI — 07/2026

Tài liệu lịch sử này hợp nhất roadmap Phase 0–6, parity matrix và execution checklist Floating AI
Assistant đã hoàn tất. Không dùng file này để suy ra trạng thái runtime hiện tại.

## Quyết định

- React + TypeScript strict là UI chính, gồm năm route phân tích và sidebar trái.
- FastAPI local cung cấp bảy endpoint dữ liệu và ba endpoint assistant.
- Trợ lý AI là floating panel dùng chung; `/ai-assistant` chỉ redirect để giữ deep-link cũ.
- Code AI luôn read-only ở trạng thái chờ duyệt; revision sinh proposal mới và chỉ proposal mới nhất
  được chạy local sau phê duyệt.
- Streamlit được giữ làm fallback đóng băng trong `app/`.
- Logic nghiệp vụ ở Python; React chỉ render view-model và quản lý interaction.

## Phạm vi đã chuyển

| Bề mặt | Kết quả |
|---|---|
| Tổng quan | KPI, bản đồ và ba story chart |
| Diễn biến | Line, heatmap năm-kề-năm, bump chart và slopegraph |
| Vùng & tỉnh | Phân phối, ranking, benchmark và profile |
| Quan hệ lĩnh vực | Correlation, scatter, residual và mean ± SD |
| Thay đổi & phân nhóm | Dumbbell, profile, PCA và Sankey |
| AI | Answer/clarification/proposal/revision/approval/execution/log |

## Acceptance đã dùng

- Numeric/content parity trên cùng snapshot `data/processed/`.
- View-model có source, unit, `n`, caveat và JSON null an toàn.
- Năm route dùng cùng sidebar, URL giữ filter/selection và không có overflow ở viewport bắt buộc.
- 20 chart có focus dialog, insight và bảng thay thế.
- Pending proposal không gọi executor; proposal superseded trả `409`.
- Executor có timeout/stdout cap/AST guard nhưng không được coi là sandbox công khai.

## Bằng chứng khi kết thúc

- 112 Python tests.
- 39 frontend unit tests.
- 43 Playwright tests trên desktop, tablet, mobile và 20 dialog phóng to.
- TypeScript/Vite build, ESLint và OpenAPI type check đạt.
- Một live Groq smoke câu hỏi kiến thức trả answer có nguồn, không sinh hoặc chạy code.

Các số kiểm thử trên là snapshot lịch sử. Kết quả hiện tại nằm trong `docs/project-status.md`.
