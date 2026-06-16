"""Plugin ví dụ (đợt nền): thống kê mô tả. Dùng để minh họa và kiểm thử luồng AI module.
Các thành viên thêm plugin riêng (trend_classification, anomaly, insight, clustering) theo mẫu này."""
from ai.registry import register

register(
    key="describe",
    label="Thống kê mô tả tổng điểm theo năm",
    description="Tính mean, std, min, max của total_papi cho từng năm.",
    default_request=(
        "Tính thống kê mô tả gồm mean, std, min, max của cột total_papi trong bảng prov_year "
        "theo từng năm. Gán bảng kết quả vào biến result."
    ),
)
