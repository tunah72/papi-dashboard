"""Plugin: phát hiện tỉnh có điểm PAPI bất thường (z-score) ở năm mới nhất."""
from ai.registry import register

register(
    key="anomaly",
    label="Phát hiện tỉnh bất thường",
    description=(
        "Tính z-score của total_papi (hoặc total_papi_6dim nếu total_papi thiếu) "
        "ở năm mới nhất; đánh dấu |z| > 2 là bất thường."
    ),
    default_request=(
        "Sử dụng bảng `prov_year` (các cột: province_vi, year, total_papi, total_papi_6dim). "
        "Lọc về năm mới nhất có dữ liệu (max của cột year). "
        "Chọn cột điểm: nếu cột total_papi không có giá trị NaN quá 10% thì dùng total_papi, "
        "ngược lại dùng total_papi_6dim. Gọi cột được chọn là `score`. "
        "Tính z-score = (score − mean(score)) / std(score) cho từng tỉnh. "
        "Đánh dấu cột `bat_thuong`: True nếu |z| > 2, False nếu không. "
        "Gán `result` = DataFrame chỉ gồm các tỉnh bất thường, "
        "các cột [province_vi, score, z_score, bat_thuong], sắp xếp z_score giảm dần tuyệt đối. "
        "Nếu không có tỉnh nào bất thường, `result` là DataFrame rỗng với các cột đó. "
        "Gán `fig` = biểu đồ thanh (bar chart) dùng plotly.express "
        "vẽ score cho TẤT CẢ tỉnh (không chỉ bất thường), "
        "trục x là province_vi, trục y là score, "
        "màu theo bat_thuong (True=đỏ cam, False=xanh dương nhạt), "
        "tiêu đề 'Điểm PAPI năm [năm mới nhất]: tỉnh bất thường (|z| > 2)', "
        "xoay nhãn trục x 90 độ."
    ),
)
