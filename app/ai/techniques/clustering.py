"""Plugin: gom nhóm 63 tỉnh theo hồ sơ 8 lĩnh vực PAPI bằng KMeans."""
from ai.registry import register

register(
    key="clustering",
    label="Gom nhóm tỉnh theo hồ sơ lĩnh vực",
    description=(
        "KMeans (n=4) trên D1–D8 của năm mới nhất sau chuẩn hoá StandardScaler. "
        "Scatter D4 vs D8 tô màu theo cụm."
    ),
    default_request=(
        "Sử dụng bảng `prov_year`. "
        "Lọc về năm mới nhất có dữ liệu (max của cột year). "
        "Chọn các cột đặc trưng: D1, D2, D3, D4, D5, D6, D7, D8. "
        "Bỏ các tỉnh có bất kỳ giá trị NaN nào trong các cột đó. "
        "Lưu lại cột province_vi cho các hàng còn lại. "
        "Chuẩn hoá đặc trưng bằng StandardScaler (đã có sẵn trong sandbox, không cần import). "
        "Áp dụng KMeans với n_clusters=4, random_state=42 (đã có sẵn, không cần import). "
        "Gán nhãn cụm vào cột `cum` (0–3). "
        "Gán `result` = DataFrame [province_vi, D1, D2, D3, D4, D5, D6, D7, D8, cum] "
        "sắp xếp theo cum rồi province_vi. "
        "Gán `fig` = scatter plot dùng plotly.express, "
        "trục x là D4 (Kiểm soát tham nhũng), trục y là D8 (Quản trị điện tử), "
        "màu theo cột cum (dùng color_continuous_scale hoặc color_discrete_sequence), "
        "hover_data gồm province_vi, "
        "tiêu đề 'Gom nhóm 63 tỉnh theo hồ sơ PAPI — D4 vs D8 (năm mới nhất)', "
        "nhãn trục x='D4 Kiểm soát tham nhũng', trục y='D8 Quản trị điện tử'."
    ),
)
