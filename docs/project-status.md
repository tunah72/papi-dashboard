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
| Dashboard sáu route | Đã có code Streamlit legacy | `app/main.py`, `app/pages/` |
| Tổng quan | Có KPI, bản đồ, ranking và context AI | `app/pages/overview.py` |
| H1 — Diễn biến | Có trend, COVID, heatmap, drill-down | `app/pages/time_trend.py`, `src/analysis/trend.py` |
| H2 — Vùng & tỉnh | Có phân phối, ranking, benchmark, profile | `app/pages/provincial.py`, `src/analysis/provincial.py` |
| H3 — Mối quan hệ lĩnh vực | Có correlation, scatter và phân tán | `app/pages/dimension.py`, `src/analysis/dimensions.py` |
| H4 — Thay đổi & phân nhóm | Có delta và KMeans profile | `app/pages/dynamics.py`, `src/analysis/dynamics.py` |
| AI Assistant | Có luồng chờ duyệt → thực thi local → log | `app/pages/ai_assistant.py`, `app/ai/` |
| Test offline | 95 test pass sau Phase 1 | `python3 -m pytest -q` |
| FastAPI local data API | Có health, OpenAPI và 7 dashboard view-model endpoints; chưa có AI/executor/log HTTP | `server/`, `tests/test_fastapi_contract.py` |
| React Phase 2–4 | Có shell TypeScript strict, sidebar và 5 route dữ liệu thật: Tổng quan, H1–H4; route AI công bố boundary, không sinh/chạy code | `frontend/`, 28 unit + 27 E2E pass, browser QA 1440–390 px |
| Báo cáo LaTeX | Ngoài scope migration | `report/` |

## Ranh giới đang áp dụng

- Data gốc và processed là bất biến trong migration; app/target UI không đọc Excel raw trực tiếp.
- Code AI phải được hiện, người dùng sửa/duyệt, rồi mới chạy local; executor demo local không phải sandbox public.
- Streamlit là fallback frozen đến khi React/FastAPI đạt acceptance trong parity matrix.
- UI target sẽ dùng sáu nhãn tiếng Việt và sidebar trái theo ADR; legacy labels không phải nguồn quyết định target UX.

## Khoảng trống trước cutover

React Phase 2–4 đã phủ shell, Tổng quan và H1–H4; route AI hiện chỉ là boundary minh bạch, không phải UI
AI thật. Production-like one-command demo/cutover chưa được tạo. FastAPI Phase 1 có OpenAPI/view-model
data contract, nhưng chưa bao gồm API AI, API thực thi hay API logs. AI demo vẫn chạy ở Streamlit theo
luồng hiện code → sửa → phê duyệt → thực thi local → log. Không coi test hiện tại là bằng chứng đã cutover.

## Chạy API Phase 1

```bash
python3 -m uvicorn server.main:app --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
```

Để xem contract: `http://127.0.0.1:8000/docs` hoặc `/openapi.json`. API chỉ đọc snapshot
`data/processed/`; Streamlit vẫn là fallback frozen, chạy độc lập bằng lệnh legacy.
