# Phân công xây dựng dashboard

Deadline thiết kế dashboard: **26/6**. Nguyên tắc: mỗi thành viên sở hữu một vertical slice gồm các
tệp riêng, không tệp nào bị hai người cùng sửa, chỉ phụ thuộc phần hạ tầng chung đã freeze.

## 1. Đợt nền — ĐÃ XONG (freeze, không sửa)

Do Dương Tuấn Anh đảm nhận, đã hoàn thành và đóng băng:

- git + cây thư mục `app/`; cột `total_papi_6dim`; `vietnam_provinces.geojson`.
- `app/main.py` multipage; module dùng chung `app/lib/` (`config`, `data`, `charts`, `filters`, `layout`).
- Theme OWID (`.streamlit/config.toml`), palette 8 lĩnh vực, helper `kpi_cards`/`section_header`/`chart`.
- Trang **Overview** và trang mẫu **H1 `time_trend.py`** (xem như khuôn để copy).
- Khung AI module: `api_ai`, `api_exec`, `api_logs`, `ai_assistant`, plugin registry.

Quy ước thiết kế bắt buộc đọc trước khi làm: `docs/design_convention.md`.

## 2. Vertical slice của từng thành viên

Mỗi người chỉ tạo/sửa các tệp của mình; copy khung từ `app/pages/time_trend.py`.

| Thành viên | Hướng | Page | Analysis module | AI technique |
|---|---|---|---|---|
| Dương Tuấn Anh | H1 Diễn biến theo thời gian | `time_trend.py` ✅ | `analysis/trend.py` | `techniques/trend_classification.py` |
| Lê Xuân Trí | H2 So sánh giữa các tỉnh | `provincial.py` | `analysis/spatial.py` | `techniques/anomaly.py` |
| Nguyễn Trần Trung Kiên | H3 Phân tích theo lĩnh vực | `dimension.py` | `analysis/dimension.py` | `techniques/insight.py` |
| Lê Đức Phúc | H4 Động lực thay đổi & phân nhóm | `dynamics.py` | `analysis/dynamics.py` | `techniques/clustering.py` |

### Nội dung gợi ý từng trang (biểu đồ + tương tác)
Đây chỉ là gợi ý. Mỗi thành viên **tự do chọn và thêm biểu đồ** phù hợp với hướng phân tích của mình,
miễn đạt Definition of Done (mục 4) và giữ đồng bộ style (xem mục 5).
- **H2 (Trí):** choropleth bản đồ theo năm · bar xếp hạng top/bottom tỉnh · slopegraph hai mốc năm ·
  boxplot phân bố theo vùng. Tương tác: chọn năm, click một tỉnh → drill chi tiết tỉnh đó.
- **H3 (Kiên):** radar 8 lĩnh vực cho một tỉnh · heatmap vùng × lĩnh vực · correlation giữa các lĩnh vực ·
  boxplot lĩnh vực theo vùng. Tương tác: chọn tỉnh/lĩnh vực để so sánh.
- **H4 (Phúc):** scatter hai lĩnh vực · clustering k-means nhóm tỉnh · slopegraph mức thay đổi ·
  bảng/heatmap chuyển dịch tier qua năm. Tương tác: chọn số nhóm, chọn cặp lĩnh vực.

Chi tiết câu hỏi và ý nghĩa từng hướng: `docs/dashboard_plan.md`.

## 3. Kế hoạch theo PHASE (16/6 → 26/6)

| PHASE | Mốc | Mục tiêu chung |
|---|---|---|
| P1 Khởi động & nắm khuôn | 16–18/6 | Dựng môi trường, đọc khuôn, chốt câu hỏi + biểu đồ |
| P2 Dựng trang phân tích | 18–22/6 | Mỗi người dựng page + analysis module (TRỌNG TÂM) |
| P3 Tương tác & storytelling | 22–24/6 | Thêm filter/drill/hover, tiêu đề kết luận, văn phong |
| P4 Tích hợp & chốt | 24–26/6 | Merge, review chéo, verify, tập demo |

### P1 — Khởi động & nắm khuôn (16–18/6)
- **Tất cả:** `git pull`, dựng `.venv` theo README, chạy `streamlit run app/main.py`; đọc
  `design_convention.md` và code `time_trend.py`; tạo branch riêng `feat/<hướng>`.
