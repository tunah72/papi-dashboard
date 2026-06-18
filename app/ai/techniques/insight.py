"""Plugin: nhận xét tự động xu hướng và phân bố tỉnh cho một lĩnh vực PAPI cụ thể."""
from ai.registry import register

register(
    key="insight",
    label="Nhận xét tự động cho một lĩnh vực",
    description=(
        "Trên bảng national nêu xu hướng mean_score (năm đầu, năm cuối, đỉnh, đáy). "
        "Trên prov_year năm mới nhất nêu tỉnh cao nhất và thấp nhất cho lĩnh vực đó."
    ),
    default_request=(
        "Phân tích lĩnh vực D4 (Kiểm soát tham nhũng). "
        "PHẦN 1 — xu hướng quốc gia: lọc bảng `national` theo code == 'D4'. "
        "Xác định: năm đầu tiên, năm cuối cùng, mean_score tương ứng; "
        "năm có mean_score cao nhất (đỉnh) và thấp nhất (đáy). "
        "PHẦN 2 — phân bố tỉnh: lọc bảng `prov_year` về năm mới nhất có dữ liệu. "
        "Tỉnh có điểm D4 cao nhất và tỉnh có điểm D4 thấp nhất (bỏ NaN). "
        "Gán `result` = DataFrame tổng hợp các chỉ số trên, "
        "cột [chi_so, gia_tri] với các hàng: "
        "'Năm đầu', 'Điểm năm đầu', 'Năm cuối', 'Điểm năm cuối', "
        "'Năm đỉnh', 'Điểm đỉnh', 'Năm đáy', 'Điểm đáy', "
        "'Tỉnh cao nhất (năm mới nhất)', 'Điểm tỉnh cao nhất', "
        "'Tỉnh thấp nhất (năm mới nhất)', 'Điểm tỉnh thấp nhất'. "
        "Gán `fig` = biểu đồ đường (line chart) dùng plotly.express "
        "vẽ mean_score theo year cho D4 từ bảng national, "
        "thêm vùng bóng min_score–max_score (dùng go.Scatter fill='tonexty'), "
        "tiêu đề 'D4 Kiểm soát tham nhũng — xu hướng trung bình quốc gia', "
        "nhãn trục x là 'Năm', trục y là 'Điểm trung bình'."
    ),
)
