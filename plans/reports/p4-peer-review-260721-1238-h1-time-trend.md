# P4 peer review — H1 time trend

**Reviewer:** H2 owner (Lê Xuân Trí workstream)
**Reviewed file:** `app/pages/time_trend.py`
**Scope:** H1 data grain, controls, source/missing-data communication, and visual consistency. No H1 files were modified.

## Evidence checked

- H1 uses `analysis.trend` for pure aggregation and starts from `prov_year` /
  `national`; it does not read raw data or mutate data.
- Scale control uses `config.scale_config`; `dash_context` publishes the selected
  scale and year range.
- Charts use the shared `charts`/`layout` conventions; the diverging bar uses
  direct Plotly selection with a safe empty-selection fallback.
- Existing unit coverage is in `tests/test_trend.py`; no page-level AppTest was
  found for H1.

## Findings for the H1 owner

1. **Medium — wording conflicts with the 6-dimension mode.** The page header
   says the assessment is aggregated from eight domains
   (`app/pages/time_trend.py:22`), while the default control explicitly selects
   the six original dimensions. Make the introductory copy depend on the
   selected scale, or use neutral wording such as “các lĩnh vực PAPI”.
2. **Medium — “trung bình 63 tỉnh” can overstate coverage.** Several subtitles
   use that exact phrase (`app/pages/time_trend.py:115`, `:145`, `:185`, `:275`)
   although the calculation is a mean of available observations and source text
   acknowledges missing provinces. Display the available count by year/range or
   change the wording to “trung bình các tỉnh có dữ liệu”.
3. **Low — missing page-level smoke coverage.** `tests/test_trend.py` exercises
   pure helpers, but there is no AppTest for the default page, mode 6/8 switch,
   or empty selection on `h1_divbar`. Add an AppTest patterned after H2 before
   considering the H1 page fully verified.

## Conclusion

H1 has sound shared-component usage and its interactive selection is guarded;
the three findings concern accuracy and verification rather than an immediate
runtime blocker. They are handed to the H1 owner and are not silently changed
within the H2 branch.
