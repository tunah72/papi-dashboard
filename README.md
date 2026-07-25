# PAPI Dashboard

Đồ án môn Trực quan hóa dữ liệu (CSC10108) xây dựng bảng điều khiển tương tác để khám phá Chỉ số
Hiệu quả Quản trị và Hành chính công cấp tỉnh (PAPI) của Việt Nam. Hệ thống sử dụng React cho giao
diện, FastAPI cho dịch vụ dữ liệu và Python cho xử lý, phân tích.

## Dữ liệu

- Nguồn: PAPI Việt Nam, UNDP Việt Nam, CECODES và RTA.
- Phạm vi: 63 tỉnh, thành phố trong 14 năm từ 2011 đến 2024; D7 và D8 có từ năm 2018.
- Dữ liệu sau xử lý: 6.094 điểm lĩnh vực và 882 tổ hợp tỉnh - năm.
- Quy trình, định nghĩa và giới hạn: [Tài liệu dữ liệu PAPI](docs/data/README.md).

## Tính năng

- Năm trang phân tích: Tổng quan, Diễn biến theo thời gian, Vùng và tỉnh, Mối quan hệ lĩnh vực,
  Thay đổi và phân nhóm.
- 20 biểu đồ tương tác kèm nhận xét, nguồn, đơn vị, số quan sát và chế độ phóng to.
- Bộ lọc và đối tượng được chọn được lưu trong URL để hỗ trợ tải lại và chia sẻ.
- Trợ lý AI theo cơ chế con người phê duyệt: hiển thị mã đề xuất, cho phép yêu cầu sửa và chỉ thực
  thi cục bộ sau khi người dùng đồng ý.

## Minh chứng

- [Minh chứng kết quả](https://drive.google.com/drive/folders/1EJoYErH-xulCpA_Sxmi9DxXkS5oMcfq9?usp=sharing)
- [Video demo](https://drive.google.com/file/d/1OIrdref8werXjB4FZUlOxp96OkxdJQKn/view?usp=sharing)
- [Mã nguồn GitHub](https://github.com/tunah72/papi-dashboard)

## Cấu trúc

```text
frontend/       Giao diện React và kiểm thử trình duyệt
server/         FastAPI, dịch vụ dữ liệu và Trợ lý AI
src/            Tiền xử lý dữ liệu và logic phân tích
tests/          Kiểm thử Python
data/           Dữ liệu gốc và dữ liệu đã xử lý
notebooks/      Khám phá và kiểm chứng dữ liệu
docs/           Tài liệu dữ liệu, thiết kế và kiến trúc
report/         Báo cáo LaTeX
slides/         Slide thuyết trình LaTeX
```

## Hướng dẫn chạy

Yêu cầu Python 3.11+, Node.js 20+ và npm.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cd frontend && npm ci && cd ..
```

Dashboard không cần API key. Để sử dụng Trợ lý AI, tạo cấu hình cục bộ:

```bash
cp .env.example .env
# Điền GROQ_API_KEY thật vào .env
```

FastAPI tự nạp file `.env`; biến môi trường đã khai báo trong hệ điều hành sẽ được ưu tiên.

Chạy FastAPI tại thư mục gốc:

```bash
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Chạy React trong terminal khác:

```bash
cd frontend
npm run dev
```
