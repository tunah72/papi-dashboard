---
title: "Hoàn tất H2 so sánh tỉnh của Trí"
description: "Hoàn tất vertical slice H2 trên main, không nhập lại nhánh feature/task/Tri cũ."
status: pending
priority: P1
effort: "2-3 ngày"
tags: [h2, provincial, streamlit, papi]
created: 2026-07-21
---

# Hoàn tất H2 so sánh tỉnh của Trí

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Hoàn thành và kiểm chứng H2 so sánh tỉnh/vùng trên `main`, đáp ứng phân công của Lê Xuân Trí mà không nhập conflict từ nhánh cũ.

**Architecture:** Giữ `src/analysis/provincial.py` là nguồn logic thuần duy nhất và `app/pages/provincial.py` là UI. Port behavior còn thiếu theo test trước; không thay đổi AI/log hoặc data pipeline. Chỉ sau validation mới tái tạo report và cập nhật docs trạng thái.

**Tech Stack:** Python, pandas, Plotly, Streamlit, pytest, Streamlit AppTest, LaTeX.

## Global Constraints

- Nền: `main` `697f5b2`; không merge/rebase/cherry-pick `feature/task/Tri` hay `90da9f9`.
- Chỉ đọc `data/processed/` qua `app/lib/data.py`; không sửa raw/pipeline.
- `total_papi_6dim`: 2011–2024; `total_papi`: từ 2018; không so chéo hai tổng.
- Chart phải dùng config/charts/layout, ghi nguồn PAPI và số tỉnh có dữ liệu; không nội suy/suy nguyên nhân.
- Không đổi public contract `app/lib/`, palette/theme, AI Assistant, logs hoặc executor.
- Docs trạng thái chỉ cập nhật sau evidence test/smoke có thật.

## Overview

Design: [H2 design](../../docs/h2-provincial-completion-design.md). Conflict trước plan: [baseline](../reports/conflict-260721-1200-new-h2-plan-baseline.md). Nhánh cũ chỉ để tham khảo behavior/test.

## Phases

| # | Phase | Status |
|---|---|---|
| 1 | [Contract và baseline](./phase-01-start.md) | Pending |
| 2 | [Logic H2 và unit test](./phase-02-h2-logic-v-unit-test.md) | Pending |
| 3 | [Trang H2 và drill-down](./phase-03-trang-h2-v-drill-down.md) | Pending |
| 4 | [Xác minh giao diện và plugin](./phase-04-xc-minh-giao-din-v-plugin.md) | Pending |
| 5 | [Báo cáo và trạng thái](./phase-05-bo-co-v-trng-thi.md) | Pending |

## Success Criteria

- [ ] H2 có map, top/bottom, boxplot vùng, outlier z-score, slopegraph, benchmark/radar và drill-down.
- [ ] Click map chọn tỉnh; selectbox fallback vẫn hoạt động.
- [ ] Unit test, AppTest, full pytest và smoke H2 6/8 lĩnh vực đều đạt trong venv dự án.
- [ ] Plugin anomaly giữ contract và có evidence offline/manual trung thực.
- [ ] Report H2 tái tạo được; docs current khớp code/test.
