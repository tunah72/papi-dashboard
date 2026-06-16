# Nhật ký xử lý dữ liệu PAPI (build_dataset.py)
_Chạy lúc: 2026-06-16 10:47_

## Bước 1 — Đọc & parse theo nguồn canonical mỗi năm

| Năm | Nguồn | #Tỉnh | #Trục | Có Tổng? | #Dòng |
|---|---|---|---|---|---|
| 2011 | PAPI-2011-Dữ-liệu-1.xlsx | 63 | 6 | không | 378 |
| 2012 | PAPI-2012-Dữ-liệu-1.xlsx | 63 | 6 | không | 378 |
| 2013 | PAPI-2013-Dữ-liệu-1.xlsx | 63 | 6 | không | 378 |
| 2014 | PAPI-2014-Dữ-liệu-1.xlsx | 63 | 6 | không | 366 |
| 2015 | PAPI-2015-Dữ-liệu-1.xlsx | 63 | 6 | không | 378 |
| 2016 | PAPI-2016-Dữ-liệu-1.xlsx | 63 | 6 | không | 378 |
| 2017 | PAPI-2017-Dữ-liệu-1.xlsx | 63 | 6 | không | 378 |
| 2018 | PAPI2018_ProvincialScores_ByIndicators_VIE | 63 | 8 | không | 500 |
| 2019 | 2019_PAPI_Provincial_indicators2019_VIE_EN | 63 | 8 | có | 567 |
| 2020 | 2020PAPI_ProvincialIndicators_BangChiTieuC | 63 | 8 | có | 567 |
| 2021 | 1.2021PAPI_ProvincialIndicators_BangChiTie | 63 | 8 | có | 540 |
| 2022 | 2022PAPI_ProvincialIndicators_BangChiTieuC | 63 | 8 | có | 567 |
| 2023 | 2023PAPI_ProvincialIndicators_BangChiTieuC | 63 | 8 | có | 549 |
| 2024 | 2024PAPI_ProvincialIndicators_BangChiTieuC | 63 | 8 | có | 567 |

_Loại 28 ô điểm = 0 (không hợp lệ, coi là thiếu):_ Bắc Giang-2022-D1, Bắc Giang-2022-D2, Bắc Ninh-2022-D2, Bắc Ninh-2022-D3, Bắc Giang-2022-D4, Bắc Ninh-2022-D4, Bắc Giang-2022-D5, Bắc Ninh-2022-D8, Vĩnh Phúc-2024-D1, Tiền Giang-2024-D1, Vĩnh Phúc-2024-D2, Tiền Giang-2024-D2, Vĩnh Phúc-2024-D3, Tiền Giang-2024-D3, Vĩnh Phúc-2024-D4, Tiền Giang-2024-D4, Vĩnh Phúc-2024-D5, Tiền Giang-2024-D5, Vĩnh Phúc-2024-D6, Tiền Giang-2024-D6, Vĩnh Phúc-2024-D7, Tiền Giang-2024-D7, Vĩnh Phúc-2024-D8, Tiền Giang-2024-D8

## Bước 2 — Làm sạch tối thiểu
- Tách TOTAL khỏi fact; fact chỉ giữ 8 trục.
- fact dạng long: 6094 dòng.

## Bước 2b — Dữ liệu thiếu tại nguồn (KHÔNG bịa số): 13 tỉnh-năm
    - Bắc Giang (2014): 0/6 trục
    - Đồng Tháp (2014): 0/6 trục
    - Quảng Ninh (2018): 6/8 trục
    - Đồng Tháp (2018): 6/8 trục
    - Bắc Giang (2021): 0/8 trục
    - Bắc Ninh (2021): 0/8 trục
    - Quảng Ninh (2021): 0/8 trục
    - Bắc Giang (2022): 4/8 trục
    - Bắc Ninh (2022): 4/8 trục
    - Quảng Ninh (2023): 0/8 trục
    - Bình Dương (2023): 0/8 trục
    - Vĩnh Phúc (2024): 0/8 trục
    - Tiền Giang (2024): 0/8 trục

## Bước 3 — Kiểm tra chất lượng

- [PASS] Tổng số dòng long ≥ 2000. = 6094
- [PASS] Mỗi năm ≥60 tỉnh (gap = thiếu thật). min=60, max=63
- [PASS] Panel wide đủ 882 dòng (63×14). = 882
- [PASS] 6 trục ≤2017, 8 trục ≥2018. 
- [PASS] Điểm trục trong (0,10]. min=1.93, max=8.46
- [PASS] Tổng PAPI trong [10,80]. min=31.7, max=48.8
- [PASS] Không trùng (tỉnh,năm,trục). 
- [PASS] Tổng tính = official (đủ 8 trục, lệch <0.01). đối chiếu 369 dòng, lệch max = 0.0000

## Bước 4 — Xuất file (data/processed/)

- fact_papi_long: 6094 dòng | agg_province_year: 882 | agg_national_year: 112
- dim_province: 63 | dim_indicator: 8