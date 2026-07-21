# Kế hoạch thực thi Floating AI Assistant

Ngày chốt phạm vi: 2026-07-21
Branch: `feat/basic-floating-ai-assistant`

## Mục tiêu và ranh giới

React có năm trang phân tích và một Trợ lý AI nổi dùng chung. Trợ lý nhận câu hỏi PAPI, trả lời kiến
thức hoặc đề xuất toàn bộ code Python kèm giải thích. Code luôn ở trạng thái **Chờ duyệt** và chỉ
proposal mới nhất được FastAPI xác nhận mới có thể chạy trong executor local.

Không xây vector database, embeddings, RAG server, intent router phức tạp hoặc AI page riêng. Không
thay đổi dữ liệu, báo cáo hay hành vi của Streamlit fallback. Executor chỉ phù hợp demo local, không
được mô tả là sandbox an toàn cho code không tin cậy trên server công khai.

## State machine

```text
hidden ── mở ──> open/default ⇄ open/maximized
  ^                   │
  └────── đóng ───────┘

idle → sending → answer | clarification | pending_approval
pending_approval → revising → pending_approval
pending_approval → approving → succeeded | failed
```

- Launcher là điểm mở lại duy nhất; không có thêm nút Thu nhỏ hoặc pill trùng chức năng.
- Đóng chỉ ẩn panel và giữ nguyên phiên. Phóng to/Khôi phục chỉ đổi kích thước bề mặt.
- `sessionStorage` giữ phiên khi đổi route hoặc refresh trong cùng tab.
- “Cuộc trò chuyện mới” là action duy nhất xóa state UI và tạo `sessionId` mới.
- Proposal mới đánh dấu proposal cũ là `superseded`; proposal cũ không còn action thực thi.

## HTTP contracts

### API AI — `POST /api/v1/assistant/messages`

Request gồm `sessionId?`, `message`, `context.route`, `context.search` và `revisionOf?`. Route chỉ nhận
năm route phân tích; query được whitelist và FastAPI tự resolve bằng dashboard service hiện hành.

Response luôn có `sessionId`, `turnId`, `kind` và đúng một payload:

- `answer`: `answer`, `source`;
- `clarification`: `question`;
- `proposal`: `proposalId`, `explanation`, `code`, `status="pending_approval"`, `source`.

Groq chỉ nhận knowledge context PAPI ngắn, schema dữ liệu thực tế, context đã canonicalize và lịch sử
cần thiết. API không trả internal reasoning. Một yêu cầu chỉ được hỏi tối đa một câu làm rõ.

### API Thực thi — `POST /api/v1/assistant/executions`

Request chỉ gồm `sessionId`, `proposalId`, `approved: true`; frontend không gửi code để chạy. Server
đọc code/hash đã lưu, xác nhận proposal là proposal mới nhất đang chờ duyệt rồi mới gọi executor.
Proposal không tồn tại, đã superseded hoặc không thuộc session trả `409`.

Response chuẩn hóa scalar, table, Plotly JSON, stdout, warning và error. Table tối đa 500 hàng, luôn có
`totalRows`, `truncated` và shape.

### API Logs — `GET /api/v1/assistant/logs?sessionId=...`

JSONL lưu các event: request, answer/clarification, proposal pending, proposal superseded, approval và
execution success/error. Event không chứa API key hoặc internal reasoning. Artifact kết quả dùng cùng
contract bounded như response để tránh log tăng không kiểm soát.

## UI contract

- Launcher có trên `/overview`, `/time-trend`, `/provincial`, `/dimension`, `/dynamics`.
- `/ai-assistant` redirect replace đến `/overview?assistant=open`; mở dialog không gọi AI.
- Desktop: launcher 56×56 px, cách phải/dưới 24 px; panel 420–460 px, tối đa 620–680 px.
- Mobile: cách mép 16 px cộng safe area; panel là bottom sheet 80–88dvh, header/composer sticky.
- Dialog không có backdrop tối, không làm đổi chart grid và click ngoài không xóa hoặc đóng state.
- `Esc` khi phóng to khôi phục kích thước; `Esc` tiếp theo hoặc nút Đóng trả focus về launcher. Focus
  ring và vùng bấm tối thiểu 44×44 px.
- Code read-only; revision gửi mô tả tự nhiên và nhận lại toàn bộ code mới.
- Chỉ proposal mới nhất hiển thị nút “Đồng ý và chạy local”.
- Câu trả lời kiến thức ghi `Nguồn: UNDP Việt Nam · CECODES · RTA`.

## Checklist implementation

- [x] Thêm ignore cho cache Vite và giữ worktree ngoài phạm vi sạch.
- [x] Thêm schema, orchestration, Groq provider, event store và executor guard cho FastAPI.
- [x] Thêm ba endpoint và TypeScript contract sinh từ OpenAPI.
- [x] Xóa AI page React, rút sidebar còn năm route và thêm redirect legacy.
- [x] Thêm launcher, dialog, pill, session store, conversation, proposal và result renderer.
- [x] Đồng bộ AGENTS, design source, architecture, parity, roadmap, status và hướng dẫn AI.
- [x] Chạy Python tests; frontend unit/lint/build; browser responsive/accessibility checks.
- [x] Gọi đúng một live Groq smoke cho câu “Chỉ số PAPI là gì?”, không chạy code AI.
- [x] Stage file rõ ràng, kiểm staged diff và tạo một local commit; không push/PR.

## Bằng chứng nghiệm thu

- Python: 112 test đạt.
- Frontend unit: 39 test đạt; ESLint và TypeScript/Vite build đạt.
- Browser: 43 Playwright test đạt trên desktop, tablet và mobile; kiểm tra launcher ở đủ năm route,
  deep-link cũ, keyboard, reduced motion, overflow và luồng proposal/revision/approval.
- OpenAPI: TypeScript schema sinh lại ổn định, không có drift.
- Live Groq: đúng một request kiến thức trả `kind="answer"`, có nguồn và chỉ ghi lifecycle
  `request_received` → `answer_returned`; không sinh hoặc chạy code.

## Acceptance criteria

1. Mở/đóng/phóng to trợ lý không phát request AI, không dịch layout và không mất hội thoại.
2. Câu hỏi kiến thức trả answer có nguồn; câu hỏi cần tính mới trả full code đang chờ duyệt.
3. Revision sinh proposal mới; endpoint execution từ chối proposal cũ bằng `409`.
4. Chỉ sau `approved: true` mới có event approval và execution/result/error.
5. Launcher/dialog dùng được ở desktop, tablet, mobile, keyboard-only, 200% zoom và reduced motion.
6. Năm route phân tích và 20 chart hiện tại không đổi nội dung hoặc phép tính.
7. Streamlit fallback và toàn bộ test legacy tiếp tục hoạt động.
