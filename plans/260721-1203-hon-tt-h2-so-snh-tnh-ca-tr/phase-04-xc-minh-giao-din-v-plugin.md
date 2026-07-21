---
phase: 4
title: "Xác minh giao diện và plugin"
status: complete_offline
priority: P1
effort: "4h"
dependencies: [3]
---

# Phase 4: Xác minh giao diện và plugin

## Overview

Thêm AppTest H2, chạy regression/smoke với dữ liệu thật, và kiểm tra plugin anomaly giữ đúng contract human-in-the-loop.

## Related Files

- Create: `tests/test_provincial_page.py`.
- Modify: `tests/test_provincial.py` nếu còn test edge case thiếu.
- Read: `app/ai/techniques/anomaly.py`, `docs/ai/manual-test-cases.md`.

## Implementation Steps

1. Tạo AppTest với data/GeoJSON fixture, không gọi Groq:
   ```python
   app = AppTest.from_file(str(ROOT / "app" / "pages" / "provincial.py"))
   app.run()
   assert not app.exception
   ```
2. Cover mode 6/8, vùng rỗng warning, year pair valid, selection event rỗng và selectbox drill fallback.
3. Run focus/full suite:
   ```bash
   python -m pytest tests/test_provincial.py tests/test_provincial_page.py -q
   python -m pytest -q
   ```
4. Run Streamlit và smoke H2 theo checklist: 6 lĩnh vực 2011/2024, 8 lĩnh vực 2018/2024, count dữ liệu thiếu, outlier/slope rỗng, map click.
5. Verify `anomaly.py` vẫn yêu cầu score theo user, `.copy()`, `result` và `fig`. Chỉ chạy manual live generate → review/edit → approve → execute nếu user cấp API key/quota; không commit key/log.
6. Commit `test(h2): cover provincial page interactions`.

## Success Criteria

- [ ] AppTest, full pytest và smoke evidence rõ pass/fail.
- [ ] Anomaly plugin có kết quả offline/manual trung thực; approval vẫn bắt buộc trước execution.
