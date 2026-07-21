---
phase: 2
title: "H2 logic và unit test"
status: pending
priority: P1
effort: "5h"
dependencies: [1]
---

# Phase 2: H2 logic và unit test

## Overview

Mở rộng `analysis.provincial` bằng helper thuần cho top/bottom, z-score và pair hai mốc. Không tạo `spatial.py` thứ hai.

## Related Files

- Modify: `src/analysis/provincial.py`, `tests/test_provincial.py`.
- Reference only: `feature/task/Tri:src/analysis/spatial.py`.

## Interfaces

```python
def top_bottom(snapshot: pd.DataFrame, total_col: str, n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]: ...
def zscore_outliers(snapshot: pd.DataFrame, total_col: str, threshold: float = 2.0) -> pd.DataFrame: ...
def slope_pair(prov_year: pd.DataFrame, year_start: int, year_end: int, total_col: str) -> pd.DataFrame: ...
```

## Implementation Steps

1. Viết test fail trước:
   ```python
   top, bottom = provincial.top_bottom(snapshot, "score", n=2)
   flagged = provincial.zscore_outliers(snapshot, "score")
   slope = provincial.slope_pair(panel, 2023, 2024, "score")
   assert set(top.index).isdisjoint(bottom.index)
   assert flagged["is_outlier"].dtype == bool
   assert set(slope.columns) == {"province_id", "province_vi", "year", "score", "delta"}
   ```
2. Run `python -m pytest tests/test_provincial.py -q`; expected fail because helper chưa tồn tại.
3. Implement tối thiểu: top/bottom không overlap; z-score trả `False` khi <2 quan sát/variance 0; slope chỉ giữ tỉnh đủ cả hai mốc và raise `ValueError` khi `year_start >= year_end`.
4. Thêm cases ngưỡng không dương, tie, NaN một mốc và input không mutate.
5. Run `python -m pytest tests/test_provincial.py -q` rồi `python -m pytest -q`.
6. Commit `feat(h2): add provincial comparison helpers`.

## Success Criteria

- [ ] Page có thể consume exact output của helper, không duplicate transform.
- [ ] Unit suite H2 và regression pass.
