# PAPI Dashboard — Trực quan hóa và phân tích dữ liệu quản trị cấp tỉnh

Đồ án cuối kỳ môn Trực quan hóa Dữ liệu (CSC10108). Dashboard Streamlit trực quan hóa Chỉ số PAPI
(Hiệu quả Quản trị và Hành chính công cấp tỉnh) tại 63 tỉnh giai đoạn 2011-2024, kèm một AI module
phân tích theo cơ chế con người phê duyệt (human-in-the-loop).

## 1. Yêu cầu

- Python 3.11 trở lên.
- Dữ liệu thô PAPI (14 tệp Excel) đặt sẵn trong `data/raw/`.

## 2. Cài đặt với venv

macOS / Linux:

```bash
cd final-project
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Các lần làm việc sau chỉ cần kích hoạt lại: `source .venv/bin/activate`.

## 3. Chuẩn bị dữ liệu

Bộ dữ liệu đã xử lý nằm sẵn trong `data/processed/`. Để build lại từ dữ liệu thô, chọn một trong hai
cách (cho kết quả y hệt nhau, đã được cross-check):

```bash
python src/build_dataset.py        # cách 1: chạy pipeline
# hoặc mở notebooks/preprocessing.ipynb và Run All  (cách 2: bản trình bày)
```

Đầu ra trong `data/processed/`: `fact_papi_long` (long), `agg_province_year` (wide panel 63x14),
`agg_national_year`, `dim_province`, `dim_indicator`, `vietnam_provinces.geojson`. Nhật ký xử lý ghi
tại `docs/data_processing_log.md`.

## 4. Chạy dashboard

```bash
streamlit run app/main.py
```

App mở ở trình duyệt với trang Tổng quan và bốn trang phân tích.

## 5. Cấu hình AI module

AI module dùng Groq. Lấy API key tại https://console.groq.com/keys rồi tạo tệp
`.streamlit/secrets.toml` (đã được `.gitignore` loại trừ, không commit):

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# rồi sửa GROQ_API_KEY bằng key thật
```

Không có key, các trang trực quan vẫn chạy bình thường; chỉ chức năng sinh code của trang AI Assistant
là cần key.

## 6. Notebooks

Ba notebook trình bày quy trình dữ liệu, chạy theo thứ tự:

```bash
jupyter notebook   # rồi mở notebooks/
```

1. `data_understanding.ipynb` — nguồn và cấu trúc dữ liệu thô.
2. `preprocessing.ipynb` — gộp và làm sạch, tự chứa logic, có ô cross-check với `src/`.
3. `eda.ipynb` — phân tích khám phá và biểu đồ.

## 7. Cấu trúc dự án

```
data/raw/            14 tệp Excel gốc (chỉ đọc)
data/processed/      dữ liệu đã xử lý + geojson
notebooks/           bản trình bày quy trình dữ liệu
src/                 bản kỹ thuật: papi_lib, build_dataset, analysis/
app/
  main.py            entry point, multipage navigation
  pages/             Overview + 4 trang phân tích + AI Assistant
  lib/               config, data, charts, filters (dùng chung)
  ai/                api_ai, api_exec, api_logs, registry, techniques/
docs/                tài liệu thiết kế, kế hoạch, kết quả
```

Kiến trúc chi tiết: `docs/architecture.md`.

## 8. Hướng dẫn cho thành viên phát triển

Mỗi thành viên sở hữu một vertical slice độc lập (xem `docs/work_assignment.md`): một trang trong
`app/pages/`, một analysis module trong `src/analysis/`, một AI technique plugin trong
`app/ai/techniques/`. Không sửa các tệp hạ tầng đã freeze trong `app/lib/`, `app/main.py`, khung
`app/ai/`.

Quy ước import trong app: `from lib import config, data, charts, filters`; `from ai import ...`;
`from analysis import <module>` (thư mục `src/` đã được thêm vào path qua `app/lib/config.py`).

Tài liệu định hướng: `docs/dashboard_plan.md` (bốn hướng và câu hỏi), `docs/foundation_checklist.md`
(tiến độ đợt nền), `docs/eda_findings.md` (phát hiện chính).

## 9. Nguồn dữ liệu

- PAPI: UNDP, CECODES, RTA. https://papi.org.vn
- Ranh giới hành chính: geoBoundaries (VNM ADM1).
