# Kiến trúc PAPI Dashboard

React + FastAPI là bề mặt chính. Streamlit trong `app/` là fallback đóng băng để trình diễn dự phòng;
capability mới chỉ được phát triển trên React/FastAPI.

## Sơ đồ tổng thể

```text
data/raw/*.xlsx
      │
      ▼
src/papi_lib.py + src/build_dataset.py
      │
      ├── data/processed/*
      └── docs/data/processing-log.md
               │
               ▼
src/data_loader.py + src/analysis/*
               │
               ▼
server/services.py + server/view_models.py
               │
               ▼
FastAPI /api/v1/*  ◄──── server/assistant.py ──── Groq
               │                    │
               ▼                    └── local executor + JSONL logs
React + TypeScript
frontend/src/pages/*
```

## Data và phân tích

- `src/papi_lib.py`: parser Excel, bảng tra cứu và chuẩn hóa tên tỉnh.
- `src/build_dataset.py`: chọn nguồn canonical, kiểm tra chất lượng và sinh processed artifacts.
- `src/data_loader.py`: đọc snapshot processed và chuẩn hóa GeoJSON trong bộ nhớ.
- `src/analysis/`: hàm thống kê cho diễn biến, tỉnh/vùng, quan hệ lĩnh vực và phân nhóm.

`data/raw/` là bất biến. App/API không đọc Excel trực tiếp và không sửa dữ liệu nguồn. Dữ liệu thiếu
được giữ là thiếu; `NaN`/`Infinity` được chuyển thành JSON `null` tại HTTP boundary.

Các artifact chính:

| Tên | Grain/vai trò |
|---|---|
| `fact_papi_long` | tỉnh × năm × lĩnh vực |
| `agg_province_year` | panel tỉnh × năm, dạng wide |
| `agg_national_year` | thống kê năm × lĩnh vực |
| `dim_province` | tỉnh, vùng và metadata |
| `dim_indicator` | D1–D8, tên, màu và thứ tự |
| `vietnam_provinces.geojson` | hình học bản đồ đã chuẩn hóa |

## FastAPI local

Entrypoint: `server.main:app`, bind mặc định `127.0.0.1:8000`.

Dashboard API:

- `GET /api/v1/metadata`
- `GET /api/v1/geojson`
- `GET /api/v1/overview`
- `GET /api/v1/trends`
- `GET /api/v1/provinces`
- `GET /api/v1/dimensions`
- `GET /api/v1/dynamics`

Assistant API:

- `POST /api/v1/assistant/messages`
- `POST /api/v1/assistant/executions`
- `GET /api/v1/assistant/logs`

`server/services.py` gọi lại `src/analysis/`, không sao chép công thức. `server/schemas.py` định nghĩa
response model cụ thể cho OpenAPI; `server/view_models.py` chuẩn hóa dữ liệu và metadata.

Query contract dùng `scale=six|eight`; snapshot dùng `year`; trends/dynamics dùng `from` và `to`;
provinces có `region`/`province`; dimensions có `x`/`y`. Giá trị thiếu được server resolve xác định từ
metadata, không để frontend tự đoán.

## React frontend

`frontend/src/router.tsx` khai báo năm route chính:

- `/overview`
- `/time-trend`
- `/provincial`
- `/dimension`
- `/dynamics`

`/ai-assistant` redirect đến `/overview?assistant=open`; `/dimensions` giữ alias tương thích cho
deep-link cũ. `AppShell` chứa sidebar và một `FloatingAssistant` dùng chung.

Mỗi page lấy view-model bằng TanStack Query, giữ filter cam kết trong URL và dựng đúng bốn chart card.
Plotly được bọc bởi các component Cartesian, Polar, Sankey và ProvinceMap. `ChartFocusDialog` dùng lại
cùng dữ liệu/chart state, không fetch hay tính lại chỉ vì phóng to.

## AI human-in-the-loop

```text
message
  ├── answer + source
  ├── clarification (tối đa một câu)
  └── proposal code read-only, pending approval
          ├── revision → proposal mới, bản cũ superseded
          └── approval proposal mới nhất
                    ▼
             local execution
                    ▼
        scalar/table/Plotly/stdout/error + log
```

Frontend không gửi code tùy ý tới execution API. Server lưu proposal, code chuẩn hóa và checksum;
execution chỉ nhận `sessionId`, `proposalId`, `approved: true` và từ chối proposal cũ bằng `409`.

Executor chạy process con, timeout 8 giây, giới hạn stdout, dùng bản sao DataFrame và kiểm AST/deny-list.
Đây là guard cho demo local, không phải public security sandbox. Table/result log được giới hạn 500
hàng nhưng luôn giữ shape, `totalRows` và `truncated`; API key và internal reasoning không được log.

## Streamlit fallback

`app/main.py` vẫn khai báo sáu trang Streamlit, bao gồm AI page cũ. `app/lib/data.py` là adapter cache
trên cùng processed snapshot; `app/ai/` giữ executor/provider legacy để fallback chạy độc lập.
Không thêm tính năng mới vào bề mặt này.

## Ranh giới phụ thuộc

- `src/` không phụ thuộc Streamlit hoặc React.
- React không truy cập filesystem, raw data, secrets hoặc công thức nghiệp vụ.
- FastAPI chỉ đọc processed snapshot trong luồng dashboard.
- Không so tổng 6 lĩnh vực với tổng 8 lĩnh vực qua mốc 2018.
- Tương quan, hồi quy và phân cụm không được diễn giải thành nhân quả hay xếp hạng chính thức.
- Secrets nằm ngoài Git; log phiên runtime không được commit.
