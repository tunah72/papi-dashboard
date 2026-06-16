"""
build_dataset.py — Gộp 14 file PAPI raw (2011-2024) về dataset chuẩn dạng long (v0).
Logic dùng chung nằm ở src/papi_lib.py. File này lo orchestration + QC + xuất + ghi log.

Đầu vào : data/raw/*.xlsx  (BẤT KHẢ XÂM PHẠM — chỉ đọc)
Đầu ra  : data/processed/  + docs/data_processing_log.md
Chạy    : python3 src/build_dataset.py
"""
from __future__ import annotations
import os, datetime
import pandas as pd
from papi_lib import (ROOT, DIM_PROVINCE, DIM_INDICATOR, parse_era1, parse_transposed, year_sources)

OUT  = os.path.join(ROOT, "data", "processed")
DOCS = os.path.join(ROOT, "docs")
DIM_ORDER = [f"D{i}" for i in range(1, 9)]

LOG: list[str] = []
def log(msg: str = ""):
    print(msg); LOG.append(msg)


def parse_all():
    """Đọc & parse mọi năm theo nguồn canonical. Trả về DataFrame long thô (gồm cả TOTAL)."""
    log("## Bước 1 — Đọc & parse theo nguồn canonical mỗi năm\n")
    log("| Năm | Nguồn | #Tỉnh | #Trục | Có Tổng? | #Dòng |")
    log("|---|---|---|---|---|---|")
    records = []
    for year, era, path, sheet in year_sources():
        if era == "era1":
            recs, nprov, ndim = parse_era1(path, year); has_total = False
        else:
            recs, nprov, ndim, has_total = parse_transposed(path, year, sheet)
        records.extend(recs)
        src = os.path.basename(path) + ("" if era == "era1" else f" :: {sheet}")
        log(f"| {year} | {src[:42]} | {nprov} | {ndim} | {'có' if has_total else 'không'} | {len(recs)} |")
    return pd.DataFrame(records, columns=["province_id", "year", "code", "score"])


def clean(fact):
    """Làm sạch tối thiểu: điểm 0 → thiếu; tách TOTAL; ép kiểu; khử trùng."""
    zeros = fact[fact.score == 0]
    if len(zeros):
        z = zeros[zeros.code != "TOTAL"].merge(DIM_PROVINCE[["province_id","province_vi"]], on="province_id")
        log(f"\n_Loại {len(zeros)} ô điểm = 0 (không hợp lệ, coi là thiếu):_ "
            + ", ".join(f"{r.province_vi}-{r.year}-{r.code}" for _, r in z.iterrows()))
    fact = fact[fact.score != 0].copy()

    official_total = (fact[fact.code == "TOTAL"].rename(columns={"score":"total_official"}).drop(columns="code"))
    fact_dim = fact[fact.code != "TOTAL"].drop_duplicates(["province_id","year","code"]).copy()
    log("\n## Bước 2 — Làm sạch tối thiểu")
    log(f"- Tách TOTAL khỏi fact; fact chỉ giữ 8 trục.")
    log(f"- fact dạng long: {len(fact_dim)} dòng.")
    fact_dim["province_id"] = fact_dim["province_id"].astype("int16")
    fact_dim["year"] = fact_dim["year"].astype("int16")
    fact_dim["code"] = fact_dim["code"].astype("category")
    fact_dim["score"] = fact_dim["score"].astype("float32")
    fact_dim = fact_dim.sort_values(["year","province_id","code"]).reset_index(drop=True)
    return fact_dim, official_total


def aggregate(fact_dim, official_total):
    """Tạo agg_province_year (panel 63×14) và agg_national_year."""
    years = list(range(2011, 2025))
    full = pd.MultiIndex.from_product([DIM_PROVINCE.province_id, years], names=["province_id","year"])
    wide = (fact_dim.pivot_table(index=["province_id","year"], columns="code", values="score", observed=False)
            .reindex(full).reset_index())
    for c in DIM_ORDER:
        if c not in wide.columns: wide[c] = pd.NA
    wide["n_dims"] = wide[DIM_ORDER].notna().sum(axis=1)
    wide["expected_dims"] = wide.year.apply(lambda y: 6 if y <= 2017 else 8)
    wide["total_papi"] = wide[DIM_ORDER].sum(axis=1, min_count=1)
    wide.loc[wide.n_dims < wide.expected_dims, "total_papi"] = pd.NA   # thiếu trục → tổng NaN
    # total_papi_6dim: tổng D1-D6, so sánh liền mạch 2011-2024 (né mốc 6->8 trục năm 2018)
    DIM6 = [f"D{i}" for i in range(1, 7)]
    wide["total_papi_6dim"] = wide[DIM6].sum(axis=1, min_count=6)
    wide = wide.merge(official_total, on=["province_id","year"], how="left")
    wide["rank_year"] = wide.groupby("year")["total_papi"].rank(ascending=False, method="min").astype("Int64")
    wide["tier"] = wide.groupby("year")["total_papi"].transform(
        lambda s: pd.qcut(s, 4, labels=["Thấp nhất","TB thấp","TB cao","Cao nhất"]))
    wide = wide.merge(DIM_PROVINCE[["province_id","province_vi","region","region_id"]], on="province_id", how="left")
    wide = wide[["province_id","province_vi","region","region_id","year"]+DIM_ORDER+
                ["total_papi","total_papi_6dim","total_official","n_dims","rank_year","tier"]].sort_values(["year","province_id"])

    # báo cáo dữ liệu thiếu
    gaps = wide[wide.total_papi.isna()][["province_vi","year","n_dims"]]
    log(f"\n## Bước 2b — Dữ liệu thiếu tại nguồn (KHÔNG bịa số): {len(gaps)} tỉnh-năm")
    for _, r in gaps.iterrows():
        log(f"    - {r.province_vi} ({r.year}): {r.n_dims}/{'6' if r.year<=2017 else '8'} trục")

    nat = (fact_dim.groupby(["year","code"], observed=False)["score"]
           .agg(mean_score="mean", min_score="min", max_score="max", std_score="std").reset_index())
    return wide, nat


