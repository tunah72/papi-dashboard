# Bàn giao Dashboard PAPI

## Chạy local

```bash
python -m pip install -r requirements-dev.txt
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
cd frontend && npm ci && npm run dev
```

Không commit `.streamlit/secrets.toml` hoặc `logs/ai_sessions.jsonl`.

## Mạch trình bày

1. **Tổng quan** — chọn phạm vi 6 hoặc 8 lĩnh vực, đọc bản đồ và khoảng cách tỉnh dẫn đầu–xếp cuối.
2. **Diễn biến theo thời gian** — xu hướng quốc gia, nhịp vùng, thứ hạng vùng và thay đổi lĩnh vực.
3. **Vùng & tỉnh** — phân phối vùng và vị trí một tỉnh so với benchmark phù hợp.
4. **Mối quan hệ lĩnh vực** — các lĩnh vực có đi cùng nhau không; tương quan không phải nhân quả.
5. **Thay đổi & phân nhóm** — tỉnh nào thay đổi giữa hai mốc và profile PAPI nào tương đồng.

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
- Chạy `npm test`, `npm run lint`, `npm run build` và `npx playwright test` trong `frontend/`.
- Mở app local và thử đủ năm route ở cả phạm vi 6 và 8 lĩnh vực.
- Phóng to ít nhất một chart mỗi trang; kiểm tooltip, nhãn, nguồn, `n`, đóng bằng `Esc` và focus return.
- Mở floating AI Assistant; kiểm tra code chỉ chạy sau nút phê duyệt và proposal cũ không chạy được.
- Không cần API key để xem Dashboard; AI sinh code live cần cấu hình secret cục bộ.
