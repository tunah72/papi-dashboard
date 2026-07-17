# Tìm hiểu dữ liệu PAPI (Data Understanding)

> Tài liệu nền cho báo cáo — phần "Nguồn dữ liệu & Tìm hiểu cấu trúc". Tổng hợp toàn bộ quá trình
> khảo sát 14 file raw 2011–2024 trước khi build dataset. Mọi số liệu mẫu trong tài liệu này được
> trích trực tiếp từ file gốc trong `data/raw/`.

---

## 1. Dataset là gì

**PAPI** — *Chỉ số Hiệu quả Quản trị và Hành chính công cấp tỉnh ở Việt Nam* (The Viet Nam Provincial
Governance and Public Administration Performance Index).

- **Đơn vị thực hiện:** UNDP Việt Nam + CECODES + RTA + Mặt trận Tổ quốc.
- **Bản chất:** khảo sát cảm nhận của **người dân** về chính quyền địa phương, tổng hợp thành điểm cấp tỉnh.
- **Quy mô khảo sát:** ~14.000–19.000 người/năm (2024: 18.894 người ≥18 tuổi, chọn ngẫu nhiên).
- **Phạm vi:** 63 tỉnh/thành, hằng năm **2011–2024** (toàn quốc từ 2011).
- **Đơn vị quan sát của file ta có:** **cấp tỉnh đã tổng hợp** (KHÔNG phải microdata từng người).
- **Nguồn:** papi.org.vn (công khai, có phương pháp luận minh bạch).

**Ý nghĩa:** mỗi con số = mức độ hài lòng/cảm nhận của dân tỉnh đó với chính quyền trong năm đó.
Đây là dữ liệu **chủ quan** (đo niềm tin của dân), không phải số liệu hành chính khách quan — vừa là
hạn chế, vừa là giá trị riêng.

## 2. Dữ liệu được tạo ra như thế nào

Câu hỏi khảo sát (phỏng vấn dân) → tổng hợp theo công thức của PAPI → điểm cấp tỉnh, xếp theo **4 tầng**:

```
Tổng PAPI (10–80 điểm)             ← điểm tổng kết của tỉnh
  └─ 8 trục nội dung (1–10 điểm)   ← "môn học"  (D1…D8)
       └─ trục thành phần          ← "bài kiểm tra" trong môn (sub-dimension)
            └─ chỉ tiêu thô (%)     ← câu hỏi khảo sát gốc
```

**Quy tắc cộng dồn:** Trục = tổng các trục thành phần; Tổng PAPI = tổng 8 trục.
Đã kiểm chứng trên file thật (An Giang 2016, trục D1): 0.874 + 1.552 + 1.145 + 0.910 = **4.481** ✓.

**Thang điểm theo số thành phần:** trục có 4 thành phần → mỗi cái 0.25–2.5; trục có 3 thành phần →
mỗi cái 0.33–3.33. Cộng lại đều ra 1–10.

## 3. Tám trục nội dung

| Mã | Tên (VI) | Tên (EN) | Có từ | Đo gì |
|---|---|---|---|---|
| D1 | Tham gia của người dân ở cấp cơ sở | Participation | 2011 | Dân được tham gia việc thôn/xã |
| D2 | Công khai, minh bạch | Transparency | 2011 | Công khai thông tin, ngân sách, hộ nghèo |
| D3 | Trách nhiệm giải trình với người dân | Vertical Accountability | 2011 | Chính quyền lắng nghe, xử lý phản ánh |
| D4 | Kiểm soát tham nhũng trong khu vực công | Control of Corruption | 2011 | Vòi vĩnh, hối lộ, "chạy" việc |
| D5 | Thủ tục hành chính công | Public Admin. Procedures | 2011 | Làm giấy tờ (sổ đỏ, chứng thực) có dễ |
| D6 | Cung ứng dịch vụ công | Public Service Delivery | 2011 | Y tế, giáo dục, hạ tầng, an ninh |
| D7 | Quản trị môi trường | Environmental Governance | **2018** | Không khí, nước, xử lý ô nhiễm |
| D8 | Quản trị điện tử | E-Governance | **2018** | Dịch vụ công online, internet |

Điểm cao = dân hài lòng hơn. **D1–D6 có từ 2011; D7, D8 chỉ có từ 2018.**

## 4. Các trục thành phần (sub-dimension)

Trong file 2011–2017, mỗi trục được tách chi tiết ở các sheet "Điểm thành phần 1…6":

