# Trạng thái dự án

- Rà soát gần nhất: **22/07/2026**
- Bề mặt chính: **React + FastAPI local**

## Dashboard

| Khối | Trạng thái | Bằng chứng |
|---|---|---|
| Năm route phân tích | Hoàn thiện | `frontend/src/pages/`, `frontend/src/router.tsx` |
| 20 biểu đồ + 20 insight | Hoàn thiện | page components và `frontend/e2e/chart-label-layout.spec.ts` |
| Focus dialog | Hoàn thiện | `ChartFocusDialog.tsx`, query `focus=` và browser tests |
| Responsive/accessibility | Hoàn thiện trong phạm vi đồ án | desktop/tablet/mobile, keyboard, reduced motion và overflow tests |
| FastAPI dashboard | Hoàn thiện | 7 endpoint dữ liệu, typed OpenAPI, null/error contract |
| Floating AI Assistant | Hoàn thiện luồng cơ bản | answer/clarification/proposal/revision/approval/result/log |
| Legacy deep-link | Hoàn thiện | `/ai-assistant` redirect; `/dimensions` alias |
| Streamlit fallback | Đóng băng, vẫn chạy độc lập | `app/` |

## Dữ liệu

- 14 file Excel nguồn PAPI trong `data/raw/`.
- Phạm vi 63 tỉnh/thành, 2011–2024; D7–D8 từ 2018.
- Bảng long đã xử lý có 6.094 dòng; panel tỉnh–năm có 882 dòng.
- Pipeline và toàn bộ quy tắc xử lý nằm trong `src/` và `docs/data/README.md`.
- Không nội suy dữ liệu thiếu và không so trực tiếp tổng 6 với tổng 8 lĩnh vực qua mốc 2018.

## Kiểm thử gần nhất

| Suite | Kết quả |
|---|---|
| Python | 112 passed |
| Frontend unit | 39 passed |
| Browser E2E | 43 passed |
| ESLint | đạt |
| TypeScript/Vite build | đạt |

Browser tests bao phủ năm route, 20 card tại 1440×900, 1024×768 và 390×844, 20 dialog phóng to,
sidebar, URL state và luồng Floating AI Assistant. Live Groq không nằm trong suite mặc định.

## Giới hạn công bố rõ

- Executor chỉ dùng cho demo local; timeout/AST guard không biến nó thành sandbox công khai.
- AI live cần `GROQ_API_KEY` local và phụ thuộc availability/quota của Groq.
- Table/result log bị giới hạn 500 hàng để bảo vệ UI và JSONL; response vẫn ghi tổng số hàng và trạng thái cắt.
- Streamlit là fallback bảo toàn, không phải bề mặt UX cần phát triển tiếp.

## Tài liệu hiện hành

- Kiến trúc: `docs/architecture.md`
- Dữ liệu: `docs/data/README.md`
- Thiết kế: `docs/design/README.md`
- AI: `docs/ai/README.md`
- Cài đặt: `docs/guides/getting-started.md`
- Demo/vấn đáp: `docs/dashboard-handoff.md`

Roadmap, parity matrix và execution checklist đã hoàn tất được hợp nhất thành bản tóm tắt lịch sử tại
`docs/archive/2026-07-react-fastapi-migration.md`.
