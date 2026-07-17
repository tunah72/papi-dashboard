# Kiến trúc thực tế của PAPI Dashboard

Tài liệu này mô tả code đang có trên `main` tại ngày 17/07/2026. Nội dung kế hoạch ban đầu đã được
chuyển vào `docs/archive/` và không còn là căn cứ để kết luận một tính năng đã hoàn thiện.

## Sơ đồ tổng thể

```text
14 file Excel trong data/raw/
          │
          ▼
src/papi_lib.py + src/build_dataset.py
          │
          ├── data/processed/*.parquet, *.csv
          └── docs/data/processing-log.md
                     │
                     ▼
          app/lib/data.py (cache và nạp dữ liệu)
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
 app/pages/*.py          app/pages/ai_assistant.py
          │                     │
          │             api_ai → người duyệt → api_exec
          │                               │
          └───────────────────────────────┴→ api_logs → logs/*.jsonl
```

## Data layer

`src/papi_lib.py` chứa bảng tra cứu, chuẩn hóa tên tỉnh và parser cho các cấu trúc Excel khác nhau.
`src/build_dataset.py` chọn một nguồn canonical cho từng năm, làm sạch, kiểm tra chất lượng rồi ghi
các bảng đã xử lý. `data/raw/` phải được xem là bất biến.

App không đọc Excel trực tiếp. `app/lib/data.py` chỉ nạp các file trong `data/processed/` và cache qua
`st.cache_data`. Các tên biến được dùng trong app và AI executor:

| Tên | Nguồn | Vai trò |
|---|---|---|
| `fact` | `fact_papi_long.parquet` | tỉnh × năm × lĩnh vực, dạng long |
| `prov_year` | `agg_province_year.parquet` | panel 63 tỉnh × 14 năm, dạng wide |
| `national` | `agg_national_year.parquet` | thống kê theo năm và lĩnh vực |
| `dim_prov` | `dim_province.csv` | tên tỉnh, vùng và metadata |
| `dim_ind` | `dim_indicator.csv` | tên/màu/thứ tự 8 lĩnh vực |
| `geojson` | `vietnam_provinces.geojson` | hình học dùng cho bản đồ |

Notebook là bản trình bày có thể chạy lại; pipeline trong `src/` là đường chạy kỹ thuật của dự án.
Không nên giả định hai bản luôn đồng bộ nếu chưa chạy cross-check trong notebook preprocessing.

## Dashboard layer

`app/main.py` khai báo sáu trang qua `st.navigation`:

- `overview.py`: KPI, bản đồ và xếp hạng; đã có nội dung thật.
- `time_trend.py`: phân tích xu hướng, COVID, heatmap và drill-down; đã có nội dung thật.
- `provincial.py`, `dimension.py`, `dynamics.py`: hiện chỉ publish context tối thiểu và hiển thị thông
  báo đang phát triển.
- `ai_assistant.py`: giao diện tạo, xem, sửa, duyệt, chạy và xem log code AI.

`app/lib/config.py` giữ đường dẫn, nhãn và token màu. `charts.py`, `filters.py`, `layout.py` là các
primitive dùng chung. Các phép tính riêng của H1 đã được tách sang `src/analysis/trend.py`; ba module
phân tích tương ứng H2–H4 chưa tồn tại.

## AI human-in-the-loop

“Ba API” trong đề bài hiện được triển khai dưới dạng ba module Python nội bộ, không phải ba HTTP
service độc lập:

1. `api_ai.py` ghép schema/context/prompt, gọi Groq và parse `code` + `explanation`.
2. `api_exec.py` chỉ chạy sau khi người dùng bấm **Phê duyệt và thực thi**.
3. `api_logs.py` ghi JSON Lines vào `logs/ai_sessions.jsonl`.

Registry tự discover năm lựa chọn: một ví dụ thống kê mô tả và bốn technique thật (`trend`,
`anomaly`, `insight`, `clustering`). Overview và H1 có nút chuyển chart context sang AI Assistant;
ba trang stub chưa có context phân tích thật.

### Giới hạn an toàn cần hiểu đúng

Executor chạy code trong process riêng, giới hạn 8 giây, cắt stdout ở 4.000 ký tự và loại một số
built-in/import nguy hiểm. DataFrame được sao chép trước khi đưa vào namespace thực thi. Đây là lớp
guard phù hợp cho demo local, **không phải security sandbox hoàn chỉnh** và không nên dùng để chạy
code từ người dùng không tin cậy trên máy chủ công khai.

GeoJSON hiện được truyền theo object gốc thay vì bản sao. Vì vậy tài liệu cũ nói “toàn bộ dữ liệu
read-only” là mạnh hơn đảm bảo thực tế. Việc harden executor được giữ trong roadmap.

## Luồng trạng thái AI

```text
Người dùng nhập yêu cầu
        │
        ▼
Groq sinh code + giải thích
        │
        ▼
Code hiển thị ở trạng thái Chờ duyệt
        │
        ├── người dùng sửa code
        ▼
Người dùng bấm Phê duyệt và thực thi
        │
        ▼
Process local chạy code → result/fig/stdout/error → log metadata
```

Hiện log được ghi khi thực thi hoặc reset. Code chỉ được sinh nhưng chưa chạy chưa tạo bản ghi; kết
quả bảng/biểu đồ đầy đủ cũng chưa được lưu, chỉ có metadata như shape, loại figure và stdout preview.
Đây là khoảng trống so với yêu cầu lưu toàn bộ quá trình.

## Ranh giới và quy tắc phụ thuộc

- `src/` không phụ thuộc Streamlit.
- Page đọc dữ liệu qua `app/lib/data.py`, không truy cập `data/raw/`.
- Biến đổi dữ liệu nguồn phải đi qua pipeline, có log và kiểm tra chất lượng.
- Không gọi `total_papi_6dim` là “Tổng PAPI”; đây là tổng sáu lĩnh vực gốc dùng để so sánh liên tục
  qua 2011–2024.
- Không so sánh tổng 6 lĩnh vực trước 2018 trực tiếp với tổng 8 lĩnh vực từ 2018.
- Secrets nằm ngoài Git trong `.streamlit/secrets.toml`.

## Các artifact khác

- `tests/`: 45 test offline tại lần rà soát 17/07/2026.
- `report/`: template và nội dung LaTeX ban đầu, chưa phải báo cáo hoàn chỉnh.
- `reports/figures/`: năm hình EDA sinh từ notebook.
- `logs/`: dữ liệu runtime local; `.gitkeep` được theo dõi, log phiên bị ignore.
