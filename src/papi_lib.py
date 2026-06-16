"""
papi_lib.py — Thư viện dùng chung cho pipeline PAPI (KHÔNG có side-effect khi import).
Chứa: bảng tra cứu, chuẩn hoá tên tỉnh, 2 parser, và kế hoạch nguồn canonical mỗi năm.
Được dùng lại bởi src/build_dataset.py và các notebook trong notebooks/.
"""
from __future__ import annotations
import os, re, unicodedata
import pandas as pd

# Thư mục data/raw (suy ra từ vị trí file, không phụ thuộc cwd)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(ROOT, "data", "raw")

# --------------------------------------------------------------------------------------
# 1) Bảng tra cứu tỉnh (63 tỉnh, mốc 2008-2024) + 6 vùng KT-XH
# --------------------------------------------------------------------------------------
REGIONS = {
    "Trung du và miền núi phía Bắc": ["Hà Giang","Cao Bằng","Bắc Kạn","Tuyên Quang","Lào Cai",
        "Yên Bái","Thái Nguyên","Lạng Sơn","Bắc Giang","Phú Thọ","Điện Biên","Lai Châu","Sơn La","Hòa Bình"],
    "Đồng bằng sông Hồng": ["Hà Nội","Vĩnh Phúc","Bắc Ninh","Quảng Ninh","Hải Dương","Hải Phòng",
        "Hưng Yên","Thái Bình","Hà Nam","Nam Định","Ninh Bình"],
    "Bắc Trung Bộ và Duyên hải miền Trung": ["Thanh Hóa","Nghệ An","Hà Tĩnh","Quảng Bình","Quảng Trị",
        "Thừa Thiên Huế","Đà Nẵng","Quảng Nam","Quảng Ngãi","Bình Định","Phú Yên","Khánh Hòa","Ninh Thuận","Bình Thuận"],
    "Tây Nguyên": ["Kon Tum","Gia Lai","Đắk Lắk","Đắk Nông","Lâm Đồng"],
    "Đông Nam Bộ": ["Bình Phước","Tây Ninh","Bình Dương","Đồng Nai","Bà Rịa - Vũng Tàu","Hồ Chí Minh"],
    "Đồng bằng sông Cửu Long": ["Long An","Tiền Giang","Bến Tre","Trà Vinh","Vĩnh Long","Đồng Tháp",
        "An Giang","Kiên Giang","Cần Thơ","Hậu Giang","Sóc Trăng","Bạc Liêu","Cà Mau"],
}

def norm(s) -> str:
    """Chuẩn hoá tên tỉnh để khớp: bỏ dấu thanh, thường hoá, đ→d, bỏ tiền tố/khoảng trắng/gạch nối."""
    if s is None: return ""
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")   # bỏ dấu thanh
    s = s.lower().strip().replace("đ", "d")                        # đ/Đ là ký tự riêng, NFD không tách
    for pre in ("tp.","tp ","thanh pho ","tinh ","province of ","city of "):
        if s.startswith(pre): s = s[len(pre):]
    return re.sub(r"[\s\-\.]", "", s)

def _build_lookup():
    rows, pid, n2id = [], 0, {}
    for rid, (region, provs) in enumerate(REGIONS.items(), start=1):
        for name in provs:
            pid += 1
            n2id[norm(name)] = pid
            if name == "Hồ Chí Minh":       n2id[norm("TP. Hồ Chí Minh")] = pid; n2id["hochiminhcity"] = pid
            if name == "Thừa Thiên Huế":    n2id["hue"] = pid
            if name == "Bà Rịa - Vũng Tàu": n2id[norm("Ba Ria-Vung Tau")] = pid
            name_en = "".join(c for c in unicodedata.normalize("NFD", name)
                              if unicodedata.category(c) != "Mn").replace("đ","d")
            rows.append(dict(province_id=pid, province_vi=name, province_en=name_en,
                             region=region, region_id=rid))
    return pd.DataFrame(rows), n2id

DIM_PROVINCE, NORM2ID = _build_lookup()
assert len(DIM_PROVINCE) == 63, f"Phải 63 tỉnh, đang {len(DIM_PROVINCE)}"

def to_pid(name):
    return NORM2ID.get(norm(name))

# --------------------------------------------------------------------------------------
# 2) Bảng tra cứu trục
# --------------------------------------------------------------------------------------
DIM_INDICATOR = pd.DataFrame([
    dict(code="D1", name_vi="Tham gia của người dân ở cấp cơ sở",      name_en="Participation",            short="Tham gia",         color="#1f77b4", sort=1, from_year=2011),
    dict(code="D2", name_vi="Công khai, minh bạch trong ra quyết định", name_en="Transparency",             short="Minh bạch",        color="#ff7f0e", sort=2, from_year=2011),
    dict(code="D3", name_vi="Trách nhiệm giải trình với người dân",     name_en="Vertical Accountability",  short="Giải trình",       color="#2ca02c", sort=3, from_year=2011),
    dict(code="D4", name_vi="Kiểm soát tham nhũng trong khu vực công",  name_en="Control of Corruption",    short="Chống tham nhũng", color="#d62728", sort=4, from_year=2011),
    dict(code="D5", name_vi="Thủ tục hành chính công",                  name_en="Public Admin. Procedures", short="Thủ tục HC",       color="#9467bd", sort=5, from_year=2011),
    dict(code="D6", name_vi="Cung ứng dịch vụ công",                    name_en="Public Service Delivery",  short="Dịch vụ công",     color="#8c564b", sort=6, from_year=2011),
    dict(code="D7", name_vi="Quản trị môi trường",                      name_en="Environmental Governance", short="Môi trường",       color="#17becf", sort=7, from_year=2018),
    dict(code="D8", name_vi="Quản trị điện tử",                         name_en="E-Governance",             short="QT điện tử",       color="#bcbd22", sort=8, from_year=2018),
])

