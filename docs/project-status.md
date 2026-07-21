# Trạng thái dự án

Ngày rà soát migration Phase 0–4: **20/07/2026**

Baseline code: `main` tại `697f5b2`

Baseline test tại commit trên: `python3 -m pytest -q` — **62 passed**

## Thứ bậc authority

Khi tài liệu mâu thuẫn, ưu tiên: **code/runtime/test hiện tại** → ADR và parity matrix migration →
trạng thái trong file này → `docs/archive/`. File này là snapshot để định hướng, không phải bằng chứng
thay thế cho runtime hoặc test. Archive chỉ để truy vết lịch sử.

## Tóm tắt

| Khối | Trạng thái tại baseline | Bằng chứng chính |
|---|---|---|
| Dữ liệu raw → processed | Có pipeline và dữ liệu đã xử lý | `src/build_dataset.py`, `src/papi_lib.py`, `data/processed/` |
| Dashboard năm route + floating AI | React có năm route phân tích; Streamlit sáu trang là legacy fallback | `frontend/`, `app/pages/` |
| Tổng quan | Có KPI, bản đồ, ranking và context AI | `app/pages/overview.py` |
| H1 — Diễn biến | Có trend, COVID, heatmap, drill-down | `app/pages/time_trend.py`, `src/analysis/trend.py` |
| H2 — Vùng & tỉnh | Có phân phối, ranking, benchmark, profile | `app/pages/provincial.py`, `src/analysis/provincial.py` |
| H3 — Mối quan hệ lĩnh vực | Có correlation, scatter và phân tán | `app/pages/dimension.py`, `src/analysis/dimensions.py` |
| H4 — Thay đổi & phân nhóm | Có delta và KMeans profile | `app/pages/dynamics.py`, `src/analysis/dynamics.py` |
| Floating AI Assistant | Có answer/proposal/revision → duyệt proposal mới nhất → thực thi local → lifecycle log | `frontend/src/components/FloatingAssistant.tsx`, `server/assistant.py` |
| Test offline | 112 Python, 39 frontend unit và 43 browser E2E pass; E2E bao phủ thêm lỗi nhãn/đường/clip của 20 biểu đồ ở card, tablet, mobile và chế độ xem riêng | `pytest`, Vitest, Playwright |
| FastAPI local API | Có health, 7 dashboard endpoint và 3 contract assistant messages/executions/logs | `server/`, `tests/test_assistant_http.py` |
| React target | Sidebar 5 route dữ liệu thật và floating assistant dùng chung; route AI cũ chỉ redirect | `frontend/` |
| Báo cáo LaTeX | Ngoài scope migration | `report/` |

## Ranh giới đang áp dụng

- Data gốc và processed là bất biến trong migration; app/target UI không đọc Excel raw trực tiếp.
- Code AI phải được hiện; người dùng yêu cầu sửa bằng ngôn ngữ tự nhiên và duyệt proposal mới nhất rồi mới chạy local; executor không phải sandbox public.
- Streamlit là fallback frozen đến khi React/FastAPI đạt acceptance trong parity matrix.
- UI target dùng năm nhãn tiếng Việt trong sidebar và floating launcher; legacy labels không quyết định target UX.

## Khoảng trống trước cutover

React đã phủ shell, Tổng quan, H1–H4 và floating AI cơ bản qua FastAPI. Production-like one-command
demo/cutover và browser evidence đầy đủ vẫn chưa hoàn tất; Streamlit tiếp tục là frozen fallback.

## Chạy API Phase 1

```bash
python3 -m uvicorn server.main:app --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
```

Để xem contract: `http://127.0.0.1:8000/docs` hoặc `/openapi.json`. API chỉ đọc snapshot
`data/processed/`; Streamlit vẫn là fallback frozen, chạy độc lập bằng lệnh legacy.
