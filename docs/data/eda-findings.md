# EDA — Phát hiện chính (PAPI 2011–2024)

> Phân tích trên `data/processed/`. Notebook: `notebooks/eda.ipynb`. Biểu đồ: `reports/figures/`.
> Đây là đầu vào cho thiết kế dashboard (Phase 3) và bộ câu hỏi vấn đáp (Phase 6).

## A. Chất lượng dữ liệu
- 869/882 tỉnh-năm có tổng hợp lệ; **13 ô thiếu thật tại nguồn** (2014, 2018, 2021–2024). Đã ghi log, không bịa.
- Điểm trục nằm trong (1,10], tổng trong [31,49] — hợp lệ.

## B. 5 phát hiện cốt lõi

### 1. Dân chấm cao "dịch vụ", chấm thấp "quản trị mới" (eda_box)
Điểm TB toàn kỳ: **Dịch vụ công (7.15)** và **Thủ tục hành chính (7.12)** cao nhất; **Quản trị điện tử (3.10)** và **Quản trị môi trường (3.70)** thấp nhất. Hai trục mới nhất (thêm 2018) bị chấm kém nhất → đây là "điểm đau" rõ ràng.

### 2. Tham nhũng & dịch vụ cải thiện; minh bạch & giải trình đi xuống (eda_trend)
Thay đổi đầu→2024:
| Trục | Thay đổi | Hướng |
|---|---|---|
| Kiểm soát tham nhũng | **+1.30** | tốt lên mạnh nhất |
| Dịch vụ công | +0.95 | tốt lên |
| Thủ tục HC | +0.33 | nhích |
| **Minh bạch** | −0.25 | đi xuống |
| **Tham gia** | −0.38 | đi xuống |
| **Môi trường** (từ 2018) | −0.94 | xấu đi |
| **Trách nhiệm giải trình** | −1.30 | xấu nhất |

→ Câu chuyện: mảng **"phục vụ"** (chống tham nhũng, dịch vụ) tiến bộ; mảng **"dân chủ cơ sở"** (giải trình, tham gia, minh bạch) trì trệ/thụt lùi.

### 3. Minh bạch là "trục trung tâm" (eda_corr)
Tương quan mạnh nhất giữa các trục: **Tham gia ~ Minh bạch = 0.70**; Minh bạch còn liên hệ với Kiểm soát tham nhũng (0.48), Thủ tục HC (0.47), Giải trình (0.42). Minh bạch như "trục xương sống" của quản trị tốt.

### 4. Bản đồ vùng miền rõ rệt (eda_topbottom, eda_region)
- 2024: **Quảng Ninh #1** (47.8), Tây Ninh, Bình Thuận theo sau. Đáy: Kiên Giang, Kon Tum, Cần Thơ.
- Theo vùng (2024): **ĐB Sông Hồng (44.3)** và **Đông Nam Bộ (44.1)** dẫn đầu; **Tây Nguyên (41.2)** thấp nhất.
- **Hà Tĩnh ổn định nhất**: vào top10 cả **10 năm** (Quảng Bình 9, Quảng Trị 8).

### 5. ⚠️ Cảnh báo phương pháp: KHÔNG so sánh tổng PAPI qua mốc 2018
Mọi tỉnh "nhảy" +10–12 điểm năm 2018 — đây là **artifact do thêm D7, D8** (6→8 trục), không phải tiến bộ thật. Khi vẽ xu hướng tổng, phải tách giai đoạn 2011–2017 (6 trục) và 2018–2024 (8 trục), hoặc chỉ so theo từng trục.

## C. ≥4 câu hỏi phân tích cho vấn đáp (1 người/câu)

1. **Thời gian:** Trục nào cải thiện/thụt lùi mạnh nhất 2011–2024? Vì sao mảng "phục vụ" tiến mà mảng "dân chủ cơ sở" lùi?
2. **Quan hệ:** "Minh bạch" có thực sự kéo theo "Kiểm soát tham nhũng" không? — hồi quy tuyến tính D2→D4, kiểm định.
3. **Không gian:** Vùng nào quản trị tốt nhất trong mắt dân? Vì sao **Tây Nguyên** luôn ở đáy? So sánh hồ sơ 8 trục của vùng cao vs vùng thấp.
4. **Phân nhóm:** Phân cụm (k-means) 63 tỉnh theo hồ sơ 8 trục → có mấy "kiểu" tỉnh? Vì sao **Hà Tĩnh** ổn định top suốt 14 năm?

(Câu dự phòng) Hai trục mới — Môi trường & Quản trị điện tử — bị chấm thấp nhất: tỉnh nào đang làm tốt nhất, học được gì?

## D. Hàm ý cho dashboard (Phase 3)
- Trang **Tổng quan**: bản đồ + KPI + top/bottom (eda_topbottom, eda_region).
- Trang **Xu hướng**: line theo trục, **tách 2 giai đoạn** ở mốc 2018 (eda_trend).
- Trang **Quan hệ**: heatmap tương quan + scatter D2–D4 (eda_corr).
- Trang **So sánh tỉnh/vùng**: radar 8 trục, chọn tỉnh.

## E. Biểu đồ đã xuất (reports/figures/, sinh từ notebooks/eda.ipynb)
`eda_box` · `eda_trend` · `eda_topbottom` · `eda_region` · `eda_corr`
