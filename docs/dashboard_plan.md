# Kế hoạch Dashboard và bốn hướng phân tích

Mỗi hướng trình bày theo ba phần: nội dung, ý nghĩa, và câu hỏi cần trả lời để làm rõ vấn đề và đề
xuất giải pháp. Dữ liệu lấy từ `data/processed/`; phát hiện nền tảng ở `docs/eda_findings.md`.

## 1. Nguyên tắc thiết kế

Mỗi page phục vụ một lăng kính phân tích độc lập; mỗi page đọc bảng phù hợp nhất với loại biểu đồ (wide
cho map và ranking, long cho biểu đồ thống kê); tính toán nặng làm sẵn ở bước chuẩn bị dữ liệu, lúc
hiển thị chỉ đọc và lọc kèm `@st.cache_data`; không so sánh tổng điểm PAPI vắt qua mốc 2018 do số trục
đổi từ 6 lên 8.

## 2. Kiến trúc page và phân công

| Page | Vai trò | Phụ trách |
|---|---|---|
| Overview | Trang nền, chỉ số tóm tắt | Cả nhóm |
| Diễn biến theo thời gian | Hướng 1 | Thành viên 1 |
| So sánh giữa các tỉnh | Hướng 2 | Thành viên 2 |
| Phân tích theo trục | Hướng 3 | Thành viên 3 |
| Động lực thay đổi và phân nhóm | Hướng 4 | Thành viên 4 |
| AI Assistant | AI module human-in-the-loop | Cả nhóm |

Sidebar filter dùng chung: khoảng năm, tỉnh, vùng, trục, và chế độ thang điểm 6 trục hoặc 8 trục.

## 3. Hướng 1: Diễn biến theo thời gian

Nội dung. Mô tả trend của điểm PAPI và từng trục giai đoạn 2011-2024, và tác động của COVID-19 lên
trục dịch vụ công và quản trị điện tử. Bảng dùng: `agg_national_year`, `fact_papi_long`,
`agg_province_year`. Biểu đồ: line đa trục theo năm, line tổng điểm liền mạch dùng `total_papi_6dim`,
bar so sánh giai đoạn, so sánh trước và sau COVID cho D6 và D8. Phương pháp: ước lượng slope hồi quy
của từng trục theo năm; so sánh trung bình 2018-2019 với 2021-2022. AI technique: trend classification
(cải thiện, ổn định, suy giảm).

Ý nghĩa. Cho biết chất lượng quản trị cải thiện hay suy giảm và ở khía cạnh nào, từ đó xác định trục
cần ưu tiên. Tách riêng tác động COVID-19 cho phép đánh giá khả năng chống chịu của dịch vụ công và
mức độ thúc đẩy quản trị điện tử sau đại dịch.

Câu hỏi. Làm rõ vấn đề: điểm PAPI và từng trục thay đổi thế nào (Q1); D6 và D8 thay đổi thế nào sau
COVID-19 (Q8). Đề xuất giải pháp: trục suy giảm nào cần ưu tiên can thiệp; bài học COVID-19 cho việc
thúc đẩy quản trị điện tử.

## 4. Hướng 2: So sánh giữa các tỉnh

Nội dung. Tập trung cấp tỉnh, so sánh 63 tỉnh và xác định các tỉnh outlier. Bảng dùng:
`agg_province_year`, `dim_province`, và `vietnam_provinces.geojson`. Biểu đồ: choropleth theo năm,
bảng ranking cao nhất và thấp nhất, scatter điểm theo tỉnh. Phương pháp: anomaly detection dựa trên
standardized residual của tỉnh so với trend chung trong cùng năm. AI technique: anomaly detection.

Ý nghĩa. Định vị các tỉnh dẫn đầu và tụt hậu, tạo cơ sở để học hỏi và can thiệp. Phát hiện outlier
giúp khoanh vùng các trường hợp cần rà soát nguyên nhân.

Câu hỏi. Làm rõ vấn đề: tỉnh nào cao nhất và thấp nhất theo từng năm (Q2); tỉnh nào là outlier (Q7).
Đề xuất giải pháp: tỉnh tụt hậu nên tham khảo mô hình của tỉnh dẫn đầu nào; outlier cần rà soát theo
hướng nào.

## 5. Hướng 3: Phân tích theo trục

Nội dung. Xác định trục cải thiện rõ và trục còn yếu, và phân tích quan hệ giữa các trục. Bảng dùng:
`fact_papi_long`, `agg_province_year`, `dim_indicator`. Biểu đồ: small multiples cho từng trục, radar
8 trục cho một tỉnh chọn, heatmap correlation, scatter kèm regression cho cặp Minh bạch và Kiểm soát
tham nhũng. Phương pháp: correlation matrix (Pearson) trên các quan sát tỉnh-năm từ 2018; regression
của Kiểm soát tham nhũng theo Minh bạch. AI technique: sinh insight diễn giải quan hệ giữa các trục.

