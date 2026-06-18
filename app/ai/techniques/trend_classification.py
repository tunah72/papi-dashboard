"""Plugin: phân loại lĩnh vực theo xu hướng cải thiện/ổn định/suy giảm qua các năm."""
from ai.registry import register

register(
    key="trend_classification",
    label="Phân loại lĩnh vực cải thiện/ổn định/suy giảm",
    description=(
        "Đánh giá mức độ thay đổi của toàn bộ 8 lĩnh vực PAPI "
        "để phân nhóm chúng thành 'cải thiện', 'suy giảm' hoặc 'ổn định'."
    ),
    user_prompt="Hãy phân loại xu hướng của toàn bộ 8 lĩnh vực PAPI (từ D1 đến D8) thành các nhóm: 'cải thiện', 'suy giảm', hoặc 'ổn định' dựa trên sự thay đổi điểm số giữa năm đầu và năm cuối.",
    system_instruction=(
        "Sử dụng bảng `national` (các cột: year, code, mean_score). "
        "Với mỗi lĩnh vực trong cột code (D1, D2, D3, D4, D5, D6, D7, D8), "
        "tính delta = mean_score ở năm lớn nhất − mean_score ở năm nhỏ nhất. "
        "Phân loại theo ngưỡng: delta > 0.03 → 'cải thiện'; delta < −0.03 → 'suy giảm'; "
        "còn lại → 'ổn định'. "
        "Ánh xạ tên đầy đủ: "
        "D1='Tham gia của người dân', D2='Công khai, minh bạch', "
        "D3='Trách nhiệm giải trình', D4='Kiểm soát tham nhũng', "
        "D5='Thủ tục hành chính công', D6='Cung ứng dịch vụ công', "
        "D7='Quản trị môi trường', D8='Quản trị điện tử'. "
        "Gán `result` = DataFrame với các cột [linh_vuc, delta, nhan] "
        "(linh_vuc là tên đầy đủ, delta là số thực, nhan là nhãn phân loại), "
        "sắp xếp theo delta giảm dần. "
        "Gán `fig` = biểu đồ thanh phân kỳ (diverging bar chart) dùng plotly.express, "
        "trục x là delta, trục y là linh_vuc, màu theo nhan "
        "('cải thiện'=xanh lá, 'ổn định'=xám, 'suy giảm'=đỏ), "
        "thêm đường kẻ dọc x=0, tiêu đề 'Xu hướng thay đổi điểm PAPI theo lĩnh vực'."
    )
)
