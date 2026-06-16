# Phân công xây dựng dashboard

Nguyên tắc: mỗi thành viên sở hữu một vertical slice gồm các tệp riêng, không tệp nào bị hai người
cùng sửa, và chỉ phụ thuộc vào phần hạ tầng chung đã freeze. Tên gắn với hướng là đề xuất, có thể
hoán đổi.

## 1. Đợt nền (làm một lần, rồi freeze)

Phần dùng chung duy nhất, phải xong trước khi làm song song, do một người đảm nhận:

- Khởi tạo git và cây thư mục `app/`.
- Bổ sung cột `total_papi_6dim`; tạo tệp `vietnam_provinces.geojson`.
- Khung `app/main.py`; bốn module dùng chung `config.py`, `data.py`, `charts.py`, `filters.py`.
- Trang Overview `overview.py`.
- Khung AI module: `api_ai.py`, `api_exec.py`, `api_logs.py`, `ai_assistant.py`, và plugin registry.

## 2. Phân công vertical slice độc lập

Sau đợt nền, mỗi thành viên chỉ tạo và sửa các tệp của mình.

| Thành viên | Page | Analysis module | AI technique plugin |
|---|---|---|---|
| Dương Tuấn Anh | `app/pages/time_trend.py` | `src/analysis/trend.py` | `app/ai/techniques/trend_classification.py` |
| Lê Xuân Trí | `app/pages/provincial.py` | `src/analysis/spatial.py` | `app/ai/techniques/anomaly.py` |
| Nguyễn Trần Trung Kiên | `app/pages/dimension.py` | `src/analysis/dimension.py` | `app/ai/techniques/insight.py` |
| Lê Đức Phúc | `app/pages/dynamics.py` | `src/analysis/dynamics.py` | `app/ai/techniques/clustering.py` |

Page là giao diện một hướng; analysis module chứa các hàm thuần tách khỏi giao diện; technique plugin
là tệp tự chứa, tự đăng ký vào registry nên không ai phải sửa tệp dùng chung.

## 3. Contract và quy ước

- Contract: schema của `fact_papi_long` và `agg_province_year`, chữ ký hàm trong `app/lib/`, và
  interface chung của plugin. Chốt ở đợt nền, không đổi khi đang làm song song.
- Mỗi thành viên làm trên một git branch riêng. Không ai sửa tệp hạ tầng sau khi freeze.
- Cần một hàm vẽ mới thì đề xuất để người phụ trách đợt nền thêm vào `charts.py`, không tự sửa.
- Mọi page chỉ đọc dữ liệu đã xử lý, không truy cập dữ liệu raw.

## 4. Tính độc lập

Mỗi thành viên chạy và test page của mình ngay khi đợt nền xong, vì các vertical slice không gọi lẫn
nhau. Một người chậm tiến độ không chặn những người còn lại, và merge gần như không xung đột.