- **D1 Tham gia:** 1.1 Tri thức công dân · 1.2 Cơ hội tham gia · 1.3 Chất lượng bầu cử · 1.4 Đóng góp tự nguyện
- **D2 Minh bạch:** 2.1 Tiếp cận thông tin · 2.2 Công khai danh sách hộ nghèo · 2.3 Công khai ngân sách xã
- **D3 Trách nhiệm giải trình:** 3.1 Tương tác với chính quyền · 3.2 Giải quyết khiếu nại, tố giác · 3.3 Tiếp cận dịch vụ tư pháp
- **D4 Kiểm soát tham nhũng:** 4.1 Trong chính quyền · 4.2 Trong dịch vụ công · 4.3 Công bằng tuyển dụng · 4.4 Quyết tâm chống tham nhũng
- **D5 Thủ tục hành chính:** 5.1 Chứng thực, xác nhận · 5.2 Cấp phép xây dựng · 5.3 Cấp sổ đỏ · 5.4 Thủ tục cấp xã/phường
- **D6 Dịch vụ công:** 6.1 Y tế công lập · 6.2 Giáo dục tiểu học công · 6.3 Hạ tầng căn bản · 6.4 An ninh trật tự

(Từ 2018 có thêm sub-dimension cho D7, D8.)

## 5. Cấu trúc file — 3 thời kỳ

Dữ liệu trải 3 thời kỳ với cấu trúc **không tương thích**, không thể dùng một parser chung.

### Thời kỳ 1 (2011–2017): tỉnh theo HÀNG
- File `PAPI-YYYY-Dữ-liệu-1.xlsx`. Sheet chính `"<YYYY>PAPI- Bảng tổng hợp kết quả"` (63 tỉnh × 29 cột) + 6 sheet "Điểm thành phần".
- Mỗi **dòng = 1 tỉnh**, mỗi **cột = 1 chỉ số**. Chỉ **6 trục**.

**Mẫu thật (PAPI-2016):**

| Tỉnh | D1 | D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|
| Hà Nội | 5.34 | 5.08 | 4.26 | 5.24 | 7.09 | 6.80 |
| Hà Giang | 5.34 | 5.27 | 4.40 | 5.82 | 6.64 | 6.48 |
| Cao Bằng | 5.21 | 5.50 | 4.44 | 5.53 | 7.02 | 6.63 |

### Thời kỳ 2 & 3 (2018–2024): tỉnh theo CỘT (đảo ngược)
- File `YYYYPAPI_ProvincialIndicators_*.xlsx`. Sheet `"<YYYY>_VIE_ENG"` (~167 dòng × 66 cột). Đủ **8 trục**.
- Mỗi **dòng = 1 chỉ tiêu**, mỗi **cột = 1 tỉnh**. Cột đầu = nhãn, có cột "Thang điểm/Scale".

**Mẫu thật (2023):**

| Chỉ tiêu | Hà Nội | Hà Giang | Cao Bằng | Bắc Kạn |
|---|---|---|---|---|
| Tổng PAPI | 43.96 | 44.25 | 41.66 | 43.35 |
| D1 Tham gia | 5.43 | 5.28 | 4.77 | 5.45 |
| D2 Minh bạch | 5.67 | 5.81 | 4.99 | 5.40 |
| … | … | … | … | … |
| D7 Môi trường | 2.87 | 3.96 | 3.68 | 3.81 |
| D8 Quản trị điện tử | 3.97 | 3.07 | 2.84 | 3.26 |

## 6. Bảng kê 14 file (inventory)

| File | KB | Năm chính | Sheet năm chứa trong file |
|---|---|---|---|
| PAPI-2011-Dữ-liệu-1.xlsx | 52 | 2011¹ | (tab ghi nhầm "2012") |
| PAPI-2012 … 2017 | 52–70 | 2012…2017 | mỗi file 1 năm |
| PAPI2018_ProvincialScores_ByIndicators_VIE.xlsx | 354 | 2018 | 2018 |
| 2019_PAPI_Provincial_indicators2019_VIE_ENG.xlsx | 542 | 2019 | 2019 |
| 2020PAPI_ProvincialIndicators_*.xlsx | 346 | 2020 | 2019–2020 |
| 1.2021PAPI_ProvincialIndicators_*.xlsx | 472 | 2021 | 2019–2021 |
| 2022PAPI_ProvincialIndicators_*.xlsx | 858 | 2022 | 2019–2022 |
| 2023PAPI_ProvincialIndicators_*.xlsx | 1525 | 2023 | 2019–2023 |
| 2024PAPI_ProvincialIndicators_*_34_TinhThanh.xlsx | 1905 | 2024 | 2019–2024 |

¹ Tab trong file 2011 ghi nhầm tên "2012PAPI" nhưng **dữ liệu đúng là 2011** (Hà Nội D1: 2011=5.76 vs 2012=5.51).
**File mới chứa lại năm cũ** → dư thừa, phải chọn nguồn canonical mỗi năm.

## 7. Tám "bẫy" dữ liệu đã phát hiện (cần xử lý minh bạch khi build)

