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

# Scale mode: chọn dùng 8 trục (chỉ 2018-2024) hay 6 trục liền mạch (2011-2024)
SCALE_8DIM = "8 trục (2018-2024)"
SCALE_6DIM = "6 trục liền mạch (2011-2024)"
SCALE_MODES = [SCALE_8DIM, SCALE_6DIM]


def scale_config(mode):
    """Trả về cấu hình ứng với scale mode: cột tổng, danh sách trục, năm bắt đầu."""
    if mode == SCALE_6DIM:
        return {"total_col": "total_papi_6dim", "dims": DIM6_CODES, "year_min": 2011}
    return {"total_col": "total_papi", "dims": DIM_CODES, "year_min": 2018}
