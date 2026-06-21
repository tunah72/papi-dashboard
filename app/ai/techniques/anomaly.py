"""Plugin: phát hiện tỉnh có điểm PAPI bất thường (z-score) ở năm mới nhất."""
from ai.registry import register

register(
    key="anomaly",
    label="Phát hiện tỉnh bất thường",
    description=(
        "Phân tích dữ liệu để tìm ra các tỉnh có mức độ chênh lệch điểm PAPI "
        "bất thường so với trung bình cả nước trong năm mới nhất."
    ),
    user_prompt="Hãy tìm và vẽ biểu đồ các tỉnh có tổng điểm PAPI bất thường so với mặt bằng chung trong năm mới nhất.",
    system_instruction=(
        "Sử dụng bảng `prov_year` (các cột: province_vi, year, total_papi, total_papi_6dim, D1..D8). "
        "Nếu câu hỏi người dùng nêu rõ một lĩnh vực/chỉ tiêu cụ thể (ví dụ D4, D8, total_papi_6dim, total_papi), hãy dùng đúng cột đó làm `score`. "
        "Nếu người dùng không nêu chỉ tiêu cụ thể thì mới dùng logic mặc định bên dưới. "
        "Lọc về năm mới nhất có dữ liệu (max của cột year) và BẮT BUỘC gọi `.copy()` sau khi lọc, ví dụ `df = prov_year[prov_year['year'] == year_new].copy()`. "
        "Logic mặc định chọn cột điểm: nếu cột total_papi không có giá trị NaN quá 10% thì dùng total_papi, "
        "ngược lại dùng total_papi_6dim. Gọi cột được chọn là `score`. "
        "Tính z-score = (score − mean(score)) / std(score) cho từng tỉnh; khi gán cột mới phải dùng `.loc[:, 'z_score'] = ...`. "
        "Đánh dấu cột `bat_thuong`: True nếu |z| > 2, False nếu không; khi gán phải dùng `.loc[:, 'bat_thuong'] = ...`. "
        "Gán `result` = DataFrame chỉ gồm các tỉnh bất thường, "
        "các cột [province_vi, score, z_score, bat_thuong]. Sắp xếp `result` theo cột `z_score` giảm dần tuyệt đối bằng cách sử dụng `result.sort_values(by='z_score', key=abs, ascending=False)` (tuyệt đối không ép kiểu dữ liệu sang int). "
        "Nếu không có tỉnh nào bất thường, `result` là DataFrame rỗng với các cột đó. "
        "Gán `fig` = biểu đồ thanh (bar chart) dùng plotly.express "
        "vẽ score cho TẤT CẢ tỉnh (không chỉ bất thường), "
        "trục x là province_vi, trục y là score, "
        "màu theo bat_thuong (True=đỏ cam, False=xanh dương nhạt), "
        "tiêu đề 'Điểm PAPI năm [năm mới nhất]: tỉnh bất thường (|z| > 2)', "
        "xoay nhãn trục x 90 độ."
    )
)
