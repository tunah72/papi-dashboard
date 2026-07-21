# Cài đặt và phát triển

## 1. Chuẩn bị môi trường

Yêu cầu Python 3.11 trở lên. Dependency runtime/demo được pin trong `requirements.txt`;
`requirements-dev.txt` kế thừa file này và bổ sung công cụ test cho môi trường phát triển.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Windows PowerShell dùng `.venv\Scripts\Activate.ps1`. Mọi lệnh sau đây chạy từ thư mục gốc dự án.

## 2. Chạy dashboard React + FastAPI

```bash
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
cd frontend && npm run dev
```

Mở `http://127.0.0.1:5173`. Năm trang dashboard không cần API key; floating assistant gọi Groq khi gửi
câu hỏi. Có thể đặt `GROQ_API_KEY` trong môi trường hoặc file local:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Điền `GROQ_API_KEY` trong file local này. Kiểm tra `git status` trước khi commit để chắc chắn secrets
không bị theo dõi.

## 3. Chạy test

`pytest` đã có trong `requirements-dev.txt`, vì vậy môi trường được cài theo bước 1 có thể chạy ngay:

```bash
python -m pytest -q
```

Chạy một nhóm test:

```bash
python -m pytest tests/test_trend.py -q
python -m pytest tests/test_api_ai.py tests/test_api_exec.py -q
python -m pytest tests/test_ai_assistant.py -q
```

Test offline không gọi Groq và không cần API key. Live AI test phải do người dùng chủ động thực hiện
vì có sử dụng quota/API bên ngoài.

## 3.1 Kiểm tra FastAPI local

Sau khi kích hoạt môi trường đã cài bằng `requirements-dev.txt`, dùng đúng interpreter của môi trường đó:

```bash
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
```

OpenAPI ở `http://127.0.0.1:8000/docs`. Không suy ra rằng một thư mục `.venv` có sẵn đã chứa dependency
mới; luôn cài lại theo bước 1 trước khi chạy API/test trong môi trường đó.

Streamlit fallback vẫn chạy độc lập bằng `streamlit run app/main.py`; không thêm capability mới vào đó.

## 4. Build lại dữ liệu

Chỉ chạy khi cần kiểm tra hoặc thay đổi pipeline:

```bash
python src/build_dataset.py
```

Đầu vào là 14 file trong `data/raw/`. Đầu ra nằm trong `data/processed/`; pipeline đồng thời ghi đè
`docs/data/processing-log.md`. Sau khi chạy, kiểm tra diff để bảo đảm không có thay đổi ngoài dự kiến.

Notebook chạy theo thứ tự:

1. `notebooks/data_understanding.ipynb`
2. `notebooks/preprocessing.ipynb`
3. `notebooks/eda.ipynb`

## 5. Luồng sửa đổi khuyến nghị

1. Đọc [trạng thái dự án](../project-status.md) và [roadmap](../roadmap.md).
2. Tạo branch theo một mục tiêu nhỏ, ví dụ `feat/provincial-analysis`.
3. Tách logic tính toán có thể test vào `src/analysis/`; page chỉ điều phối UI và biểu đồ.
4. Dùng `app/lib/config.py`, `data.py`, `filters.py`, `charts.py`, `layout.py` thay vì tạo convention mới.
5. Thêm test cùng thay đổi.
6. Chạy test, `git diff --check` và kiểm tra trực tiếp trang liên quan.
7. Cập nhật `docs/project-status.md` và `docs/roadmap.md` khi trạng thái thật thay đổi.

## 6. Quy tắc dữ liệu và AI

- Không sửa file trong `data/raw/`.
- Không điền dữ liệu thiếu bằng phỏng đoán; mọi cách xử lý phải có log.
- Không so tổng PAPI 6 lĩnh vực với tổng 8 lĩnh vực qua mốc 2018.
- Code AI phải hiển thị read-only; yêu cầu sửa bằng ngôn ngữ tự nhiên sinh full code mới và chỉ proposal
  mới nhất được chạy sau phê duyệt.
- Không đưa secrets hoặc log phiên chứa nội dung nhạy cảm lên Git.
- Không quảng bá executor hiện tại như sandbox an toàn cho người dùng không tin cậy.

## 7. Checklist trước khi bàn giao

```bash
git status --short
python -m pytest -q
git diff --check
```

Sau đó mở app, kiểm tra trang đã sửa, trạng thái thiếu dữ liệu và luồng lỗi. Nếu thay đổi AI, thực hiện
manual test trong [docs/ai/manual-test-cases.md](../ai/manual-test-cases.md) khi có API key và ghi lại
bằng chứng thay vì chỉ đánh dấu “đã test”.
