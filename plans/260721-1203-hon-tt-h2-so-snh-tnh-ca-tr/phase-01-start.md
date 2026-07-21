---
phase: 1
title: "Contract và baseline"
status: pending
priority: P1
effort: "2h"
dependencies: []
---

# Phase 1: Contract và baseline

## Overview

Khóa contract H2 theo design và làm môi trường test chạy được trước khi thay đổi behavior.

## Related Files

- Read: `docs/h2-provincial-completion-design.md`, `docs/guides/design-system.md`, `docs/data/processed-dataset.md`, `docs/guides/team-guide.md`.
- Modify: `docs/h2-provincial-completion-design.md` chỉ khi phát hiện contract mơ hồ.

## Implementation Steps

1. Xác nhận branch/baseline:
   ```bash
   git branch --show-current
   git status --short
   git diff --check
   ```
   Expected: `feat/h2-provincial-completion`; không có sửa code chưa hiểu.
2. Cài và chạy test bằng venv dự án, không dùng interpreter global:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements-dev.txt
   python -m pytest -q
   ```
3. Ghi baseline pass/fail, sau đó xác nhận trong code/comment contract: snapshot drop `NaN`; scale 6/8 không so chéo; outlier là z-score cùng năm `ddof=1`, `abs(z)>2`.
4. Commit docs/plan riêng:
   ```bash
   git add docs/h2-provincial-completion-design.md plans/
   git commit -m "docs(h2): define completion contract"
   ```

## Success Criteria

- [ ] Có output baseline test hoặc blocker dependency cụ thể.
- [ ] Không còn mơ hồ về scale, missing-data, outlier hoặc nhánh cũ.
