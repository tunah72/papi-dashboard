# Kiến trúc thực tế của PAPI Dashboard

Tài liệu này mô tả code Streamlit legacy dùng làm baseline migration tại `main` `697f5b2`. Khi có mâu
thuẫn, code/runtime/test hiện tại có authority cao hơn tài liệu này; ADR/parity matrix quyết định target
React + FastAPI, còn `docs/archive/` không là căn cứ để kết luận một tính năng đã hoàn thiện.

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

## FastAPI local (Phase 1)

`server/` là ranh giới HTTP local cho UI target. Server được chạy độc lập với fallback bằng:

```bash
python3 -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

`server.main:create_app()` chỉ cho phép CORS từ các origin dev localhost đã liệt kê và target bind là
`127.0.0.1`. Phase 1 có `GET /health` và bảy endpoint dashboard dưới `/api/v1`: `metadata`,
`geojson`, `overview`, `trends`, `provinces`, `dimensions`, `dynamics`. Không có HTTP API AI,
executor hay logs ở phase này; chúng vẫn thuộc Phase 5 để không làm mờ luồng phê duyệt của con người.

View-model trả JSON (không trả DataFrame hay Plotly Python object) với `meta.schemaVersion`, `source`,
`unit`, `n` là số quan sát hợp lệ của input chính, `caveats` và filter đã resolve. `rowCount` của từng
artifact chỉ là số hàng hiển thị, không thay cho `n`. Series trung bình theo năm/lĩnh vực có `contributorN`
ở từng điểm; benchmark/profile nêu rõ mẫu vùng và toàn quốc. `NaN`/`Infinity` được đổi thành `null`;
filter không hợp lệ trả `422` tiếng Việt. Các use case ở `server/services.py` gọi lại `src/analysis/`,
không sao chép công thức nghiệp vụ sang UI.

Contract query: `scale=six|eight`; route snapshot dùng `year`; `trends` và `dynamics` dùng `from`/`to`;
`provinces` nhận thêm `region`/`province`; `dimensions` nhận `x`/`y`. Giá trị optional được resolve
deterministic từ metadata (mốc mới nhất, hoặc toàn khoảng hợp lệ); `province` đơn lẻ tự suy ra vùng,
và `x`/`y` đơn lẻ tự chọn lĩnh vực còn lại. API trả availability để UI không tự đoán lựa chọn hợp lệ.

Mỗi endpoint có response model Pydantic cụ thể trong OpenAPI, gồm typed row/metric/artifact cho H1–H4;
không dùng envelope `data: dict[str, Any]`. H4 trả `fromScore`/`toScore`, không dùng key năm động.

`src/data_loader.py` là data layer thuần mới: đọc snapshot processed và normalise GeoJSON trong bộ nhớ.
`app/lib/data.py` chỉ còn adapter `st.cache_data` và re-export các helper để Streamlit fallback giữ nguyên
hành vi. GeoJSON trên file, raw và processed data không bị ghi.

OpenAPI luôn có tại `/openapi.json`. Khi Phase 2 tạo frontend, hook sinh type được chốt là:

```bash
npx openapi-typescript http://127.0.0.1:8000/openapi.json -o frontend/src/api/schema.ts
```

Lệnh trên chỉ là contract hook cho Phase 2, chưa tạo thư mục hay scaffold React trong Phase 1.

## Data layer

`src/papi_lib.py` chứa bảng tra cứu, chuẩn hóa tên tỉnh và parser cho các cấu trúc Excel khác nhau.
`src/build_dataset.py` chọn một nguồn canonical cho từng năm, làm sạch, kiểm tra chất lượng rồi ghi
các bảng đã xử lý. `data/raw/` phải được xem là bất biến.

App/API không đọc Excel trực tiếp. `src/data_loader.py` nạp các file trong `data/processed/`; fallback
cache kết quả qua `app/lib/data.py`. Các tên biến được dùng trong app và AI executor:

| Tên | Nguồn | Vai trò |
|---|---|---|
| `fact` | `fact_papi_long.parquet` | tỉnh × năm × lĩnh vực, dạng long |
| `prov_year` | `agg_province_year.parquet` | panel 63 tỉnh × 14 năm, dạng wide |
| `national` | `agg_national_year.parquet` | thống kê theo năm và lĩnh vực |
| `dim_prov` | `dim_province.csv` | tên tỉnh, vùng và metadata |
| `dim_ind` | `dim_indicator.csv` | tên/màu/thứ tự 8 lĩnh vực |
| `geojson` | `vietnam_provinces.geojson` | bản sao đã chuẩn hoá để vẽ bản đồ |

GeoJSON nguồn có hai feature của Bà Rịa–Vũng Tàu cùng ID `49` (đất liền và Côn Đảo). Khi nạp app,
`app/lib/data.py` gộp chúng thành MultiPolygon và rewind vòng theo quy ước Plotly/D3; source GeoJSON
trên đĩa vẫn giữ nguyên. Notebook là bản trình bày có thể chạy lại; pipeline trong `src/` là đường chạy kỹ thuật của dự án.
Không nên giả định hai bản luôn đồng bộ nếu chưa chạy cross-check trong notebook preprocessing.

## Dashboard layer

`app/main.py` khai báo sáu trang qua `st.navigation`:

- `overview.py`: chọn tổng 6/8 lĩnh vực, KPI, bản đồ và xếp hạng.
- `time_trend.py`: phân tích xu hướng, COVID, heatmap và drill-down.
- `provincial.py`: phân phối/ranking vùng, benchmark và profile tỉnh.
- `dimension.py`: correlation, scatter theo cặp lĩnh vực và phân tán.
- `dynamics.py`: thay đổi đầu-cuối và phân nhóm KMeans profile.
- `ai_assistant.py`: giao diện tạo, xem, sửa, duyệt, chạy và xem log code AI.

`app/lib/config.py` giữ đường dẫn, nhãn và token màu. `charts.py`, `filters.py`, `layout.py` là các
primitive dùng chung. Phép tính theo route nằm trong `src/analysis/`: `trend.py`, `provincial.py`,
`dimensions.py` và `dynamics.py` tương ứng H1–H4.

## AI human-in-the-loop

“Ba API” trong đề bài hiện được triển khai dưới dạng ba module Python nội bộ, không phải ba HTTP
service độc lập:

1. `api_ai.py` ghép schema/context/prompt, gọi Groq và parse `code` + `explanation`.
2. `api_exec.py` chỉ chạy sau khi người dùng bấm **Phê duyệt và thực thi**.
3. `api_logs.py` ghi JSON Lines vào `logs/ai_sessions.jsonl`.

Registry tự discover năm lựa chọn: một ví dụ thống kê mô tả và bốn technique thật (`trend`,
`anomaly`, `insight`, `clustering`). Các trang phân tích publish context để AI Assistant nhận câu hỏi
theo filter/chart đang xem.

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

Ngay khi AI sinh đề xuất, UI ghi event `generated_pending_approval` với request, code, explanation và
context; reset cũng được log. Sau phê duyệt, event `executed_after_approval` ghi `code_run`, stdout,
error, shape kết quả và loại figure (cùng metadata liên quan). Kết quả bảng/biểu đồ đầy đủ vẫn chưa được
lưu thành artifact truy xuất được, nên đây còn là khoảng trống so với yêu cầu lưu toàn bộ quá trình.

## Ranh giới và quy tắc phụ thuộc

- `src/` không phụ thuộc Streamlit.
- Page đọc dữ liệu qua `app/lib/data.py`, không truy cập `data/raw/`.
- Biến đổi dữ liệu nguồn phải đi qua pipeline, có log và kiểm tra chất lượng.
- Không gọi `total_papi_6dim` là “Tổng PAPI”; đây là tổng sáu lĩnh vực gốc dùng để so sánh liên tục
  qua 2011–2024.
- Không so sánh tổng 6 lĩnh vực trước 2018 trực tiếp với tổng 8 lĩnh vực từ 2018.
- Secrets nằm ngoài Git trong `.streamlit/secrets.toml`.

## Các artifact khác

- `tests/`: 62 test offline pass tại baseline `697f5b2`; migration hiện có 95 test Python pass, chạy bằng `python3 -m pytest -q`.
- `report/`: template và nội dung LaTeX ban đầu, chưa phải báo cáo hoàn chỉnh.
- `reports/figures/`: năm hình EDA sinh từ notebook.
- `logs/`: dữ liệu runtime local; `.gitkeep` được theo dõi, log phiên bị ignore.
