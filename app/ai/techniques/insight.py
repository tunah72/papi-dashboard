"""Plugin: nhận xét tự động xu hướng và phân bố tỉnh cho một lĩnh vực PAPI cụ thể."""
from ai.registry import register

register(
    key="insight",
    label="Nhận xét tự động cho một lĩnh vực",
    description=(
        "Tự động trích xuất các thông tin quan trọng nhất (đỉnh, đáy, xu hướng chung) "
        "của một lĩnh vực cụ thể để đưa ra nhận xét tổng quan."
    ),
    user_prompt="Hãy phân tích và nhận xét các điểm nổi bật của lĩnh vực D4 (Kiểm soát tham nhũng).",
    system_instruction=(
        "Yêu cầu xử lý chia làm 2 phần:\n"
        "PHẦN 1 — xu hướng quốc gia: lọc bảng `national` theo code tương ứng với lĩnh vực người dùng yêu cầu (ví dụ: 'D4'). "
        "Xác định: năm đầu tiên, năm cuối cùng, mean_score tương ứng; "
        "năm có mean_score cao nhất (đỉnh) và thấp nhất (đáy). \n"
        "PHẦN 2 — phân bố tỉnh: lọc bảng `prov_year` về năm mới nhất có dữ liệu. "
        "Tỉnh có điểm của lĩnh vực đó cao nhất và thấp nhất (bỏ NaN). \n"
        "Gán `result` = DataFrame tổng hợp các chỉ số trên, "
        "cột [chi_so, gia_tri] với các hàng: "
        "'Năm đầu', 'Điểm năm đầu', 'Năm cuối', 'Điểm năm cuối', "
        "'Năm đỉnh', 'Điểm đỉnh', 'Năm đáy', 'Điểm đáy', "
        "'Tỉnh cao nhất (năm mới nhất)', 'Điểm tỉnh cao nhất', "
        "'Tỉnh thấp nhất (năm mới nhất)', 'Điểm tỉnh thấp nhất'. \n"
        "Gán `fig` = biểu đồ đường (line chart) dùng plotly.express "
        "vẽ mean_score theo year cho lĩnh vực đó từ bảng national, "
        "thêm vùng bóng min_score–max_score (dùng go.Scatter fill='tonexty'), "
        "nhãn trục x là 'Năm', trục y là 'Điểm trung bình'."
    )
)
