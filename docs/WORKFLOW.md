# WORKFLOW — Đồ án Trực quan hóa Dữ liệu (PAPI)

Nhóm 4 người. Dataset: PAPI (Chỉ số Hiệu quả Quản trị và Hành chính công cấp tỉnh, 2011-2024).
Hai khối sản phẩm: dashboard trực quan và AI module human-in-the-loop. Kèm báo cáo LaTeX và vấn đáp.

Trạng thái: [XONG] / [ĐANG LÀM] / [CHƯA].

## Phase 0 — Khởi tạo và dữ liệu thô  [XONG]
- [x] Research PAPI (nguồn, 8 trục, phương pháp luận); tải 14 tệp raw vào `data/raw/`
- [x] Khám phá cấu trúc raw (`docs/data_understanding.md`): 3 thời kỳ và 8 điểm cần xử lý
- [x] git init + cây thư mục (`data/ docs/ src/ app/ notebooks/`)
- [x] `requirements.txt` (pinned) + venv verify chạy sạch
- [x] `README.md` (cài venv, build lại dữ liệu, chạy dashboard, cấu hình AI)
- [x] 3 notebook narrated, chạy verify không lỗi

## Phase 1 — Dataset chuẩn  [XONG]
- [x] `src/build_dataset.py` + `src/papi_lib.py`: 2 nhánh parser, chọn nguồn canonical mỗi năm
- [x] `data/processed/`: `fact_papi_long` (6.094), `agg_province_year` (panel 882, có `total_papi_6dim`),
      `agg_national_year`, `dim_province`, `dim_indicator`
- [x] `docs/data_processing_log.md`; toàn bộ QC PASS, tổng khớp official (lệch 0.0000)
- [x] 13 tỉnh-năm thiếu thật được ghi nhận, không bịa số
- [ ] (stretch) thêm cấp sub-dimension nếu cần về sau

## Phase 2 — EDA  [XONG]
- [x] `notebooks/eda.ipynb`: quality, univariate, temporal, spatial, multivariate, outlier
- [x] 5 biểu đồ (`reports/figures/`) + `docs/eda_findings.md` (5 insight + 4 câu hỏi vấn đáp)
- [x] Cảnh báo phương pháp: không so tổng PAPI vắt qua mốc 2018 (artifact 6→8 trục)

## Phase 3 — Dashboard Streamlit  [ĐANG LÀM]
Kế hoạch: `docs/dashboard_plan.md`. Kiến trúc: `docs/architecture.md`. Phân công: `docs/work_assignment.md`.
Convention thiết kế: `docs/design_convention.md`.
- [x] Đợt nền F1-F6 (`docs/foundation_checklist.md`): cây `app/`, `total_papi_6dim`, geojson,
      `app/lib/` (config, data, charts, filters, layout), `app/main.py` multipage, trang Overview
- [x] Nền tảng style OWID: theme `config.toml`, palette OWID (8 lĩnh vực + vùng + tier + thang),
      `charts.py` bake style (tiêu đề+phụ đề+nguồn, nhãn cuối đường, heatmap, diverging bar),
      `layout.py` helper (page_header, kpi_cards có sparkline, section_header, chart)
- [x] Trang H1 `time_trend.py` hoàn thiện làm khuôn: bố cục lưới card, KPI, line tổng,
      cột so sánh COVID, heatmap lĩnh vực×năm, diverging bar; tương tác click-to-drill (on_select),
      hover, range năm; văn phong PAPI (tên lĩnh vực đầy đủ, nhãn tổng theo chế độ)
- [x] Verify: pipeline pass, app boot (AppTest + server thật HTTP 200)
- [ ] 3 trang phân tích còn lại (mỗi thành viên 1 vertical slice + 1 `src/analysis` module)
- [ ] Storytelling: nhận xét trên mỗi biểu đồ

## Phase 4 — AI module human-in-the-loop  [ĐANG LÀM]
Provider: Gemini (key trong `.streamlit/secrets.toml`, không commit).
- [x] Framework F6: `api_ai` (Gemini), `api_exec` (sandbox, chặn import nguy hiểm), `api_logs`,
      `registry`, trang `ai_assistant`
- [x] Luồng chờ duyệt → sửa → phê duyệt → thực thi local → ghi log
- [ ] 4 AI technique plugin (mỗi thành viên 1: trend classification, anomaly, insight, clustering)
- [ ] Chuẩn bị ≥4 câu hỏi demo chạy qua module

## Phase 5 — Báo cáo LaTeX  [CHƯA]
- [ ] `report/`: giới thiệu, nguồn và xử lý dữ liệu, EDA, dashboard, AI module, kết luận
- [ ] Phần tóm tắt quá trình dùng AI (yêu cầu đặt, kết quả, thay đổi, nhận xét)
- [ ] Ghi nguồn dữ liệu đầy đủ

## Phase 6 — Vấn đáp  [CHƯA]
- [ ] ≥4 câu hỏi phân tích (= số thành viên), mỗi người nắm một mảng
- [ ] Tập demo dashboard và AI module; chuẩn bị câu hỏi ngoài lề

---

## Phụ thuộc
Phase 1 → 2 → 3. Phase 4 framework đã xong (cần Phase 1). Bốn vertical slice của Phase 3 và bốn
technique của Phase 4 làm song song theo `work_assignment.md`. Phase 5-6 chạy cuối kỳ.

## Quy ước
- `data/raw/` bất khả xâm phạm; mọi xử lý ra `data/processed/`, có log.
- `src/` không import streamlit; code do AI sinh phải qua phê duyệt mới chạy.
- Secrets không commit; mỗi người tự tạo `.streamlit/secrets.toml` từ `.example`.
