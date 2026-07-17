# Dataset đã xử lý — PAPI (v0)

> Sản phẩm của `src/build_dataset.py` (gộp 14 file raw 2011–2024). Nhật ký xử lý đầy đủ:
> `docs/data/processing-log.md`. Nền tảng dữ liệu thô: `docs/data/data-understanding.md`.
> **Mọi kiểm tra chất lượng hiện có của pipeline đều PASS.** Tổng tính khớp 100% tổng official
> (369 dòng, lệch 0.0000). Pipeline chưa kiểm tra tính duy nhất của feature GeoJSON.

## 1. Bộ file (data/processed/)

| File | Dạng | #Dòng | Dùng cho |
|---|---|---|---|
| `fact_papi_long.parquet` (+csv) | long | 6.094 | GỐC — mọi biểu đồ tidy (line, heatmap, radar) |
| `agg_province_year.parquet` (+csv) | wide panel | 882 | Bản đồ, KPI, bảng xếp hạng |
| `agg_national_year.parquet` | long | 112 | Đường xu hướng cả nước |
| `dim_province.csv` | tra cứu | 63 | Tỉnh → vùng |
| `dim_indicator.csv` | tra cứu | 8 | Trục → tên/màu/thang |
| `vietnam_provinces.geojson` | geojson | 64 feature | Choropleth (join theo `province_id`) |

## 2. Schema từng bảng

### `fact_papi_long` — bảng gốc (grain: tỉnh × năm × trục)
| Cột | Kiểu | Ví dụ | Mô tả |
|---|---|---|---|
| province_id | int16 | 1 | Khoá nối (1–63) |
| year | int16 | 2011 | 2011–2024 |
| code | category | D1 | D1…D8 |
| score | float32 | 4.88 | Điểm trục, thang 1–10 |

Mẫu thật:
```
 province_id  year code    score
           1  2011   D1  4.876205
           1  2011   D2  4.829181
           1  2011   D3  5.007073
           1  2011   D4  5.220708
```

### `agg_province_year` — wide panel đầy đủ 63×14
Cột: `province_id, province_vi, region, region_id, year, D1…D8, total_papi, total_papi_6dim, total_official, n_dims, rank_year, tier`.
- `total_papi` = tổng các trục có ở năm đó (6 trục cho ≤2017, 8 trục cho ≥2018; NaN nếu thiếu trục)
- `total_papi_6dim` = tổng D1–D6, **so sánh liền mạch 2011–2024** (né mốc 6→8 trục năm 2018)
- `total_official` = tổng lấy thẳng từ file (2018+, để đối chiếu)
- `rank_year` = hạng trong năm · `tier` = nhóm tứ phân vị (Cao nhất / TB cao / TB thấp / Thấp nhất)

Mẫu thật (top 3 năm 2024):
```
province_vi   region                year   D1    D4    D8   total_papi  rank_year  tier
Quảng Ninh    Đồng bằng sông Hồng   2024  5.87  7.99  3.94  47.82       1          Cao nhất
Tây Ninh      Đông Nam Bộ           2024  5.37  8.20  3.88  47.35       2          Cao nhất
Bình Thuận    BTB & DH miền Trung   2024  5.63  7.71  3.66  47.13       3          Cao nhất
```

### `agg_national_year` — xu hướng cả nước (grain: năm × trục)
Cột: `year, code, mean_score, min_score, max_score, std_score`.

### `dim_province` / `dim_indicator`
- `dim_province`: province_id, province_vi, province_en, region, region_id (6 vùng KT-XH)
- `dim_indicator`: code, name_vi, name_en, short, color, sort, from_year (D7/D8 from_year=2018)

## 3. Cách dùng trong Streamlit
```python
import streamlit as st, pandas as pd

@st.cache_data
def load():
    b="data/processed"
    return dict(
        long=pd.read_parquet(f"{b}/fact_papi_long.parquet"),
        prov_year=pd.read_parquet(f"{b}/agg_province_year.parquet"),
        national=pd.read_parquet(f"{b}/agg_national_year.parquet"),
        dim_prov=pd.read_csv(f"{b}/dim_province.csv"),
        dim_ind=pd.read_csv(f"{b}/dim_indicator.csv"),
    )
D = load()
D["prov_year"].query("year == 2024").nsmallest(10, "rank_year")   # top 10 tỉnh 2024
```

## 4. Quyết định xử lý (tóm tắt — chi tiết ở log)
1. Nguồn canonical: **file gốc từng năm** (file 2024 tổng hợp đã tổ chức lại theo 34 tỉnh → sheet năm cũ rỗng).
2. Parse 2 nhánh: 2011–2017 (tỉnh-hàng) / 2018–2024 (tỉnh-cột); trục nhận theo **số 1–8**, không theo chữ.
3. Chỉ lấy bản **Unweighted**.
4. Chuẩn hoá tên tỉnh (xử lý dấu, "Đ→D", "TP." …) → `province_id`.
5. Điểm = 0 trên thang 1–10 → coi là **thiếu** (28 ô, đã ghi log).
6. `total_papi` = NaN khi thiếu trục (không báo cáo tổng sai).

## 5. Hạn chế đã biết (nêu trong báo cáo)
- **13 tỉnh-năm thiếu tại nguồn** (882 ô, ~1,5%): vd Quảng Ninh 2021/2023, Bình Dương 2023,
  Bắc Giang/Bắc Ninh 2021–2022, Vĩnh Phúc/Tiền Giang 2024. Là gap thật trong dữ liệu PAPI — **không bịa**.
- **2024:** Vĩnh Phúc & Tiền Giang bị zero-hoá do file 2024 tổ chức theo 34 tỉnh mới (hai tỉnh này bị sáp nhập).
- **v0 chỉ ở cấp 8 trục** — chưa có trục thành phần (sẽ thêm nếu EDA cần).
- **Dữ liệu chủ quan** (cảm nhận của dân) + **cấp tỉnh tổng hợp** → không phân tích được khác biệt nam/nữ, dân tộc.
- **GeoJSON có 64 feature record nhưng 63 ID duy nhất; `province_id=49` lặp hai lần.** Cần xác minh
  đây là geometry tách mảnh hợp lệ hay bản ghi trùng trước khi sửa và bổ sung QC tương ứng.

## 6. Đối chiếu ràng buộc đề
| Yêu cầu | Kết quả |
|---|---|
| ≥2000 dòng | ✅ 6.094 (long) |
| ≥7 biến độc lập | ✅ ~12 cột |
| >50% Việt Nam | ✅ 100% |
| Nguồn minh bạch | ✅ UNDP+CECODES+RTA |
| Ghi rõ bước xử lý | ✅ `docs/data/processing-log.md` |

## 7. Tái lập
```bash
python3 src/build_dataset.py     # đọc data/raw/ → ghi data/processed/ + docs/data/processing-log.md
```
`data/raw/` không bị chỉnh sửa. Chạy lại cho kết quả y hệt (deterministic).