1. **Orientation đảo ngược** giữa 2011–2017 (tỉnh-hàng) và 2018+ (tỉnh-cột) → 2 nhánh parser.
2. **Nhãn trục đổi ngôn ngữ giữa chừng:** 2018–2019 = `Chỉ số nội dung 1`; 2020–2024 = `Dimension 1`.
   → **Parse theo SỐ trục (1–8), không dựa vào chữ.**
3. **6 trục (≤2017) → 8 trục (≥2018):** D7, D8 không tồn tại trước 2018 → để NULL, không bịa.
4. **File mới chứa lại nhiều năm cũ** → chọn nguồn canonical mỗi năm để tránh đếm trùng.
5. **File 2024 `_34_TinhThanh`:** có 4 dòng metadata đầu (map sang 34 tỉnh mới 1/7/2025) + cột trống ngăn
   nhóm. Dữ liệu gốc **vẫn 63 tỉnh cũ** → bỏ metadata + cột trống, dùng cột "tỉnh cũ".
6. **Năm gần đây có nhiều dòng thống kê mỗi chỉ tiêu:** Unweighted / Weighted / 95% CI / Standard Error.
   → Chỉ lấy **Unweighted** (dễ giải thích).
7. **Tên tab lệch năm** (file 2011 → "2012PAPI") → tin theo tên FILE, không theo tên tab.
8. **Tên tỉnh không nhất quán:** khoảng trắng thừa, có/không dấu ("Ha Noi" vs "Hà Nội ") →
   chuẩn hoá một lần qua bảng tra `dim_province.csv`. (Lưu ý thêm: sheet "Điê**m** thành phần 5" gõ sai dấu.)

## 8. Hàm ý cho việc build dataset

**Vì sao phải chuyển sang dạng long:** để wide (1 tỉnh-năm/dòng) chỉ 63 × 14 = **882 dòng** → trượt mốc
2000 của đề. Lưới đầy đủ theo lý thuyết có 7×63×6 + 7×63×8 = **6.174 dòng**. Sau khi giữ dữ liệu
thiếu tại nguồn là thiếu và loại các điểm 0 không hợp lệ, fact thực tế có **6.094 dòng** → vẫn đạt.

**Quyết định build v0 (tối thiểu, để bắt đầu EDA):**
- Lấy **Tổng PAPI + 8 trục**; tạm bỏ trục thành phần (thêm sau nếu EDA cần).
- Chỉ dòng **Unweighted**.
- Chuẩn hoá tên tỉnh → `province_id`; NULL giữ nguyên, đánh dấu.
- Xuất: `fact_papi_long` (gốc) + `agg_province_year` (wide) + `agg_national_year` + bảng tra cứu.
- Ghi `docs/data/processing-log.md` từng bước.

## 9. Đối chiếu ràng buộc đề bài

| Yêu cầu | Đạt | Ghi chú |
|---|---|---|
| Dữ liệu thật | ✅ | Khảo sát thật của UNDP+CECODES+RTA |
| Về Việt Nam, >50% | ✅ | 100% Việt Nam |
| Nguồn đáng tin, minh bạch | ✅ | Công khai, có phương pháp luận |
| ≥7 biến độc lập | ✅ | ≥10 (tỉnh, mã, vùng, năm, trục, điểm, tổng, hạng, tier…) |
| ≥2000 dòng | ✅ | 6.094 dòng thực tế (dạng long) |
| Ghi rõ các bước xử lý | ✅ | `docs/data/processing-log.md` |

**Hạn chế cần nêu trong báo cáo:** dữ liệu là **cảm nhận chủ quan** của dân, không phải số liệu hành
chính; và là **cấp tỉnh đã tổng hợp** nên không phân tích được khác biệt nam/nữ, dân tộc, hộ khẩu
(muốn làm phải tìm thêm microdata).

## 10. Nguồn tham khảo
- PAPI — UNDP Việt Nam: https://www.undp.org/vietnam/projects/papi-viet-nam-provincial-governance-and-public-administration-performance-index
- Báo cáo PAPI 2024 — UNDP: https://www.undp.org/vietnam/publications/2024-provincial-governance-and-public-administration-performance-index-papi-report
- Trang dữ liệu PAPI: https://papi.org.vn/eng/papi-data/
- Số liệu KT-XH 63 tỉnh 2019–2023 — Tổng cục Thống kê (nguồn ghép tùy chọn): https://www.nso.gov.vn/en/default/2025/01/socio-economic-statistical-data-of-63-provinces-and-cities-2019-2023/

---
*Tài liệu này là bản tổng hợp giai đoạn Data Understanding. Các phát hiện sẽ được kiểm chứng lại trong
bước EDA (`docs/data/eda-findings.md`) và quá trình xử lý ghi tại `docs/data/processing-log.md`.*
