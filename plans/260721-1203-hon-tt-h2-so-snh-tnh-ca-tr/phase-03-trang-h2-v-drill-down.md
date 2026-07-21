---
phase: 3
title: "Trang H2 và drill-down"
status: complete
priority: P1
effort: "6h"
dependencies: [2]
---

# Phase 3: Trang H2 và drill-down

## Overview

Render H2 đầy đủ trên `main`: map chọn tỉnh, ranking top/bottom, boxplot vùng, outlier, slopegraph và benchmark/radar cùng một snapshot contract.

## Related Files

- Modify: `app/pages/provincial.py`.
- Read: `app/lib/charts.py`, `app/lib/filters.py`, `app/lib/layout.py`, `app/lib/config.py`.

## Implementation Steps

1. Thêm control mốc đầu/cuối; mốc cuối chỉ bao gồm năm lớn hơn mốc đầu, theo range hợp lệ của scale.
2. Render map và selection guard trực tiếp (không đổi `layout.chart`):
   ```python
   event = st.plotly_chart(fig_map, on_select="rerun", selection_mode="points", key="h2_map")
   points = getattr(getattr(event, "selection", None), "points", [])
   if points and points[0].get("location") in province_by_id:
       st.session_state["h2_selected_province"] = province_by_id[points[0]["location"]]
   ```
3. Selectbox là fallback; map/selectbox phải đồng bộ selected province cho ranking vùng, benchmark, radar và `dash_context`.
4. Dùng helper phase 2 cho top/bottom snapshot, outlier và slope pair. Với slope rỗng hoặc no outlier, render caption/insight thay vì index dòng đầu.
5. Mỗi chart dùng config/charts/layout, source PAPI, số tỉnh thật, tên lĩnh vực đầy đủ và note không nội suy/không suy nguyên nhân.
6. Smoke manual H2 ở 6 lĩnh vực 2011/2024 và 8 lĩnh vực 2018/2024; kiểm tra map click và select fallback.
7. Commit `feat(h2): complete provincial comparison page`.

## Success Criteria

- [ ] Map, ranking, boxplot, outlier, slopegraph, benchmark/radar và drill-down cùng hoạt động.
- [ ] Event rỗng/data rỗng không gây exception.
