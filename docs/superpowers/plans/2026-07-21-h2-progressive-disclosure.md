# H2 Progressive Disclosure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Giảm tải nhận thức H2 và làm drill-down tỉnh phản hồi ngay sau map.

**Architecture:** Giữ `analysis.provincial` là logic thuần. Page chỉ compose map,
drill-down, boxplot và hai tab phụ; delta ranking dùng DataFrame wide từ
`slope_pair`, không vẽ full slopegraph.

**Tech Stack:** Python, pandas, Streamlit, Plotly, pytest, Streamlit AppTest.

## Global Constraints

- Không đổi pipeline/raw data/AI/log; chỉ đọc `data/processed/`.
- `total_papi_6dim` 2011–2024, `total_papi` từ 2018; không so chéo thước đo.
- Không nội suy dữ liệu thiếu; ghi rõ số tỉnh có dữ liệu và nguồn PAPI theo section.
- Test focused trước, full pytest sau; Chrome inspect chỉ sau server đã chạy.

### Task 1: Delta ranking logic

**Files:** Modify `src/analysis/provincial.py`, `tests/test_provincial.py`.

- [ ] Viết test `largest_absolute_changes` chọn đúng 7 tỉnh theo `abs(delta)`,
  giữ cột `delta` và trả rỗng khi không có cặp năm.
- [ ] Chạy test, xác nhận fail vì helper chưa tồn tại.
- [ ] Thêm `largest_absolute_changes(prov_year, year_start, year_end, total_col, n=7)`
  dùng `slope_pair`, sort `abs(delta)` giảm dần, validate `n > 0`.
- [ ] Chạy `PYTHONPATH=src pytest -q tests/test_provincial.py`.

### Task 2: Page progressive disclosure

**Files:** Modify `app/pages/provincial.py`, `tests/test_provincial_page.py`.

- [ ] Viết AppTest kiểm tra H2 render ≤ 5 chart ở default và mode 8 vẫn publish
  `dash_context.total_col == total_papi`.
- [ ] Chạy test, xác nhận fail với 8 chart hiện tại.
- [ ] Sắp lại page: map/chip → ranking/radar → boxplot → tabs Cực trị/Thay đổi.
  Xóa mean bar và full slopegraph; default top/bottom 5; tab delta dùng bar ngang
  phân kỳ từ `largest_absolute_changes`.
- [ ] Đồng bộ scale/year/region/province với `st.query_params`, có parse guard
  cho giá trị URL không hợp lệ.
- [ ] Chạy focused tests và full `PYTHONPATH=src pytest -q`.

### Task 3: Runtime inspection

**Files:** Create `plans/reports/h2-improvement-inspection-260721-1247.md`.

- [ ] Cài Chrome/Chromium hoặc dùng executable sẵn có, chạy qua Xvfb với remote
  debugging local và bảo đảm Chrome DevTools MCP list/snapshot được tab H2.
- [ ] Inspect desktop 1366 px, map click, tabs và narrow viewport; kiểm tra console
  error và overflow. Ghi bằng chứng/finding vào report.
- [ ] Chạy `git diff --check`; không commit browser cache, profile, log hoặc secret.
