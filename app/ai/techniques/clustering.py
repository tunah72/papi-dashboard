"""Plugin: gom nhóm 63 tỉnh theo hồ sơ 8 lĩnh vực PAPI bằng KMeans."""
from ai.registry import register

register(
    key="clustering",
    label="Gom nhóm tỉnh theo hồ sơ lĩnh vực",
    description=(
        "Sử dụng thuật toán học máy (KMeans Clustering) để tự động phân "
        "nhóm 63 tỉnh thành dựa trên cấu trúc điểm của 8 lĩnh vực."
    ),
    user_prompt="Hãy gom nhóm 63 tỉnh thành thành 4 cụm dựa trên điểm của 8 lĩnh vực PAPI trong năm mới nhất, sau đó vẽ biểu đồ phân tán (scatter plot) so sánh giữa D4 (Kiểm soát tham nhũng) và D8 (Quản trị điện tử).",
    system_instruction=(
        "Sử dụng bảng `prov_year`. "
        "Không được tự bịa giá trị `region`. Nếu người dùng yêu cầu 'miền Nam', lọc `region` bằng đúng hai giá trị thật: `Đông Nam Bộ` và `Đồng bằng sông Cửu Long`. "
        "Nếu người dùng yêu cầu vùng khác, phải dùng đúng giá trị `region` có trong schema/dữ liệu. "
        "Nếu câu hỏi người dùng thay đổi số cụm (ví dụ k=3, 5 cụm, n_clusters=6) thì dùng số cụm đó; nếu không nêu thì dùng n_clusters=4. "
        "Nếu câu hỏi người dùng thay đổi trục scatter (ví dụ D1 vs D6) thì dùng đúng hai trục đó; nếu không nêu thì dùng D4 vs D8. "
        "Lọc về năm mới nhất có dữ liệu (max của cột year) và BẮT BUỘC gọi `.copy()` sau khi lọc. "
        "Chọn các cột đặc trưng: D1, D2, D3, D4, D5, D6, D7, D8. "
        "Bỏ các tỉnh có bất kỳ giá trị NaN nào trong các cột đó và tiếp tục gọi `.copy()` sau `dropna`. "
        "Sau khi lọc/dropna, nếu số dòng bằng 0 hoặc nhỏ hơn n_clusters thì KHÔNG chạy StandardScaler/KMeans; thay vào đó gán `result` là DataFrame có cột `ly_do` giải thích không đủ dữ liệu và gán `fig = None`. "
        "Lưu lại cột province_vi cho các hàng còn lại. "
        "Chuẩn hoá đặc trưng bằng StandardScaler (đã có sẵn trong sandbox, không cần import). "
        "Áp dụng KMeans với n_clusters theo câu hỏi người dùng hoặc mặc định 4, random_state=42 (đã có sẵn, không cần import). "
        "Gán nhãn cụm vào cột `cum` (0–3) bằng `.loc[:, 'cum'] = ...`, không dùng chained assignment. "
        "Gán `result` = DataFrame [province_vi, D1, D2, D3, D4, D5, D6, D7, D8, cum] "
        "sắp xếp theo cum rồi province_vi. "
        "Gán `fig` = scatter plot dùng plotly.express, "
        "trục x/y theo câu hỏi người dùng hoặc mặc định x là D4 (Kiểm soát tham nhũng), y là D8 (Quản trị điện tử), "
        "màu theo cột cum (dùng color_continuous_scale hoặc color_discrete_sequence), "
        "hover_data gồm province_vi, "
        "tiêu đề 'Gom nhóm 63 tỉnh theo hồ sơ PAPI — D4 vs D8 (năm mới nhất)', "
        "nhãn trục x='D4 Kiểm soát tham nhũng', trục y='D8 Quản trị điện tử'."
    )
)
