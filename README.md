# PAPI Dashboard

Đồ án cuối kỳ môn Trực quan hóa Dữ liệu (CSC10108), trực quan hóa Chỉ số Hiệu quả Quản trị và
Hành chính công cấp tỉnh (PAPI) của Việt Nam giai đoạn 2011–2024. Sản phẩm gồm dashboard Streamlit,
pipeline dữ liệu có thể tái lập và module AI human-in-the-loop: AI đề xuất code, người dùng xem/sửa/
phê duyệt, sau đó code mới được chạy tại máy.

## Trạng thái hiện tại

- Đã hoàn thiện pipeline dữ liệu, EDA, trang Tổng quan và trang Diễn biến theo thời gian.
- Ba trang So sánh tỉnh, Phân tích theo lĩnh vực và Động lực/phân nhóm vẫn là trang chờ.
- AI Assistant đã có luồng sinh code → duyệt → chạy local, bốn plugin phân tích và test offline.
- Báo cáo LaTeX mới ở mức khung ban đầu.
- Lần rà soát gần nhất: 17/07/2026, toàn bộ 45 test offline đạt.

Chi tiết và các khoảng trống đã xác minh: [Trạng thái dự án](docs/project-status.md).

## Chạy nhanh

Yêu cầu Python 3.11 trở lên. Từ thư mục gốc dự án:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
streamlit run app/main.py
```

Trên Windows PowerShell, kích hoạt môi trường bằng `.venv\Scripts\Activate.ps1`.

Dashboard không cần API key để xem các trang trực quan. Để dùng AI Assistant:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Sau đó điền `GROQ_API_KEY` vào file vừa tạo. Không commit file secrets.

## Dữ liệu

- Nguồn chính: PAPI, do UNDP Việt Nam, CECODES và RTA công bố tại [papi.org.vn](https://papi.org.vn/).
- Phạm vi: 63 tỉnh/thành, 14 năm (2011–2024), 8 lĩnh vực PAPI; D7–D8 chỉ có từ 2018.
- Bảng long đã xử lý có 6.094 dòng; panel tỉnh-năm có 882 dòng.
- Dữ liệu thiếu tại nguồn được giữ là thiếu, không nội suy hay bịa số.

Build lại dữ liệu:

```bash
python src/build_dataset.py
```

Lệnh này đọc `data/raw/`, ghi `data/processed/` và cập nhật
[`docs/data/processing-log.md`](docs/data/processing-log.md). Không chỉnh sửa dữ liệu raw.

## Kiểm thử

`requirements-dev.txt` bao gồm dependency runtime và `pytest` cho môi trường phát triển:

```bash
python -m pytest -q
```

Các test hiện tại tập trung vào AI API/executor, trạng thái AI Assistant và phân tích xu hướng.

## Tài liệu

Bắt đầu tại [docs/README.md](docs/README.md). Đây là chỉ mục phân biệt tài liệu nguồn sự thật, hướng
dẫn đang dùng và tài liệu lịch sử. Không dùng trực tiếp nội dung trong `docs/archive/` để quyết định
trạng thái hiện tại.

Các điểm vào chính:

- [Trạng thái dự án](docs/project-status.md)
- [Kiến trúc thực tế](docs/architecture.md)
- [Hướng dẫn cài đặt và phát triển](docs/guides/getting-started.md)
- [Roadmap còn lại](docs/roadmap.md)
- [Dữ liệu và EDA](docs/data/README.md)
- [AI human-in-the-loop](docs/ai/README.md)
- [Quy ước thiết kế](docs/guides/design-system.md)

## Cấu trúc chính

```text
app/                 Streamlit dashboard và AI Assistant
src/                 pipeline dữ liệu và hàm phân tích thuần
data/raw/            14 file Excel nguồn, chỉ đọc
data/processed/      các bảng đã xử lý và GeoJSON
notebooks/           data understanding, preprocessing, EDA
tests/               test offline
docs/                tài liệu dự án đang dùng và archive
report/              khung báo cáo LaTeX HCMUS
reports/figures/      biểu đồ EDA đã xuất
logs/                log JSONL của AI Assistant, không commit dữ liệu phiên
```

## Nhóm thực hiện

- 23120199 — Lê Xuân Trí
- 23120208 — Dương Tuấn Anh
- 23122038 — Nguyễn Trần Trung Kiên
- 23122045 — Lê Đức Phúc
