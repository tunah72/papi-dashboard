# Bàn giao Dashboard PAPI

## Chạy local

```bash
pip install -r requirements-dev.txt
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
cd frontend && npm run dev
```

Không commit `.streamlit/secrets.toml` hoặc `logs/ai_sessions.jsonl`.

## Mạch trình bày

1. **Tổng quan** — chọn phạm vi 6 hoặc 8 lĩnh vực, đọc bản đồ và khoảng cách tỉnh dẫn đầu–xếp cuối.
2. **Hướng 1** — xu hướng quốc gia: lĩnh vực nào tăng/giảm qua thời gian.
3. **Hướng 2** — khoảng cách vùng và vị trí của một tỉnh so với benchmark phù hợp.
4. **Hướng 3** — các lĩnh vực có đi cùng nhau không; tương quan không phải quan hệ nhân quả.
5. **Hướng 4** — tỉnh nào thay đổi giữa hai mốc, và profile PAPI nào tương đồng.

## Demo AI human-in-the-loop

1. Mở floating launcher ở góc dưới bên phải và nhập câu hỏi.
2. AI trả answer kiến thức hoặc **đề xuất** code và giải thích ở trạng thái *chờ duyệt*.
3. Nếu cần sửa, mô tả bằng ngôn ngữ tự nhiên để nhận full code mới; sau đó bấm **Đồng ý và chạy local**.
4. Code chạy local trên bản sao dữ liệu; xem bảng/biểu đồ kết quả và nhật ký.
5. Nhật ký phân biệt rõ code mới sinh chưa duyệt với lần chạy sau phê duyệt, kể cả log cũ.

## Bốn câu hỏi gợi ý cho vấn đáp

- Trong giai đoạn đang chọn, lĩnh vực nào tăng và giảm mạnh nhất?
- Điểm PAPI khác nhau thế nào giữa các vùng trong năm gần nhất?
- Công khai, minh bạch có liên hệ thế nào với sự tham gia của người dân?
- Tỉnh nào thay đổi nhiều nhất giữa hai mốc và thuộc profile PAPI nào?

## Kiểm tra trước khi trình bày

- Chạy `python -m pytest -q`.
- Mở app local và thử Overview cùng H1–H4 ở cả 6 và 8 lĩnh vực.
- Mở floating AI Assistant; kiểm tra code chỉ chạy sau nút phê duyệt và proposal cũ không chạy được.
- Không cần API key để xem Dashboard; AI sinh code live cần cấu hình secret cục bộ.
