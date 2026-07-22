# Cài đặt và phát triển

## 1. Chuẩn bị

Yêu cầu Python 3.11+, Node.js 20+ và npm.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
cd frontend && npm ci && cd ..
```

Windows PowerShell kích hoạt môi trường bằng `.venv\Scripts\Activate.ps1`.

## 2. Chạy React + FastAPI

Terminal 1, từ thư mục gốc:

```bash
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd frontend
npm run dev
```

Mở `http://127.0.0.1:5173`. OpenAPI ở `http://127.0.0.1:8000/docs`.

Dashboard không cần API key. Floating AI Assistant chỉ gọi Groq khi người dùng gửi câu hỏi. Cấu hình
key local bằng:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Điền `GROQ_API_KEY` thật vào file vừa tạo. File này bị Git ignore; luôn kiểm tra `git status` trước commit.

Streamlit fallback có thể chạy độc lập bằng `streamlit run app/main.py`, nhưng không phải bề mặt phát
triển capability mới.

## 3. Kiểm thử

Python:

```bash
python -m pytest -q
```

Frontend:

```bash
cd frontend
npm test
npm run lint
npm run build
npx playwright test
```

Kiểm OpenAPI type khi FastAPI đang chạy:

```bash
cd frontend
npm run check:api
```

Các test mặc định không gọi Groq. Chỉ chạy live smoke khi chủ động chấp nhận dùng quota và không retry
tự động nếu provider lỗi.

## 4. Build lại dữ liệu

Chỉ chạy khi thay đổi hoặc kiểm chứng pipeline:

```bash
python src/build_dataset.py
```

Lệnh đọc 14 file trong `data/raw/`, ghi `data/processed/` và cập nhật
`docs/data/processing-log.md`. Kiểm tra diff ngay sau khi chạy; không chỉnh sửa raw data.

Notebook chạy theo thứ tự:

1. `notebooks/data_understanding.ipynb`
2. `notebooks/preprocessing.ipynb`
3. `notebooks/eda.ipynb`

## 5. Nguyên tắc sửa đổi

1. Đọc `docs/project-status.md`, đặc tả trang trong `docs/design/` và contract dữ liệu liên quan.
2. Giữ logic nghiệp vụ trong `src/analysis/` hoặc FastAPI; React chỉ render view-model và interaction.
3. Không sửa `data/raw/`, không bịa dữ liệu thiếu và không so tổng 6/8 lĩnh vực qua mốc 2018.
4. Thêm test cùng thay đổi; kiểm tra runtime ở desktop, tablet và mobile nếu sửa UI.
5. Cập nhật đúng tài liệu nguồn sự thật, không tạo thêm kế hoạch song song.
6. Không commit secrets, log phiên, cache, `dist/` hoặc test artifacts.

## 6. Checklist bàn giao

```bash
git status --short
python -m pytest -q
cd frontend && npm test && npm run lint && npm run build && npx playwright test
cd .. && git diff --check
```

Nếu thay đổi AI, chạy thêm manual cases trong `docs/ai/manual-test-cases.md`. Nếu thay đổi biểu đồ, kiểm
tooltip, nhãn, overflow, bảng fallback, focus dialog và reduced motion trên runtime thật.
