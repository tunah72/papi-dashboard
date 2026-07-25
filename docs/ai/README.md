# AI human-in-the-loop

## Trạng thái React + FastAPI

Trợ lý AI là floating panel dùng chung trên năm trang phân tích React. Sidebar không có route AI;
`/ai-assistant` chỉ là redirect tương thích đến `/overview?assistant=open`. Mở panel không gọi Groq và
không chạy code.

Ba HTTP API local:

| API | Trách nhiệm |
|---|---|
| `POST /api/v1/assistant/messages` | nhận câu hỏi/context, trả answer, clarification hoặc code proposal |
| `POST /api/v1/assistant/executions` | xác nhận và chạy đúng proposal mới nhất đã được người dùng duyệt |
| `GET /api/v1/assistant/logs` | truy xuất lifecycle event theo `sessionId` |

Groq dùng knowledge context ngắn từ `docs/data/README.md`, metadata D1–D8, schema dữ liệu và context đã
được FastAPI canonicalize. Hệ thống không dùng vector database, embeddings, RAG server hoặc indexing.

## Luồng sử dụng

1. Mở launcher ở góc dưới bên phải và nhập câu hỏi.
2. Câu hỏi kiến thức nhận answer trực tiếp kèm nguồn.
3. Phân tích cần tính mới nhận explanation và toàn bộ code ở trạng thái **Chờ duyệt**.
4. Nếu cần sửa, chọn **Yêu cầu chỉnh lại** và mô tả bằng ngôn ngữ tự nhiên; AI sinh toàn bộ code mới.
5. Chỉ proposal mới nhất có action **Đồng ý và chạy local**.
6. FastAPI xác nhận proposal/checksum, ghi approval rồi mới chạy local và trả table/figure/stdout/error.

Frontend không gửi code tùy ý vào API execution. Proposal cũ bị superseded và execution trả `409`.
Phiên UI được giữ trong `sessionStorage` khi đổi route hoặc refresh cùng tab.

## Knowledge và nguồn

Knowledge context gồm ý nghĩa PAPI, tên/định nghĩa D1–D8, 2011–2024, D7/D8 từ 2018, nguồn UNDP Việt
Nam · CECODES · RTA và giới hạn diễn giải. Không tự bịa số liệu, không so tổng 6 với tổng 8 lĩnh vực qua
2018, không diễn giải tương quan/hồi quy/phân cụm thành nhân quả hoặc xếp hạng chính thức.

## Executor và log

Executor chạy process con, timeout 8 giây, giới hạn stdout, dùng bản sao DataFrame và chỉ cấp pandas,
numpy, Plotly, scipy, sklearn cần thiết. FastAPI kiểm AST để chặn import còn lại, dunder và thao tác
file/process phổ biến. Đây là guard cho demo local, **không phải security sandbox công khai**.

JSONL ghi request/context, answer/clarification, pending/superseded proposal, approval và execution.
Result table/log giới hạn 500 hàng nhưng luôn có shape, `totalRows` và `truncated`; figure lưu Plotly JSON.
Không ghi API key hoặc internal reasoning.

## Kiểm thử

```bash
python3 -m pip install pytest==9.1.0 httpx==0.28.1
python3 -m pytest tests/test_assistant_http.py tests/test_executor.py -q
cd frontend
npm test -- --run
npm run lint
npm run build
```

Live Groq smoke chỉ thực hiện khi có chủ đích và dùng một câu kiến thức, không tự chạy code AI.
