"""Plugin ví dụ (đợt nền): thống kê mô tả. Dùng để minh họa và kiểm thử luồng AI module.
Các thành viên thêm plugin riêng (trend_classification, anomaly, insight, clustering) theo mẫu này."""
from ai.registry import register

register(
    key="describe",
    label="Thống kê mô tả tổng điểm theo năm",
    description="Tính mean, std, min, max của total_papi cho từng năm.",
    user_prompt="Tính thống kê mô tả (trung bình, độ lệch chuẩn, lớn nhất, nhỏ nhất) của tổng điểm PAPI theo từng năm.",
    system_instruction=(
        "Sử dụng bảng `prov_year`. "
        "Tính thống kê mô tả gồm mean, std, min, max của cột `total_papi` theo từng năm (`year`). "
        "Gán bảng kết quả vào biến `result`. Không cần vẽ biểu đồ."
    )
)