def quality_checks(fact_dim, wide):
    log("\n## Bước 3 — Kiểm tra chất lượng\n")
    ok_all = True
    def check(name, ok, detail=""):
        nonlocal ok_all; ok_all = ok_all and ok
        log(f"- [{'PASS' if ok else 'FAIL'}] {name}. {detail}")
    n = len(fact_dim)
    check("Tổng số dòng long ≥ 2000", n >= 2000, f"= {n}")
    ppy = fact_dim.groupby("year")["province_id"].nunique()
    check("Mỗi năm ≥60 tỉnh (gap = thiếu thật)", ppy.min() >= 60, f"min={ppy.min()}, max={ppy.max()}")
    check("Panel wide đủ 882 dòng (63×14)", len(wide) == 882, f"= {len(wide)}")
    dpy = fact_dim.groupby("year", observed=False)["code"].nunique()
    ok_d = all(dpy[y]==6 for y in range(2011,2018)) and all(dpy[y]==8 for y in range(2018,2025))
    check("6 trục ≤2017, 8 trục ≥2018", ok_d)
    check("Điểm trục trong (0,10]", (fact_dim.score.gt(0) & fact_dim.score.le(10)).all(),
          f"min={fact_dim.score.min():.2f}, max={fact_dim.score.max():.2f}")
    check("Tổng PAPI trong [10,80]", wide.total_papi.dropna().between(10,80).all(),
          f"min={wide.total_papi.min():.1f}, max={wide.total_papi.max():.1f}")
    check("Không trùng (tỉnh,năm,trục)", not fact_dim.duplicated(["province_id","year","code"]).any())
    cmp = wide.dropna(subset=["total_official"]).query("n_dims == 8")
    if len(cmp):
        diff = (cmp.total_papi - cmp.total_official).abs()
        check("Tổng tính = official (đủ 8 trục, lệch <0.01)", (diff < 0.01).all(),
              f"đối chiếu {len(cmp)} dòng, lệch max = {diff.max():.4f}")
    return ok_all


def export(fact_dim, wide, nat):
    os.makedirs(OUT, exist_ok=True); os.makedirs(DOCS, exist_ok=True)
    fact_dim.to_parquet(f"{OUT}/fact_papi_long.parquet", index=False)
    fact_dim.to_csv(f"{OUT}/fact_papi_long.csv", index=False)
    wide.to_parquet(f"{OUT}/agg_province_year.parquet", index=False)
    wide.to_csv(f"{OUT}/agg_province_year.csv", index=False)
    nat.to_parquet(f"{OUT}/agg_national_year.parquet", index=False)
    DIM_PROVINCE.to_csv(f"{OUT}/dim_province.csv", index=False)
    DIM_INDICATOR.to_csv(f"{OUT}/dim_indicator.csv", index=False)
    log(f"\n## Bước 4 — Xuất file (data/processed/)\n")
    log(f"- fact_papi_long: {len(fact_dim)} dòng | agg_province_year: {len(wide)} | agg_national_year: {len(nat)}")
    log(f"- dim_province: 63 | dim_indicator: 8")


def main():
    log("# Nhật ký xử lý dữ liệu PAPI (build_dataset.py)")
    log(f"_Chạy lúc: {datetime.datetime.now():%Y-%m-%d %H:%M}_\n")
    fact = parse_all()
    fact_dim, official_total = clean(fact)
    wide, nat = aggregate(fact_dim, official_total)
    ok = quality_checks(fact_dim, wide)
    export(fact_dim, wide, nat)
    with open(f"{DOCS}/data_processing_log.md", "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    print("\n" + ("✅ TẤT CẢ KIỂM TRA PASS" if ok else "⚠️ CÓ KIỂM TRA FAIL — xem log"))
    return ok


if __name__ == "__main__":
    main()