- **Mỗi người:** chốt 2–3 câu hỏi định hướng + danh sách biểu đồ cho trang của mình.
- **Tuấn Anh:** hỗ trợ giải thích khuôn; bổ sung hàm vào `charts.py` nếu ai cần loại biểu đồ mới.

### P2 — Dựng trang phân tích (18–22/6)
- **Trí / Kiên / Phúc:** dựng `app/pages/<của mình>.py` + `src/analysis/<của mình>.py` theo khuôn H1
  (page_header → control bar → KPI cards → lưới biểu đồ); dùng dữ liệu đã xử lý, tên lĩnh vực đầy đủ.
- **Tuấn Anh:** hoàn thiện `analysis/trend.py` tách hàm khỏi H1; review sớm page của ba người;
  giữ đồng bộ `charts.py`/`config.py`.

### P3 — Tương tác & storytelling (22–24/6)
- **Trí / Kiên / Phúc:** thêm tương tác (filter page-level, click-to-drill, hover); đặt tiêu đề biểu đồ
  là kết luận bám số liệu; viết nhận xét; rà văn phong khoa học, bỏ mã viết tắt.
- **Tuấn Anh:** kiểm tra nhất quán màu/bố cục/tương tác giữa bốn trang.

### P4 — Tích hợp & chốt (24–26/6)
- **Tất cả:** merge branch vào `main`; review chéo (mỗi người review trang người khác); chạy
  AppTest + server thật, fix lỗi; tập demo.
- **Tuấn Anh:** chủ trì merge và verify cuối; cập nhật `WORKFLOW.md`.

> AI technique plugin (mỗi người một cái) làm song song trong P3 nếu kịp, hoặc sau 26/6 (thuộc Phase 4
> đề bài — module AI). Deadline 26/6 ưu tiên cho **bốn trang dashboard**.

## 4. Definition of Done cho một trang
1. Chạy `streamlit run app/main.py` không lỗi; trang boot sạch.
2. Có tiêu đề trang mô tả nội dung + control bar + KPI + ≥3 biểu đồ.
3. Tiêu đề biểu đồ là kết luận bám số liệu; có nhận xét; ghi nguồn.
4. Tên lĩnh vực đầy đủ (không D1..D8); văn phong khoa học; màu theo palette chung.
5. Có ít nhất một tương tác có ý nghĩa (filter hoặc drill).

## 5. Contract và quy ước git

**Chia sẻ design system, không chia sẻ catalog biểu đồ.** Thứ giữ bốn trang đồng bộ là style + token +
khung trang, không phải các hàm vẽ.

- **Bắt buộc dùng chung:** palette trong `config`, `charts.apply_owid(...)`, khung `layout`
  (`page_header`/`kpi_cards`/`section_header`/`chart`), theme `config.toml`, `data.load_data`.
- **Page tự do** chọn biểu đồ, bố cục, filter, tương tác. `charts.py` là **menu primitive tuỳ chọn**;
  tự viết hàm vẽ inline trong page hoặc thêm hàm mới vào `charts.py` (chỉ thêm ở cuối, không sửa hàm
  có sẵn). Mọi biểu đồ tự dựng **phải gọi** `charts.apply_owid(...)` và lấy màu từ `config`.
- **Không sửa** chữ ký hàm có sẵn trong `app/lib/`, `app/main.py`, theme `config.toml`, `dim_indicator.csv`.
- Mỗi người một branch `feat/<hướng>`. Page chỉ đọc dữ liệu đã xử lý, không truy cập raw. Không commit `secrets.toml`.

## 6. Tính độc lập
Các vertical slice không gọi lẫn nhau nên mỗi người chạy/test page của mình ngay sau đợt nền; một
người chậm không chặn người khác, và merge gần như không xung đột.

## 7. Checklist từng thành viên

### P1 — Tất cả (16–18/6)
- [ ] `git pull`; dựng `.venv` theo README; chạy `streamlit run app/main.py` thành công.
- [ ] Đọc `docs/design_convention.md` và đọc code `app/pages/time_trend.py` (khuôn mẫu).
- [ ] Tạo branch riêng `feat/<hướng>` (vd `feat/provincial`).
- [ ] Chốt 2–3 câu hỏi định hướng + danh sách biểu đồ cho trang của mình (ghi vào `dashboard_plan.md`).

