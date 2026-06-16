"""Hằng số và cấu hình dùng chung cho toàn app. Không chứa logic tính toán."""
import sys
from pathlib import Path

# Đường dẫn (suy ra từ vị trí file: app/lib/config.py -> project root)
ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = ROOT / "data" / "processed"
GEOJSON = DATA_PROCESSED / "vietnam_provinces.geojson"

# Cho phép import các module trong src/ (papi_lib, analysis...) từ app
_SRC = ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

APP_TITLE = "PAPI Dashboard — Quản trị & Hành chính công cấp tỉnh"
YEAR_MIN, YEAR_MAX = 2011, 2024

DIM_CODES = [f"D{i}" for i in range(1, 9)]    # 8 trục
DIM6_CODES = [f"D{i}" for i in range(1, 7)]   # 6 trục gốc (liền mạch 2011-2024)

REGION_ORDER = [
    "Trung du và miền núi phía Bắc",
    "Đồng bằng sông Hồng",
    "Bắc Trung Bộ và Duyên hải miền Trung",
    "Tây Nguyên",
    "Đông Nam Bộ",
    "Đồng bằng sông Cửu Long",
]
TIER_ORDER = ["Thấp nhất", "TB thấp", "TB cao", "Cao nhất"]

# Scale mode: chọn dùng 6 lĩnh vực liền mạch (2011-2024) hay 8 lĩnh vực (chỉ 2018-2024)
SCALE_8DIM = "8 lĩnh vực (2018-2024)"
SCALE_6DIM = "6 lĩnh vực gốc (2011-2024)"
SCALE_MODES = [SCALE_6DIM, SCALE_8DIM]   # 6 lĩnh vực gốc là mặc định

# Tên hiển thị đầy đủ cho 8 lĩnh vực (không dùng mã D1..D8 hay viết tắt trên UI)
DIM_LABELS = {
    "D1": "Tham gia của người dân",
    "D2": "Công khai, minh bạch",
    "D3": "Trách nhiệm giải trình",
    "D4": "Kiểm soát tham nhũng",
    "D5": "Thủ tục hành chính công",
    "D6": "Cung ứng dịch vụ công",
    "D7": "Quản trị môi trường",
    "D8": "Quản trị điện tử",
}


def scale_config(mode):
    """Trả về cấu hình ứng với scale mode: cột tổng, danh sách trục, năm bắt đầu."""
    if mode == SCALE_6DIM or (mode is not None and "6" in str(mode)):
        return {"total_col": "total_papi_6dim", "dims": DIM6_CODES, "year_min": 2011}
    return {"total_col": "total_papi", "dims": DIM_CODES, "year_min": 2018}


# --------------------------------------------------------------------------------------
# Hệ màu dùng chung (phong cách OWID). Màu 8 trục lấy từ dim_indicator.csv; phần dưới
# bổ sung màu vùng, tier, và các thang liên tục/phân kỳ để mọi trang dùng nhất quán.
# --------------------------------------------------------------------------------------
ACCENT = "#B13507"   # vermillion — accent thương hiệu

# Màu 6 vùng kinh tế - xã hội (khớp REGION_ORDER)
REGION_COLORS = {
    "Trung du và miền núi phía Bắc":        "#6D4C9C",
    "Đồng bằng sông Hồng":                  "#4C6A9C",
    "Bắc Trung Bộ và Duyên hải miền Trung": "#2C8C99",
    "Tây Nguyên":                           "#578145",
    "Đông Nam Bộ":                          "#B13507",
    "Đồng bằng sông Cửu Long":              "#E0A23B",
}

# Màu 4 tier (thấp -> cao), một tông xanh đậm dần
TIER_COLORS = {
    "Thấp nhất": "#C9D5E5", "TB thấp": "#8FA8CB", "TB cao": "#4C6A9C", "Cao nhất": "#2A3F66",
}

# Thang liên tục cho choropleth/bar tổng (điểm thấp -> cao)
SEQ_SCALE = ["#EAF0F6", "#9DB4D2", "#4C6A9C", "#2A3F66"]
# Thang phân kỳ cho biến động (giảm <-> tăng), trung tính ở giữa
DIV_SCALE = ["#B13507", "#E7C9B8", "#F2EDE6", "#A9CBC9", "#2C8C99"]

# Hằng số style biểu đồ (charts.py dùng)
FONT_FAMILY = "Helvetica Neue, Helvetica, Arial, sans-serif"
GRID_COLOR = "#ECECEC"
AXIS_COLOR = "#9CA3AF"
TITLE_COLOR = "#1F2937"
SUBTITLE_COLOR = "#6B7280"
SOURCE_COLOR = "#9CA3AF"
SOURCE_DEFAULT = "Nguồn: PAPI — UNDP, CECODES, RTA"