Ý nghĩa. Chỉ ra điểm mạnh và điểm yếu theo từng khía cạnh, từ đó xác định trục cần ưu tiên cải cách.
Kiểm định vai trò trung tâm của trục Minh bạch có giá trị thực tiễn vì nếu trục này quan hệ chặt với
nhiều trục khác thì cải thiện nó có thể tạo hiệu ứng lan tỏa.

Câu hỏi. Làm rõ vấn đề: trục nào cải thiện rõ nhất (Q4); trục nào còn yếu hoặc giảm (Q5); trục Minh
bạch có giữ vai trò trung tâm không (Q9); tỉnh nào làm tốt ở hai trục môi trường và quản trị điện tử
(Q10). Đề xuất giải pháp: cải thiện trục nào sẽ kéo theo trục khác; hai trục mới yếu nhất nên cải
thiện theo kinh nghiệm của tỉnh nào.

## 6. Hướng 4: Động lực thay đổi và phân nhóm

Nội dung. Xác định các tỉnh cải thiện hoặc suy giảm mạnh nhất, phân nhóm các tỉnh theo profile 8 trục,
và so sánh giữa 6 vùng. Bảng dùng: `agg_province_year`, `fact_papi_long`, `dim_province`. Biểu đồ:
bảng ranking mức tăng giảm, slopegraph, scatter các cluster, boxplot theo vùng. Phương pháp: tính mức
thay đổi trong cùng một chế độ trục; clustering bằng k-means trên 8 trục đã chuẩn hóa, số cluster chọn
theo elbow và silhouette; kiểm định khác biệt giữa các vùng bằng ANOVA hoặc Kruskal-Wallis. AI
technique: clustering.

Ý nghĩa. Nhận diện các tỉnh chuyển biến mạnh và các kiểu tỉnh điển hình, từ đó rút ra mô hình cải
thiện có thể nhân rộng. So sánh theo vùng làm rõ bất bình đẳng địa lý trong quản trị.

Câu hỏi. Làm rõ vấn đề: tỉnh nào cải thiện hoặc suy giảm mạnh nhất (Q3); có khác biệt giữa các vùng
không (Q6). Đề xuất giải pháp: mô hình của tỉnh cải thiện nhanh có thể nhân rộng thế nào; vùng tụt hậu
như Tây Nguyên cần hỗ trợ chính sách theo hướng nào.

## 7. Overview và AI module

Overview là entry point, hiển thị chỉ số tóm tắt của năm chọn, map thu nhỏ, danh sách tỉnh dẫn đầu và
xếp cuối, và link tới bốn page phân tích; dùng `agg_province_year`, không tính toán mới.

AI module human-in-the-loop gồm ba API: `api_ai` (sinh đề xuất), `api_exec` (execute), `api_logs` (ghi
log), theo quy trình con người phê duyệt. Bốn AI technique của bốn hướng là bốn case minh họa chạy qua
module. Hai chức năng văn bản bổ sung: AI-generated insight trên từng biểu đồ, và AI summary toàn
dashboard theo filter người dùng chọn.

## 8. Tiền đề dữ liệu cần bổ sung

Cột `total_papi_6dim` (tổng D1-D6) cho Hướng 1, và tệp `vietnam_provinces.geojson` khớp `province_id`
cho Hướng 2.

## 9. Bảng ánh xạ câu hỏi theo hướng

| Mã | Câu hỏi | Hướng |
|---|---|---|
| Q1 | Điểm PAPI thay đổi thế nào trong 2011-2024 | 1 |
| Q8 | Quản trị điện tử và dịch vụ công thay đổi thế nào sau COVID-19 | 1 |
| Q2 | Tỉnh nào cao nhất và thấp nhất theo từng năm | 2 |
| Q7 | Tỉnh nào là outlier so với trend chung | 2 |
| Q4 | Trục nào cải thiện rõ nhất | 3 |
| Q5 | Trục nào còn yếu hoặc giảm | 3 |
| Q9 | Trục Minh bạch có giữ vai trò trung tâm không | 3 |
| Q10 | Tỉnh nào làm tốt ở hai trục môi trường và quản trị điện tử | 3 |
| Q3 | Tỉnh nào cải thiện hoặc suy giảm mạnh nhất | 4 |
| Q6 | Có khác biệt giữa các vùng không | 4 |
