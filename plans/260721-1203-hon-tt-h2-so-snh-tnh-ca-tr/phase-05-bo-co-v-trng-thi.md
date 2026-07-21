---
phase: 5
title: "Báo cáo và trạng thái"
status: complete_pending_main_docs
priority: P2
effort: "4h"
dependencies: [4]
---

# Phase 5: Báo cáo và trạng thái

## Overview

Tái tạo số H2 từ processed data, cập nhật report và docs current sau khi có bằng chứng code/test thật.

## Related Files

- Modify: `report/content/`, `report/main.tex`, `docs/README.md`, `docs/project-status.md`, `docs/roadmap.md`, `docs/architecture.md`, `docs/guides/team-guide.md`.
- Create only if needed: test/script tái tạo bảng số H2 trong `tests/` hoặc `scripts/`.

## Implementation Steps

1. Tạo bảng/test tái tạo số 2024 bằng current helper và `total_col`; không copy số hard-code từ branch cũ.
2. Viết H2 report: câu hỏi, data scope, z-score, giới hạn missing data, source PAPI và số có thể tái tạo.
3. Build report:
   ```bash
   cd report
   pdflatex -interaction=nonstopmode -halt-on-error main.tex
   bibtex main
   pdflatex -interaction=nonstopmode -halt-on-error main.tex
   pdflatex -interaction=nonstopmode -halt-on-error main.tex
   ```
4. Chỉ khi phase 4 pass, update `docs/README.md` link design và thay claim H2 stub trong status/roadmap/architecture/team guide; không đổi archive/H3/H4/AI backlog.
5. Verify:
   ```bash
   git diff --check
   rg -n "H2.*Stub|Page/module chưa có|status: stub" docs
   ```
6. Commit `docs(h2): document provincial analysis evidence`; tạo PR ghi scope data, before/after, test/smoke evidence, và ghi rõ không merge branch cũ.

## Success Criteria

- [ ] PDF build sạch; số report có nguồn tái tạo.
- [ ] Docs current khớp code/test và không claim H2 hoàn tất sớm.
