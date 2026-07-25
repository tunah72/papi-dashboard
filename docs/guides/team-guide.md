# Hướng dẫn làm việc nhóm

## Nguồn sự thật

- Kiến trúc: `docs/architecture.md`
- Dữ liệu: `docs/data/README.md`
- Thiết kế React: `docs/design/README.md`
- AI: `docs/ai/README.md`

## Bản đồ module

| Hướng | React page | FastAPI/analysis |
|---|---|---|
| Tổng quan | `Overview.tsx` | `server/services.py` |
| Diễn biến | `TimeTrend.tsx` | `src/analysis/trend.py` |
| Vùng và tỉnh | `Provincial.tsx` | `src/analysis/provincial.py` |
| Quan hệ lĩnh vực | `Dimension.tsx` | `src/analysis/dimensions.py` |
| Thay đổi và phân nhóm | `Dynamics.tsx` | `src/analysis/dynamics.py` |
| Trợ lý AI | `FloatingAssistant.tsx` | `server/assistant.py`, `server/executor.py` |

## Definition of Done

- Câu hỏi phân tích và grain dữ liệu rõ ràng.
- Số liệu được tính tại Python boundary và có test.
- UI có loading, empty, error, partial-data và metadata nguồn/đơn vị/`n`.
- Filter/selection cam kết được giữ trong URL.
- Biểu đồ có tooltip, nhãn không chồng, keyboard fallback và focus dialog.
- AI không chạy code trước phê duyệt; proposal cũ không thực thi được.
- Unit, lint, build và browser tests liên quan đều đạt.
- Tài liệu nguồn sự thật được cập nhật, không tạo file kế hoạch trùng lặp.

## Git và review

- Một branch cho một mục tiêu nhỏ; kiểm tra worktree trước khi sửa.
- Stage file rõ ràng, không dùng broad add khi worktree có thay đổi khác.
- Không commit secrets, logs, cache, `dist/` hoặc Playwright artifacts.
- PR/commit mô tả dữ liệu, hành vi trước/sau, test đã chạy và giới hạn còn lại.
- Reviewer đối chiếu code và runtime; test pass không tự chứng minh chất lượng giao diện.

## Ranh giới dữ liệu và AI

- Không sửa `data/raw/` và không điền dữ liệu thiếu bằng phỏng đoán.
- Không so tổng 6 lĩnh vực với tổng 8 lĩnh vực qua mốc 2018.
- Không diễn giải tương quan, hồi quy hoặc KMeans thành quan hệ nhân quả/xếp hạng chính thức.
- Secrets chỉ nằm local; lifecycle log không chứa API key hoặc internal reasoning.
- Executor là guard demo local, không phải sandbox công khai.
