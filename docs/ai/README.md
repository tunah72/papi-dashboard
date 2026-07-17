# AI human-in-the-loop

## Mục tiêu

AI đóng vai trò đề xuất phương pháp, code và giải thích. Người dùng giữ quyền định hướng, sửa code,
phê duyệt và quyết định có thực thi hay không. Code được chạy local trên dữ liệu đã xử lý.

## Thành phần đang có

| Module | Trách nhiệm thực tế |
|---|---|
| `app/ai/api_ai.py` | tạo prompt, gọi Groq, parse và chuẩn hóa code |
| `app/ai/api_exec.py` | chạy code đã duyệt trong process local có guard/timeout |
| `app/ai/api_logs.py` | ghi và đọc JSONL |
| `app/ai/registry.py` | discover technique plugin |
| `app/pages/ai_assistant.py` | UI nhập yêu cầu, sửa, duyệt, chạy, xem kết quả/log |

Đây là ba API logic nội bộ theo đề bài, không phải HTTP endpoint.

## Technique hiện có

- Thống kê mô tả (`example_describe.py`) — plugin ví dụ/đường kiểm tra cơ bản.
- Phân loại xu hướng (`trend_classification.py`).
- Phát hiện tỉnh bất thường (`anomaly.py`).
- Nhận xét một lĩnh vực (`insight.py`).
- Gom nhóm tỉnh (`clustering.py`).

Plugin cung cấp prompt mặc định và hướng dẫn chuyên môn; LLM vẫn sinh code cụ thể. Vì vậy người dùng
phải đọc code và kiểm tra biến, filter, phương pháp trước khi phê duyệt.

## Luồng sử dụng

1. Chọn technique hoặc tự nhập yêu cầu.
2. Có thể chỉnh câu hỏi mẫu và thêm yêu cầu bổ sung.
3. Bấm **Sinh code (AI đề xuất)**.
4. Đọc giải thích và toàn bộ code ở trạng thái chờ duyệt.
5. Sửa code nếu cần.
6. Bấm **Phê duyệt và thực thi**.
7. Kiểm tra result/figure/error và nhật ký; diff thể hiện phần người dùng đã sửa.

Overview và H1 có thể seed yêu cầu từ một biểu đồ. Context gồm page/filter/data scope/chart được đưa
vào prompt. H2–H4 vẫn là stub nên chưa có context thật.

## Guard thực thi

Executor hiện:

- loại import và một số built-in nguy hiểm;
- chỉ cung cấp pandas/numpy/plotly/scipy/sklearn cần thiết;
- copy DataFrame trước khi chạy;
- chạy process riêng và dừng sau 8 giây;
- giới hạn stdout 4.000 ký tự;
- trả result, fig, stdout, warning và error về UI.

Các guard này giảm lỗi cho demo local nhưng không cô lập filesystem/process/network ở cấp hệ điều
hành. Không triển khai công khai để chạy code không tin cậy. Object GeoJSON hiện không được copy.

## Khoảng trống so với yêu cầu lưu trữ

Log hiện được tạo khi chạy code hoặc reset. Nếu người dùng sinh code rồi rời trang mà không chạy,
request/code/explanation đó không được lưu. Khi thực thi, log giữ code, context, stdout preview,
error, shape kết quả và loại figure; nó chưa lưu đầy đủ bảng kết quả hay artifact biểu đồ.

Roadmap ưu tiên chuyển log sang event lifecycle và lưu artifact có thể truy xuất. Cho đến khi hoàn
thiện, không mô tả hệ thống là đã “lưu toàn bộ yêu cầu, code, kết quả và giải thích”.

## Kiểm thử

Test offline:

```bash
python -m pytest tests/test_api_ai.py tests/test_api_exec.py tests/test_ai_assistant.py -q
```

Test này không gọi Groq. Nghiệm thu live dùng [manual-test-cases.md](manual-test-cases.md), cần API
key và phải do con người quyết định thực hiện vì có dùng quota bên ngoài.
