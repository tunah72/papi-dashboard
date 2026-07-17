# Bàn giao Dashboard PAPI

## Chạy local

```bash
pip install -r requirements-dev.txt
streamlit run app/main.py
```

Không commit `.streamlit/secrets.toml` hoặc `logs/ai_sessions.jsonl`.

## Mạch trình bày

1. **Tổng quan** — chọn phạm vi 6 hoặc 8 lĩnh vực, đọc bản đồ và khoảng cách tỉnh dẫn đầu–xếp cuối.
2. **Hướng 1** — xu hướng quốc gia: lĩnh vực nào tăng/giảm qua thời gian.
3. **Hướng 2** — khoảng cách vùng và vị trí của một tỉnh so với benchmark phù hợp.
4. **Hướng 3** — các lĩnh vực có đi cùng nhau không; tương quan không phải quan hệ nhân quả.
5. **Hướng 4** — tỉnh nào thay đổi giữa hai mốc, và profile PAPI nào tương đồng.

## Demo AI human-in-the-loop

1. Mở một nút **Giải thích** dưới biểu đồ hoặc nhập câu hỏi ở AI Assistant.
2. AI chỉ **đề xuất** code và giải thích; trạng thái là *chờ duyệt*.
3. Sửa code hoặc giữ nguyên, sau đó bấm **Phê duyệt và thực thi**.
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
- Mở AI Assistant; kiểm tra code chỉ chạy sau nút phê duyệt.
- Không cần API key để xem Dashboard; AI sinh code live cần cấu hình secret cục bộ.
