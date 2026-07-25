# Notebooks — trình bày workflow để kiểm chứng

Chạy **theo thứ tự**, mỗi notebook chạy được từ trên xuống (Kernel → Restart & Run All).
Mỗi notebook có các block **🔎 Nhận xét** bình luận kết quả.

| Thứ tự | Notebook | Nội dung |
|---|---|---|
| 1 | `data_understanding.ipynb` | Nguồn + cấu trúc 14 file raw (3 thời kỳ, 8 bẫy), mẫu thật |
| 2 | `preprocessing.ipynb` | Gộp + làm sạch → `data/processed/`, kiểm chứng QC từng bước |
| 3 | `eda.ipynb` | Phân tích khám phá + biểu đồ → 5 phát hiện chính |

Tài liệu chuẩn giải thích nguồn gốc, nội dung, pipeline, schema và kết quả EDA nằm tại
[`../docs/data/README.md`](../docs/data/README.md). Notebook là bề mặt trình bày và kiểm chứng, không
phải nguồn tài liệu song song.

## Chuẩn bị
```bash
python -m pip install -r ../requirements.txt
python -m pip install openpyxl==3.1.5 matplotlib==3.10.8 seaborn==0.13.2 jupyter==1.1.1
```
- `preprocessing.ipynb` đọc `../data/raw/` → ghi `../data/processed/` + `../docs/data/processing-log.md`.
- `eda.ipynb` chỉ đọc `../data/processed/` (không sửa dữ liệu).
- Logic dùng chung ở `../src/papi_lib.py`; notebook gọi lại đúng hàm đó (một nguồn sự thật).
