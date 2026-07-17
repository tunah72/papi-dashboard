# Tài liệu dữ liệu và EDA

## Luồng dữ liệu

```text
data/raw/*.xlsx
    → src/papi_lib.py + src/build_dataset.py
    → data/processed/*
    → notebooks/eda.ipynb và app/lib/data.py
```

## Đọc theo nhu cầu

- Muốn hiểu PAPI và 14 file nguồn: [data-understanding.md](data-understanding.md).
- Muốn biết bảng processed có cột/grain gì: [processed-dataset.md](processed-dataset.md).
- Muốn kiểm tra các bước pipeline/QC gần nhất: [processing-log.md](processing-log.md).
- Muốn xem insight và câu hỏi phân tích ban đầu: [eda-findings.md](eda-findings.md).

## Quy tắc

- `data/raw/` chỉ đọc.
- Mọi chuyển đổi phải nằm trong pipeline/notebook, có thể tái lập và có ghi nhận.
- Không điền 13 tỉnh-năm thiếu tại nguồn bằng số giả hoặc nội suy ngầm.
- D1–D6 tồn tại từ 2011; D7–D8 từ 2018. Không so tổng 6 và tổng 8 lĩnh vực như cùng một thước đo.
- `processing-log.md` là output được sinh bởi pipeline, không phải file kế hoạch.

## Snapshot đã kiểm tra ngày 17/07/2026

| Artifact | Kích thước/đặc điểm |
|---|---|
| `fact_papi_long` | 6.094 dòng, grain tỉnh × năm × lĩnh vực |
| `agg_province_year` | 882 dòng, panel 63 × 14 |
| `agg_national_year` | 112 dòng, 14 × 8 |
| `dim_province` | 63 tỉnh |
| `dim_indicator` | 8 lĩnh vực |
| GeoJSON | 64 feature record, 63 ID duy nhất; ID 49 bị lặp |

Vấn đề GeoJSON được theo dõi trong [roadmap](../roadmap.md); chưa được tự động sửa trong lần tổ chức
tài liệu này.