### Dương Tuấn Anh — H1 + tích hợp (trang đã xong)
P2 (18–22/6)
- [ ] Tách logic H1 ra `src/analysis/trend.py` (hàm thuần: slope theo năm, delta từng lĩnh vực, so sánh giai đoạn).
- [ ] Review sớm page của Trí/Kiên/Phúc; thêm hàm vào `charts.py` khi ai cần biểu đồ mới.

P3 (22–24/6)
- [ ] Rà nhất quán màu/bố cục/tương tác giữa bốn trang.
- [ ] (nếu kịp) AI plugin `trend_classification.py`: phân loại lĩnh vực cải thiện/ổn định/suy giảm.

P4 (24–26/6)
- [ ] Chủ trì merge ba branch vào `main`; chạy AppTest + server thật; fix lỗi.
- [ ] Cập nhật `WORKFLOW.md`.

### Lê Xuân Trí — H2 So sánh giữa các tỉnh
P2 (18–22/6)
- [ ] `app/pages/provincial.py`: page_header + control bar (năm, vùng) + KPI cards.
- [ ] Choropleth bản đồ tổng điểm theo năm (`charts.choropleth`).
- [ ] Bar xếp hạng top/bottom tỉnh (`charts.bar_ranking`).
- [ ] `src/analysis/spatial.py`: hàm xếp hạng, gom theo vùng, phát hiện outlier (z-score hoặc IQR).

P3 (22–24/6)
- [ ] Slopegraph hai mốc năm; boxplot phân bố theo vùng.
- [ ] Tương tác: chọn năm; click một tỉnh trên bản đồ → drill chi tiết tỉnh (line/radar tỉnh đó).
- [ ] Tiêu đề biểu đồ là kết luận bám số liệu; viết nhận xét; tên lĩnh vực đầy đủ.
- [ ] (nếu kịp) AI plugin `anomaly.py`: phát hiện tỉnh bất thường.

P4 (24–26/6)
- [ ] Merge vào `main`; review chéo một trang của bạn khác; `streamlit run` không lỗi.

### Nguyễn Trần Trung Kiên — H3 Phân tích theo lĩnh vực
P2 (18–22/6)
- [ ] `app/pages/dimension.py`: page_header + control bar (chọn tỉnh/vùng/năm) + KPI cards.
- [ ] Radar 8 lĩnh vực cho một tỉnh (`charts.radar`).
- [ ] Heatmap vùng × lĩnh vực (`charts.heatmap`).
- [ ] `src/analysis/dimension.py`: ma trận correlation giữa các lĩnh vực, trung bình theo vùng.

P3 (22–24/6)
- [ ] Correlation heatmap giữa các lĩnh vực; boxplot lĩnh vực theo vùng.
- [ ] Tương tác: chọn tỉnh để so sánh radar; chọn lĩnh vực để xem phân bố.
- [ ] Tiêu đề kết luận + nhận xét; tên lĩnh vực đầy đủ.
- [ ] (nếu kịp) AI plugin `insight.py`: sinh nhận xét tự động cho một lĩnh vực/tỉnh.

P4 (24–26/6)
- [ ] Merge vào `main`; review chéo một trang của bạn khác; `streamlit run` không lỗi.

### Lê Đức Phúc — H4 Động lực thay đổi & phân nhóm
P2 (18–22/6)
- [ ] `app/pages/dynamics.py`: page_header + control bar (chọn cặp lĩnh vực, số nhóm, năm) + KPI cards.
- [ ] Scatter hai lĩnh vực; slopegraph mức thay đổi (`charts.slopegraph`).
- [ ] `src/analysis/dynamics.py`: k-means nhóm tỉnh (StandardScaler + KMeans), tính chuyển dịch tier qua năm.

P3 (22–24/6)
- [ ] Scatter tô màu theo nhóm cluster; heatmap/bảng chuyển dịch tier qua năm.
- [ ] Tương tác: slider chọn số nhóm; chọn cặp lĩnh vực; click điểm → xem tỉnh.
- [ ] Tiêu đề kết luận + nhận xét; tên lĩnh vực đầy đủ.
- [ ] (nếu kịp) AI plugin `clustering.py`: gom nhóm tỉnh theo hồ sơ lĩnh vực.

P4 (24–26/6)
- [ ] Merge vào `main`; review chéo một trang của bạn khác; `streamlit run` không lỗi.

> Mỗi trang phải đạt 5 tiêu chí **Definition of Done** ở mục 4 trước khi tick xong P4.