# --------------------------------------------------------------------------------------
# 3) Parsers
# --------------------------------------------------------------------------------------
RE_DIM = re.compile(r"(?:Dimension|Chỉ số nội dung|nội dung)\s*([1-8])\s*:", re.IGNORECASE)

def parse_era1(path, year):
    """2011-2017: tỉnh theo HÀNG. Trả về (records, n_prov, n_dim_cols)."""
    xl = pd.ExcelFile(path)
    sheet = next(s for s in xl.sheet_names if "tổng hợp" in s)
    df = pd.read_excel(path, sheet_name=sheet, header=0)
    df.columns = [str(c).strip() for c in df.columns]
    prov_col = df.columns[0]
    dim_cols = {c: f"D{re.match(r'^[1-6]', c.strip()).group()}"
                for c in df.columns if re.match(r"^\s*[1-6]\s*:", c)}
    out, n_prov = [], 0
    for _, r in df.iterrows():
        pid = to_pid(r[prov_col])
        if pid is None: continue
        n_prov += 1
        for c, code in dim_cols.items():
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.notna(v): out.append((pid, year, code, float(v)))
    return out, n_prov, len(dim_cols)

def parse_transposed(path, year, sheet):
    """2018-2024: chỉ tiêu theo HÀNG, tỉnh theo CỘT. Trả về (records, n_prov, n_dims, has_total)."""
    df = pd.read_excel(path, sheet_name=sheet, header=None)
    # dò dòng tên tỉnh = dòng có nhiều tỉnh khớp nhất (quét 6 dòng đầu)
    best_row, best_map = None, {}
    for r in range(min(6, len(df))):
        m = {c: to_pid(df.iloc[r, c]) for c in range(df.shape[1])}
        m = {c: p for c, p in m.items() if p is not None}
        if len(m) > len(best_map): best_row, best_map = r, m
    if not best_map:
        raise RuntimeError(f"{sheet}: không tìm được dòng tên tỉnh")
    out, seen = [], set()
    for r in range(best_row + 1, df.shape[0]):
        lab = f"{df.iloc[r,0]} | {df.iloc[r,1] if df.shape[1]>1 else ''}"
        m = RE_DIM.search(lab)
        if m:
            code = f"D{m.group(1)}"
        else:
            l = lab.lower()
            is_total = ("unweighted papi score" in l) or \
                       ("papi tổng hợp" in l and "không có trọng số" in l
                        and not any(k in l for k in ["điểm thấp","điểm cao","sai số","ci low","ci high","standard error"]))
            code = "TOTAL" if is_total else None
        if code is None or code in seen: continue
        seen.add(code)
        for c, pid in best_map.items():
            v = pd.to_numeric(df.iloc[r, c], errors="coerce")
            if pd.notna(v): out.append((pid, year, code, float(v)))
    return out, len(best_map), len([c for c in seen if c.startswith("D")]), ("TOTAL" in seen)

# --------------------------------------------------------------------------------------
# 4) Kế hoạch nguồn canonical mỗi năm (file gốc từng năm — KHÔNG dùng sheet năm cũ của file 2024)
# --------------------------------------------------------------------------------------
def year_sources(raw_dir=RAW):
    plan = [(y, "era1", os.path.join(raw_dir, f"PAPI-{y}-Dữ-liệu-1.xlsx"), None) for y in range(2011, 2018)]
    plan += [
        (2018, "trans", os.path.join(raw_dir, "PAPI2018_ProvincialScores_ByIndicators_VIE.xlsx"), "ProvincialIndicators_VIE"),
        (2019, "trans", os.path.join(raw_dir, "2019_PAPI_Provincial_indicators2019_VIE_ENG.xlsx"), "2019PAPI_Indicators_VIE"),
        (2020, "trans", os.path.join(raw_dir, "2020PAPI_ProvincialIndicators_BangChiTieuCapTinh-1.xlsx"), "2020_VIE_ENG"),
        (2021, "trans", os.path.join(raw_dir, "1.2021PAPI_ProvincialIndicators_BangChiTieuCapTinh.xlsx"), "2021_VIE_ENG"),
        (2022, "trans", os.path.join(raw_dir, "2022PAPI_ProvincialIndicators_BangChiTieuCapTinh.xlsx"), "2022_VIE_ENG"),
        (2023, "trans", os.path.join(raw_dir, "2023PAPI_ProvincialIndicators_BangChiTieuCapTinh..xlsx"), "2023_VIE_ENG"),
        (2024, "trans", os.path.join(raw_dir, "2024PAPI_ProvincialIndicators_BangChiTieuCapTinh_34_TinhThanh.xlsx"), "2024_PAPI_VIE_ENG"),
    ]
    return plan
