# Checklist đợt nền (foundation, Phase 3)

Phần dùng chung, làm một lần rồi freeze, trước khi 4 thành viên làm song song. Quy trình: implement
từng phase, báo cáo, rồi tiếp phase sau. Trạng thái: [ ] chưa làm, [x] xong.

## Phase F1: Project setup [XONG]
- [x] `git init` + `.gitignore` (bỏ qua `__pycache__/`, `*.pyc`, `.DS_Store`, `~$*`, `secrets.toml`, giữ `data/`)
- [x] Cây thư mục `app/` (`pages/`, `lib/`, `ai/techniques/`), `src/analysis/`, `logs/`
- [x] Bổ sung `requirements.txt`: streamlit, plotly, scikit-learn, scipy

## Phase F2: Data prerequisites [XONG]
- [x] Thêm cột `total_papi_6dim` (tổng D1-D6, liền mạch 2011-2024) vào `src/build_dataset.py`
- [x] Chạy lại pipeline, verify QC pass và cross-check
- [x] Cập nhật ô aggregate trong `notebooks/preprocessing.ipynb` (cross-check vẫn KHỚP)
- [x] Tạo `data/processed/vietnam_provinces.geojson` (nguồn geoBoundaries ADM1, gắn `province_id`, phủ đủ 63 tỉnh)

## Phase F3: App skeleton + core lib [XONG]
- [x] `app/lib/config.py` (paths, region order, tier, scale mode, thêm src vào path)
- [x] `app/lib/data.py` (`load_data` với `@st.cache_data` + `_load_tables` thuần, `dim_maps`)
- [x] `app/lib/filters.py` (selector: scale mode, year, year range, region, province, dimension)
- [x] `app/main.py` (multipage navigation) + 6 page stub trong `app/pages/`
- [x] Verify: app boot không exception (AppTest), data nạp đủ 6 bảng + geojson

## Phase F4: Charts library [XONG]
- [x] `app/lib/charts.py`: 7 hàm plotly (choropleth, line_trend, bar_ranking, radar, heatmap,
      boxplot, slopegraph), verify với dữ liệu thật đều trả về Figure hợp lệ
- [x] Sửa drift `dim_indicator.csv` (thiếu color/sort), mở rộng cross-check notebook để bắt drift bảng tra cứu

## Phase F5: Overview page [XONG]
- [x] `app/pages/overview.py` (4 KPI, choropleth theo năm, top/bottom 10, link tới 4 page)
- [x] Verify AppTest: boot không exception, dùng `width="stretch"` (chuẩn streamlit mới)

## Phase F6: AI module framework [XONG] (LLM provider: Gemini)
- [x] `app/ai/api_logs.py` (ghi/đọc nhật ký JSON lines), `app/ai/api_exec.py` (sandbox, chặn import nguy hiểm)
- [x] `app/ai/api_ai.py` (gọi Gemini qua google-genai, trả code + giải thích, parser chịu code fence)
- [x] `app/ai/registry.py` (plugin registry + discovery) + plugin ví dụ `example_describe.py`
- [x] `app/pages/ai_assistant.py` (luồng chờ duyệt -> sửa -> phê duyệt -> thực thi -> log)
- [x] `.streamlit/secrets.toml.example` (mẫu GEMINI_API_KEY) + thêm google-genai vào requirements
- [x] Verify: registry discover, exec chạy code + chặn import os, parser, page boot graceful khi thiếu key

## Sau đợt nền [HOÀN TẤT]
Toàn bộ đợt nền đã xong và verify. Bốn thành viên bắt đầu vertical slice theo `docs/work_assignment.md`.
Trước khi chạy AI thật: tạo `.streamlit/secrets.toml` với GEMINI_API_KEY (lấy free tại aistudio.google.com).
Mỗi phase tiếp theo (4 page, report) có checklist riêng khi tới.
