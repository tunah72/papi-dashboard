# PAPI Dashboard

Đồ án cuối kỳ môn Trực quan hóa Dữ liệu (CSC10108), trực quan hóa Chỉ số Hiệu quả Quản trị và
Hành chính công cấp tỉnh (PAPI) của Việt Nam giai đoạn 2011–2024.

Sản phẩm chính gồm năm trang phân tích React, FastAPI local và một Floating AI Assistant
human-in-the-loop. AI có thể trả lời kiến thức hoặc đề xuất code; code chỉ được chạy local sau khi
người dùng phê duyệt proposal mới nhất.

## Tính năng

- Năm trang: Tổng quan, Diễn biến theo thời gian, Vùng & tỉnh, Mối quan hệ lĩnh vực, Thay đổi & phân nhóm.
- 20 biểu đồ có insight, nguồn, đơn vị, cỡ mẫu, bảng truy cập được và chế độ phóng to.
- Filter/selection quan trọng được giữ trong URL để refresh và chia sẻ liên kết.
- Floating AI Assistant dùng chung, hỗ trợ answer, clarification, proposal, revision, approval và log.
- Pipeline dữ liệu tái lập từ 14 file Excel nguồn; không nội suy dữ liệu thiếu.
- Streamlit trong `app/` được giữ như fallback đóng băng, không phải giao diện phát triển chính.

## Chạy local

Yêu cầu Python 3.11+, Node.js 20+ và npm.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Terminal 1:

```bash
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd frontend
npm ci
npm run dev
```

Mở `http://127.0.0.1:5173`. Dashboard không cần API key; để gửi câu hỏi AI, sao chép
`.streamlit/secrets.toml.example` thành `.streamlit/secrets.toml` và điền `GROQ_API_KEY` local.

## Kiểm thử

```bash
python -m pytest -q
cd frontend
npm test
npm run lint
npm run build
npx playwright test
```

Live Groq smoke không nằm trong test mặc định vì sử dụng quota bên ngoài.

## Dữ liệu

- Nguồn: PAPI Việt Nam, UNDP Việt Nam, CECODES và RTA.
- Phạm vi: 63 tỉnh/thành, 2011–2024; D7–D8 có từ 2018.
- Bảng long đã xử lý: 6.094 dòng; panel tỉnh–năm: 882 dòng.
- Nguồn và quy trình xử lý: [docs/data/README.md](docs/data/README.md).

Chỉ chạy lại pipeline khi thật sự cần thay đổi dữ liệu:

```bash
python src/build_dataset.py
```

## Tài liệu

- [Chỉ mục tài liệu](docs/README.md)
- [Trạng thái dự án](docs/project-status.md)
- [Kiến trúc](docs/architecture.md)
- [Hướng dẫn cài đặt và phát triển](docs/guides/getting-started.md)
- [Đặc tả thiết kế](docs/design/README.md)
- [AI human-in-the-loop](docs/ai/README.md)
- [Hướng dẫn demo/vấn đáp](docs/dashboard-handoff.md)

## Cấu trúc

```text
frontend/       React + TypeScript và browser tests
server/         FastAPI, view-model và orchestration AI
src/            pipeline dữ liệu và logic phân tích thuần
app/            Streamlit legacy fallback
tests/          Python tests
data/           dữ liệu raw/processed
notebooks/      data understanding, preprocessing và EDA
docs/           tài liệu nguồn sự thật và thiết kế
report/         báo cáo LaTeX
slides/         slide Beamer
logs/           lifecycle log local của AI
```

## Nhóm thực hiện

- 23120199 — Lê Xuân Trí
- 23120208 — Dương Tuấn Anh
- 23122038 — Nguyễn Trần Trung Kiên
- 23122045 — Lê Đức Phúc
