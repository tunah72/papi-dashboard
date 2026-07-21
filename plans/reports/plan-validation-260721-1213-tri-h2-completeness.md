---
date: 2026-07-21
plan: plans/260721-1203-hon-tt-h2-so-snh-tnh-ca-tr
tier: full
verdict: revise-before-implementation
---

# Validation plan H2 — độ bao phủ nhiệm vụ Trí

## Kết luận

Plan bao phủ đầy đủ phần kỹ thuật H2, plugin anomaly, kiểm thử, report và docs. Tuy nhiên **chưa đạt 100% nhiệm vụ được giao** vì thiếu hai bước P4 độc lập: review chéo một trang thành viên khác và merge H2 vào `main` sau review/check. Không nên bắt đầu implementation theo claim “hoàn tất toàn bộ task” trước khi hai bước này được bổ sung vào phase 5.

## Verification Results

- **Tier:** Full (5 phases)
- **Claims checked:** 38
- **Verified:** 36
- **Failed:** 2
- **Unverified:** 0

### Failures

1. **Review chéo thiếu.** `docs/archive/2026-06-initial-plans/work-assignment.md:134` yêu cầu Trí review một trang của thành viên khác. Toàn bộ phase file không có step nhận/review trang H1/H3/H4 hoặc lưu kết luận review.
2. **Merge vào main thiếu.** Cùng yêu cầu P4 bắt buộc merge; phase 5 chỉ kết thúc ở tạo PR. Plan không có gate review, merge, rồi xác nhận `main` chứa commit H2.

## Đã xác minh

- `app/pages/provincial.py`, `src/analysis/provincial.py`, `tests/test_provincial.py`, `app/ai/techniques/anomaly.py`, chart/filter/config/data helper đều tồn tại.
- Contract 6/8 lĩnh vực khớp `app/lib/config.py:49-54` và docs data/design.
- H1 có mẫu selection `st.plotly_chart(... on_select="rerun")` trong `app/pages/time_trend.py`, nên hướng click-to-drill H2 khả thi trên stack hiện tại.
- Plan không tham chiếu API/file không tồn tại ngoài các file sẽ tạo có chủ đích: `tests/test_provincial_page.py` và artifact tái tạo report.
- Không thấy contradiction giữa phase 1–4 về source data, module ownership, scope AI/log hay branch cũ.

## Whole-Plan Consistency Sweep

- Files reread: `plan.md` và 5 phase files.
- Decision deltas checked: scale 6/8, `provincial.py` thay `spatial.py`, map selection, z-score, plugin anomaly, report/docs gate.
- Reconciled stale references: 0.
- Unresolved contradictions: 0.
- Blocking omissions: review chéo và merge-to-main chưa có task.

## Sửa plan đề xuất

Thêm vào phase 5, sau PR:

1. Review một trang H1/H3/H4 theo DoD, ghi finding/approval trong PR hoặc report; không tự đánh dấu pass nếu chưa boot/test được.
2. Yêu cầu review H2; chỉ merge sau approvals và evidence phase 4.
3. Checkout/pull `main`, chạy `pytest -q` và smoke H2 tối thiểu một lần để xác nhận merge thực tế; cập nhật docs status theo commit main.

## Câu hỏi cần xác nhận

- Trí sẽ review trang nào trong H1/H3/H4 để đáp ứng review chéo?
