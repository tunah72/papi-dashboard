---
date: 2026-07-21
scope: Đối chiếu toàn bộ docs hiện hành và archive yêu cầu H2 của Lê Xuân Trí
design: docs/h2-provincial-completion-design.md
verdict: incomplete
---

# Audit độ bao phủ docs của design H2

## Kết luận

Design hiện đạt khoảng **75%** yêu cầu tài liệu cho nhiệm vụ chính H2 của Trí. Nó đủ làm nền kiến trúc, nhưng **chưa đủ để coi là plan/design hoàn chỉnh 100%**. Không có lỗi mâu thuẫn nghiêm trọng với `main`; các thiếu sót là contract/acceptance criteria chưa được ghi rõ.

## Yêu cầu đã bao phủ

| Nguồn yêu cầu | Trạng thái | Bằng chứng trong design |
|---|---|---|
| `team-guide`: page + logic tách Streamlit + test + context AI | Đạt | Scope, ranh giới module, test và `dash_context`. |
| Phân công H2: choropleth, ranking, slopegraph, boxplot, drill | Đạt | Phần “Thiết kế H2” mục 3–6. |
| Data processed thật, không raw | Đạt | Chỉ dùng `prov_year`, không thay pipeline/raw data. |
| Dữ liệu thiếu không nội suy | Đạt một phần | Có lọc điểm thiếu/hiển thị số tỉnh và risk rỗng; chưa ghi rõ ghi chú dưới từng chart. |
| Design system: palette/layout/chart primitives | Đạt một phần | Giữ palette/theme/signature ngoài phạm vi; chưa ghi bắt buộc source, full label, `apply_owid`. |
| 6/8 lĩnh vực | Đạt một phần | Có control 6/8; chưa ghi contract năm bắt đầu và cấm so chéo hai tổng. |
| Báo cáo H2 và cập nhật trạng thái | Đạt | Scope + completion criteria yêu cầu report/docs sau khi có số tái tạo. |

## Thiếu để đạt 100%

1. **Câu hỏi phân tích H2 chính thức.** DoD yêu cầu câu hỏi rõ; design chỉ mô tả biểu đồ. Cần chốt tối thiểu: chênh lệch tỉnh/vùng, tỉnh outlier cùng năm, và tỉnh thay đổi mạnh giữa hai mốc.
2. **Contract thang đo và thời gian.** Ghi rõ `total_papi_6dim` dùng 2011–2024; `total_papi` chỉ 2018–2024; không đặt hai tổng cùng một so sánh/kết luận; luôn hiển thị nhãn đúng theo `design-system.md`.
3. **Acceptance criteria dữ liệu/visual.** Mỗi chart phải có nguồn PAPI, số tỉnh có dữ liệu, không nội suy, tên lĩnh vực đầy đủ, palette từ `config`, và `charts.apply_owid`/primitive tương đương.
4. **Contract phát hiện outlier.** Chốt một phương pháp. Design ghi z-score nhưng archive cũ từng mô tả standardized residual theo trend chung. Theo scope hiện tại nên chốt z-score trong cùng năm, `ddof=1`, ngưỡng `|z| > 2`, và nêu đây chỉ là mô tả không suy nguyên nhân.
5. **Plugin `anomaly.py` của Trí.** Design chưa có acceptance/test riêng cho plugin, dù phân công và `docs/ai/README.md` giao plugin này. Cần xác nhận prompt dùng đúng score người dùng yêu cầu, `.copy()` sau lọc, output `result`/`fig`, và manual/live test có phê duyệt của người dùng.
6. **Test matrix cụ thể.** Bổ sung cases: 6/8 lĩnh vực; năm có thiếu dữ liệu; vùng rỗng; một tỉnh không có đủ hai mốc; không có outlier; selection event rỗng và click hợp lệ; dữ liệu GeoJSON đã chuẩn hoá 63 ID.
7. **Bằng chứng completion.** Định nghĩa artifact phải nộp: pytest output, AppTest output, smoke test Streamlit, ảnh H2 6/8, số report tái tạo được, và review/PR evidence. Không cần tạo log AI mới trong scope H2, nhưng test plugin live phải theo manual test docs nếu dùng API.
8. **Discoverability và tài liệu stale.** `docs/README.md` chưa link design; `architecture.md`, `project-status.md`, `team-guide.md` vẫn mô tả H2 là stub do chúng phản ánh `main`. Chỉ cập nhật sau khi H2 merge/verify, nhưng design nên nêu rõ thứ tự này để tránh claim sớm.

## Không nên thêm vào design H2

- Lifecycle logging/artefact/checksum và deep-copy GeoJSON: đây là backlog AI liên nhóm trong roadmap, không phải điều kiện để merge H2.
- Merge/cherry-pick nhánh `feature/task/Tri` cũ.
- Thay pipeline dữ liệu hoặc palette/theme chung.

## Tài liệu đã đối chiếu

- `docs/README.md`, `project-status.md`, `roadmap.md`, `architecture.md`, `dashboard-handoff.md`.
- `docs/guides/team-guide.md`, `design-system.md`, `getting-started.md`.
- `docs/data/processed-dataset.md`, `processing-log.md`, `eda-findings.md`.
- `docs/ai/README.md`, `ai/manual-test-cases.md`.
- `docs/archive/2026-06-initial-plans/work-assignment.md`, `dashboard-plan.md`, `ai-integration-tasks.md` — chỉ dùng để truy nguyên yêu cầu đã giao, không dùng làm trạng thái hiện hành.

## Câu hỏi chưa giải quyết

- Có yêu cầu H2 phải giữ standardized-residual theo dashboard plan cũ, hay chốt z-score cùng năm như plugin/anomaly branch cũ?
- Plugin anomaly có cần hoàn tất live API test trong cùng PR H2 hay tách thành task AI riêng?
