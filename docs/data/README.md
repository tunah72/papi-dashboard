# Dữ liệu PAPI — nguồn gốc, nội dung và pipeline xử lý

Đây là **nguồn sự thật duy nhất** cho dữ liệu của dự án PAPI Dashboard. Tài liệu này hợp nhất phần
nguồn gốc, cách thu thập, cấu trúc file thô, ý nghĩa biến, quy trình xử lý, schema đầu ra, kết quả kiểm
tra chất lượng và giới hạn diễn giải. Nhật ký chi tiết của lần chạy pipeline gần nhất nằm tại
[processing-log.md](processing-log.md) và được `src/build_dataset.py` sinh tự động.

> Snapshot trong tài liệu được đối chiếu trực tiếp với `data/processed/` ngày 21/07/2026. Khi có mâu
> thuẫn, ưu tiên file dữ liệu hiện tại, code pipeline, kiểm tra tự động và nhật ký lần chạy mới nhất.

## 1. Tóm tắt nhanh

| Thuộc tính | Giá trị |
|---|---|
| Bộ chỉ số | PAPI — Chỉ số Hiệu quả Quản trị và Hành chính công cấp tỉnh ở Việt Nam |
| Bản chất | Khảo sát trải nghiệm và cảm nhận của người dân về chính quyền địa phương |
| Đơn vị dữ liệu dự án | Điểm đã tổng hợp ở cấp tỉnh, không phải câu trả lời của từng người |
| Phạm vi thời gian | 2011–2024, 14 năm |
| Phạm vi không gian | 63 tỉnh/thành theo địa giới dùng trong dữ liệu PAPI, thuộc 6 vùng |
| Lĩnh vực | D1–D6 từ 2011; D7–D8 từ 2018 |
| File nguồn | 14 workbook Excel, một nguồn canonical cho mỗi năm |
| Bảng fact chính | 6.094 dòng, grain tỉnh × năm × lĩnh vực |
| Panel tỉnh–năm | 882 dòng = 63 tỉnh × 14 năm |
| Tỉnh–năm có tổng hợp lệ | 869/882; 13 trường hợp thiếu toàn bộ hoặc một phần |
| Mức độ Việt Nam | 100% quan sát thuộc Việt Nam |

## 2. Nguồn gốc và mục đích của PAPI

PAPI (*The Viet Nam Provincial Governance and Public Administration Performance Index*) là công cụ
theo dõi chính sách lấy người dân làm trung tâm. Chương trình đo lường và đối sánh trải nghiệm, cảm
nhận và mức độ hài lòng của người dân đối với quản trị, hành chính công và cung ứng dịch vụ công ở
cấp quốc gia và địa phương.

PAPI do UNDP Việt Nam, Trung tâm Nghiên cứu Phát triển và Hỗ trợ Cộng đồng (CECODES) và Real-Time
Analytics (RTA) phối hợp thực hiện, với sự hỗ trợ điều phối khảo sát của Mặt trận Tổ quốc Việt Nam.
Khảo sát được triển khai toàn quốc hằng năm từ 2011. Theo báo cáo chính thức, năm 2024 có 18.894 công
dân từ 18 tuổi trở lên được chọn ngẫu nhiên tham gia; từ năm 2009 đến hết 2024 đã có 216.673 lượt
người dân được phỏng vấn trực tiếp.

Nguồn chính thức:

- [Trang dự án PAPI — UNDP Việt Nam](https://www.undp.org/vietnam/projects/papi-viet-nam-provincial-governance-and-public-administration-performance-index)
- [Báo cáo PAPI 2024 — UNDP Việt Nam](https://www.undp.org/vietnam/publications/2024-provincial-governance-and-public-administration-performance-index-papi-report)
- [Cổng dữ liệu PAPI](https://papi.org.vn/eng/papi-data/)

Mục đích của PAPI là tạo bằng chứng định lượng từ tiếng nói người dân để:

1. người dân và các bên liên quan đối chiếu kết quả quản trị địa phương;
2. chính quyền tự nhìn lại điểm mạnh, điểm yếu;
3. thúc đẩy cạnh tranh mang tính xây dựng và học hỏi giữa các địa phương;
4. gợi mở lĩnh vực cần cải thiện trong quản trị và cung ứng dịch vụ công.

## 3. Dữ liệu được thu thập và tạo thành điểm như thế nào

Luồng hình thành dữ liệu ở mức khái niệm:

```text
Người dân được chọn vào mẫu khảo sát
    → trả lời về trải nghiệm và cảm nhận trong đời sống thực tế
    → PAPI tổng hợp chỉ tiêu và trục thành phần
    → điểm 8 lĩnh vực ở cấp tỉnh
    → tổng điểm và bảng chỉ tiêu cấp tỉnh được công bố hằng năm
    → dự án tải 14 file Excel công khai và chuẩn hóa thành panel 2011–2024
```

Dữ liệu trong repo là **kết quả đã tổng hợp cấp tỉnh**. Repo không chứa microdata từng người, trọng số
mẫu cá nhân hay các biến nhân khẩu học như giới tính, dân tộc và tình trạng cư trú. Vì vậy Dashboard
phân tích khác biệt giữa tỉnh, vùng, năm và lĩnh vực; không thể phân tích trực tiếp khác biệt giữa các
nhóm dân cư.

PAPI công bố nhiều loại thống kê ở một số năm gần đây, gồm ước lượng không trọng số, có trọng số,
khoảng tin cậy và sai số chuẩn. Dataset của dự án chỉ lấy dòng **Unweighted** để giữ một quy tắc nhất
quán và dễ giải thích. Đây là lựa chọn kỹ thuật của dự án, không có nghĩa ước lượng unweighted luôn
phù hợp cho mọi nghiên cứu PAPI khác.

## 4. Ý nghĩa của điểm PAPI

Mỗi điểm lĩnh vực trả lời câu hỏi:

> Người dân trong mẫu khảo sát của tỉnh đó, ở năm đó, đánh giá trải nghiệm với một mặt quản trị địa
> phương tích cực đến mức nào?

Điểm cao hơn nghĩa là trải nghiệm hoặc cảm nhận tích cực hơn. Điểm không phải phép đo trực tiếp về
ngân sách, năng suất cơ quan nhà nước hay hiệu quả chính sách khách quan.

Cấu trúc chỉ số gốc có bốn tầng:

```text
Tổng PAPI
  └── lĩnh vực D1–D8
       └── trục thành phần
            └── chỉ tiêu/câu hỏi khảo sát
```

Dataset v0 của dự án chỉ giữ **8 điểm lĩnh vực và tổng điểm cấp tỉnh**. Trục thành phần và chỉ tiêu thô
chưa được đưa vào bảng processed.

### Tám lĩnh vực

| Mã | Tên lĩnh vực | Có từ | Nội dung đo lường ở mức khái quát |
|---|---|---:|---|
| D1 | Tham gia của người dân ở cấp cơ sở | 2011 | Tri thức công dân, cơ hội tham gia, bầu cử cơ sở, đóng góp tự nguyện |
| D2 | Công khai, minh bạch trong ra quyết định | 2011 | Tiếp cận thông tin, hộ nghèo, ngân sách và kế hoạch sử dụng đất |
| D3 | Trách nhiệm giải trình với người dân | 2011 | Tương tác với chính quyền, phản ánh/khiếu nại và tiếp cận tư pháp |
| D4 | Kiểm soát tham nhũng trong khu vực công | 2011 | Vòi vĩnh, hối lộ, công bằng tuyển dụng và quyết tâm chống tham nhũng |
| D5 | Thủ tục hành chính công | 2011 | Trải nghiệm làm chứng thực, giấy phép, sổ đỏ và thủ tục cấp xã |
| D6 | Cung ứng dịch vụ công | 2011 | Y tế, giáo dục, hạ tầng căn bản và an ninh trật tự |
| D7 | Quản trị môi trường | 2018 | Chất lượng không khí, nước và phản ứng với vấn đề môi trường |
| D8 | Quản trị điện tử | 2018 | Tiếp cận internet, thông tin và dịch vụ công trực tuyến |

Điểm từng lĩnh vực nằm trên thang 1–10. D1–D6 có chuỗi từ 2011; D7–D8 chỉ có từ 2018 và phải để
thiếu trước thời điểm đó, không được điền 0 hoặc nội suy.

### Hai thước đo tổng trong dự án

| Thước đo | Công thức | Khoảng năm hợp lệ | Mục đích |
|---|---|---|---|
| `total_papi_6dim` | D1 + … + D6 | 2011–2024 | So sánh dài hạn với cùng một cấu trúc lĩnh vực |
| `total_papi` trong phạm vi 8 lĩnh vực | D1 + … + D8 | 2018–2024 | Đọc tổng PAPI đầy đủ của giai đoạn có D7–D8 |

Trong bảng panel, `total_papi` kỹ thuật cũng chứa tổng sáu lĩnh vực ở các năm trước 2018 để bảo toàn
nguồn. UI/API tách hai phạm vi `six` và `eight`, không nối hai cấu trúc thành một chuỗi so sánh. Bước
nhảy tổng điểm năm 2018 chủ yếu do thêm D7–D8, không được diễn giải là cải thiện thực chất.

## 5. Danh mục 14 file nguồn

`data/raw/` là vùng **chỉ đọc**. Mỗi file tương ứng với nguồn canonical của một năm:

| Năm | File nguồn canonical | Cấu trúc chính |
|---:|---|---|
| 2011 | `PAPI-2011-Dữ-liệu-1.xlsx` | Tỉnh theo hàng, 6 lĩnh vực |
| 2012 | `PAPI-2012-Dữ-liệu-1.xlsx` | Tỉnh theo hàng, 6 lĩnh vực |
| 2013 | `PAPI-2013-Dữ-liệu-1.xlsx` | Tỉnh theo hàng, 6 lĩnh vực |
| 2014 | `PAPI-2014-Dữ-liệu-1.xlsx` | Tỉnh theo hàng, 6 lĩnh vực |
| 2015 | `PAPI-2015-Dữ-liệu-1.xlsx` | Tỉnh theo hàng, 6 lĩnh vực |
| 2016 | `PAPI-2016-Dữ-liệu-1.xlsx` | Tỉnh theo hàng, 6 lĩnh vực |
| 2017 | `PAPI-2017-Dữ-liệu-1.xlsx` | Tỉnh theo hàng, 6 lĩnh vực |
| 2018 | `PAPI2018_ProvincialScores_ByIndicators_VIE.xlsx` | Chỉ tiêu theo hàng, tỉnh theo cột, 8 lĩnh vực |
| 2019 | `2019_PAPI_Provincial_indicators2019_VIE_ENG.xlsx` | Chỉ tiêu theo hàng, tỉnh theo cột |
| 2020 | `2020PAPI_ProvincialIndicators_BangChiTieuCapTinh-1.xlsx` | Chỉ tiêu theo hàng, tỉnh theo cột |
| 2021 | `1.2021PAPI_ProvincialIndicators_BangChiTieuCapTinh.xlsx` | Chỉ tiêu theo hàng, tỉnh theo cột |
| 2022 | `2022PAPI_ProvincialIndicators_BangChiTieuCapTinh.xlsx` | Chỉ tiêu theo hàng, tỉnh theo cột |
| 2023 | `2023PAPI_ProvincialIndicators_BangChiTieuCapTinh..xlsx` | Chỉ tiêu theo hàng, tỉnh theo cột |
| 2024 | `2024PAPI_ProvincialIndicators_BangChiTieuCapTinh_34_TinhThanh.xlsx` | Metadata 34 tỉnh mới và dữ liệu PAPI theo 63 tỉnh cũ |

Một số workbook mới chứa lại sheet của năm cũ. Pipeline không gộp tất cả sheet vì sẽ đếm trùng; kế
hoạch nguồn trong `src/papi_lib.py::year_sources()` chỉ định chính xác file và sheet dùng cho mỗi năm.

## 6. Khác biệt và bẫy trong file thô

Pipeline xử lý minh bạch các trường hợp sau:

1. **Đảo chiều bảng:** 2011–2017 đặt tỉnh theo hàng, từ 2018 đặt tỉnh theo cột.
2. **Nhãn thay đổi:** `Chỉ số nội dung 1` và `Dimension 1` cùng chỉ D1; parser nhận theo số lĩnh vực.
3. **Thay đổi cấu trúc chỉ số:** chỉ có D1–D6 trước 2018, thêm D7–D8 từ 2018.
4. **Workbook lặp năm:** file mới có thể chứa lại sheet năm cũ; pipeline dùng một nguồn canonical/năm.
5. **Tên sheet sai hoặc không thống nhất:** ví dụ tab trong file 2011 mang nhãn dễ gây nhầm với 2012;
   pipeline tin kế hoạch nguồn đã kiểm chứng thay vì tự suy năm từ tên tab.
6. **Tên tỉnh không thống nhất:** có/không dấu, tiền tố `TP.`, khoảng trắng và dấu gạch nối; pipeline
   chuẩn hóa rồi nối với `province_id` cố định.
7. **Nhiều loại ước lượng:** pipeline chỉ lấy điểm lĩnh vực và tổng PAPI không trọng số.
8. **File 2024 có metadata về 34 tỉnh:** parser dò dòng có nhiều tên tỉnh cũ khớp nhất và không dùng
   metadata chuyển đổi địa giới làm điểm PAPI.
9. **Giá trị 0 không hợp lệ:** 28 record bằng 0 gồm 24 điểm lĩnh vực và 4 tổng điểm được loại trước
   khi aggregate; chúng được xem là thiếu, không phải điểm 0 thật.

## 7. Quy trình xử lý có thể tái lập

Pipeline kỹ thuật là `src/build_dataset.py`, dùng các parser và bảng tra cứu trong `src/papi_lib.py`:

```text
data/raw/*.xlsx
    → chọn file + sheet canonical theo năm
    → parse 2011–2017 hoặc parse bảng transposed 2018–2024
    → chuẩn hóa tỉnh và mã D1–D8
    → chỉ giữ điểm Unweighted
    → loại record điểm 0 không hợp lệ
    → tách TOTAL khỏi fact lĩnh vực
    → khử trùng tỉnh × năm × lĩnh vực
    → tạo panel đầy đủ 63 × 14
    → giữ thiếu tại nguồn là NaN
    → tính tổng, hạng, tier và thống kê toàn quốc
    → chạy quality checks
    → ghi data/processed/* và processing-log.md
```

### Quy tắc làm sạch

- Không sửa workbook nguồn.
- Không điền số giả, nội suy hoặc mặc định điểm thiếu bằng 0.
- Chỉ tính tổng khi có đủ số lĩnh vực mong đợi của phạm vi.
- `total_papi_6dim` yêu cầu đủ D1–D6.
- Tổng 8 lĩnh vực yêu cầu đủ D1–D8.
- Thứ hạng chỉ được tính trong các tỉnh có tổng hợp lệ của cùng năm.
- `tier` là tứ phân vị theo năm, không phải phân loại chính thức của PAPI.

### Tái lập

Từ thư mục gốc dự án, với môi trường đã cài dependencies:

```bash
python src/build_dataset.py
```

Lệnh này **ghi lại** `data/processed/` và `docs/data/processing-log.md`. Chỉ chạy khi chủ động kiểm
chứng hoặc thay đổi pipeline; sau khi chạy phải kiểm tra diff. Các notebook trong `notebooks/` trình
bày workflow và gọi lại logic dùng chung, nhưng pipeline trong `src/` là đường build kỹ thuật chuẩn.

## 8. Kết quả xử lý hiện tại

### Artifact đầu ra

| File | Dạng/grain | Số dòng | Vai trò |
|---|---|---:|---|
| `fact_papi_long.parquet` và `.csv` | Tỉnh × năm × lĩnh vực | 6.094 | Fact gốc cho line, heatmap, phân phối và phân nhóm |
| `agg_province_year.parquet` và `.csv` | Tỉnh × năm | 882 | KPI, bản đồ, xếp hạng, benchmark và thay đổi hai mốc |
| `agg_national_year.parquet` | Năm × lĩnh vực | 112 | Mean/min/max/std theo năm và lĩnh vực |
| `dim_province.csv` | Một tỉnh | 63 | Khóa tỉnh, tên Việt/Anh, vùng và mã vùng |
| `dim_indicator.csv` | Một lĩnh vực | 8 | Tên, mã, màu, thứ tự và năm bắt đầu |
| `vietnam_provinces.geojson` | Feature địa lý | 64 record/63 ID | Hình học để vẽ choropleth |

GeoJSON có hai feature cùng `province_id=49`, tương ứng các phần hình học của Bà Rịa–Vũng Tàu. Data
loader gộp chúng thành một MultiPolygon trong bộ nhớ và rewind vòng để Plotly/D3 hiển thị đúng; file
GeoJSON trên đĩa không bị sửa.

### Schema `fact_papi_long`

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `province_id` | `int16` | Khóa tỉnh từ 1 đến 63 |
| `year` | `int16` | Năm quan sát, 2011–2024 |
| `code` | `category` | D1–D8 |
| `score` | `float32` | Điểm lĩnh vực PAPI |

### Schema `agg_province_year`

| Nhóm cột | Ý nghĩa |
|---|---|
| `province_id`, `province_vi`, `region`, `region_id`, `year` | Định danh tỉnh, vùng và năm |
| `D1`…`D8` | Điểm từng lĩnh vực; D7–D8 thiếu trước 2018 |
| `total_papi` | Tổng các lĩnh vực mong đợi của năm; NaN nếu thiếu lĩnh vực |
| `total_papi_6dim` | Tổng D1–D6 dùng cho chuỗi so sánh 2011–2024 |
| `total_official` | Tổng đọc trực tiếp từ nguồn khi có, dùng đối chiếu |
| `n_dims` | Số lĩnh vực thực sự có dữ liệu |
| `rank_year` | Hạng giảm dần trong cùng năm trên các tổng hợp lệ |
| `tier` | Tứ phân vị trong cùng năm |

### Schema `agg_national_year`

| Cột | Ý nghĩa |
|---|---|
| `year`, `code` | Năm và lĩnh vực |
| `mean_score` | Trung bình các tỉnh có dữ liệu |
| `min_score`, `max_score` | Giá trị nhỏ nhất và lớn nhất |
| `std_score` | Độ lệch chuẩn giữa các tỉnh |

Mỗi thống kê toàn quốc chỉ dùng tỉnh có dữ liệu ở điểm đó. UI/API phải hiển thị `n` hoặc
`contributorN` thay vì giả định luôn có đủ 63 tỉnh.

## 9. Dữ liệu thiếu và chất lượng

### 13 tỉnh–năm không có tổng hợp lệ

| Năm | Tỉnh | Số lĩnh vực có / mong đợi | Lĩnh vực thiếu |
|---:|---|---:|---|
| 2014 | Bắc Giang | 0/6 | D1–D6 |
| 2014 | Đồng Tháp | 0/6 | D1–D6 |
| 2018 | Quảng Ninh | 6/8 | D2, D4 |
| 2018 | Đồng Tháp | 6/8 | D2, D4 |
| 2021 | Bắc Giang | 0/8 | D1–D8 |
| 2021 | Bắc Ninh | 0/8 | D1–D8 |
| 2021 | Quảng Ninh | 0/8 | D1–D8 |
| 2022 | Bắc Giang | 4/8 | D1, D2, D4, D5 |
| 2022 | Bắc Ninh | 4/8 | D2, D3, D4, D8 |
| 2023 | Quảng Ninh | 0/8 | D1–D8 |
| 2023 | Bình Dương | 0/8 | D1–D8 |
| 2024 | Vĩnh Phúc | 0/8 | D1–D8 |
| 2024 | Tiền Giang | 0/8 | D1–D8 |

Đây là thiếu tại nguồn hoặc record bị zero hóa trong nguồn và đã được chuyển thành thiếu. Dashboard
không được tô các trường hợp này như điểm 0, tự nội suy hoặc xếp hạng chúng.

### Kết quả quality checks của snapshot

| Kiểm tra | Kết quả |
|---|---|
| Fact có ít nhất 2.000 dòng | PASS — 6.094 dòng |
| Mỗi năm có ít nhất 60 tỉnh xuất hiện trong fact | PASS — 60 đến 63 tỉnh |
| Panel đủ 63 × 14 | PASS — 882 dòng |
| Số lĩnh vực đúng theo giai đoạn | PASS — 6 trước 2018, 8 từ 2018 |
| Điểm lĩnh vực trong `(0, 10]` | PASS — quan sát từ 1,93 đến 8,46 |
| Tổng nằm trong phạm vi hợp lệ | PASS — quan sát từ 31,7 đến 48,8 |
| Không trùng tỉnh × năm × lĩnh vực | PASS |
| Tổng tính lại khớp tổng official khi đủ 8 lĩnh vực | PASS — 369 dòng, lệch lớn nhất 0,0000 |

## 10. Kết quả EDA dùng để kiểm chứng và định hướng Dashboard

Các số dưới đây là mô tả trên snapshot hiện tại, không phải kết luận nhân quả.

### Mặt bằng lĩnh vực

| Lĩnh vực | Điểm trung bình trên các quan sát có dữ liệu |
|---|---:|
| D6 Cung ứng dịch vụ công | 7,147 |
| D5 Thủ tục hành chính công | 7,122 |
| D4 Kiểm soát tham nhũng | 6,380 |
| D2 Công khai, minh bạch | 5,471 |
| D1 Tham gia | 5,085 |
| D3 Trách nhiệm giải trình | 5,022 |
| D7 Quản trị môi trường | 3,698 |
| D8 Quản trị điện tử | 3,104 |

D7–D8 chỉ có giai đoạn 2018–2024, nên các trung bình trên không có cùng số năm quan sát với D1–D6.

### Thay đổi trung bình toàn quốc từ mốc đầu có dữ liệu đến 2024

| Lĩnh vực | Mốc so sánh | Thay đổi |
|---|---|---:|
| D1 Tham gia | 2011 → 2024 | −0,38 |
| D2 Công khai, minh bạch | 2011 → 2024 | −0,25 |
| D3 Trách nhiệm giải trình | 2011 → 2024 | −1,30 |
| D4 Kiểm soát tham nhũng | 2011 → 2024 | +1,30 |
| D5 Thủ tục hành chính | 2011 → 2024 | +0,33 |
| D6 Cung ứng dịch vụ công | 2011 → 2024 | +0,95 |
| D7 Quản trị môi trường | 2018 → 2024 | −0,94 |
| D8 Quản trị điện tử | 2018 → 2024 | +0,34 |

### Snapshot 2024, tổng 8 lĩnh vực

- 61 tỉnh có tổng hợp lệ; Vĩnh Phúc và Tiền Giang thiếu.
- Ba tỉnh cao nhất: Quảng Ninh 47,82; Tây Ninh 47,35; Bình Thuận 47,13.
- Ba tỉnh thấp nhất: Kiên Giang 39,91; Kon Tum 40,31; Cần Thơ 40,44.
- Trung bình vùng cao nhất: Đồng bằng sông Hồng 44,32.
- Trung bình vùng thấp nhất: Tây Nguyên 41,23.
- Cặp tương quan Pearson mạnh nhất trong snapshot là D1–D2, `r ≈ 0,72`.

Tương quan chỉ mô tả mức cùng biến thiên giữa các tỉnh trong một snapshot, không chứng minh lĩnh vực
này gây ra lĩnh vực kia.

## 11. Dataset hỗ trợ mục tiêu Dashboard như thế nào

| Hướng phân tích | Câu hỏi dữ liệu trả lời tốt | Bảng chính |
|---|---|---|
| Diễn biến theo thời gian | Lĩnh vực, vùng hoặc tỉnh tăng/giảm khi nào và bao nhiêu? | `fact`, `national`, `prov_year` |
| Khác biệt vùng và tỉnh | Địa phương nào cao/thấp, phân hóa và lệch benchmark ra sao? | `prov_year`, `dim_prov`, GeoJSON |
| Mối quan hệ lĩnh vực | Các lĩnh vực có cùng biến thiên không, tỉnh nào là ngoại lệ? | `prov_year` |
| Thay đổi và phân nhóm | Tỉnh nào đổi mạnh, các profile PAPI nào tương đồng? | `prov_year` |

Dataset phù hợp với câu hỏi **cái gì, khi nào, ở đâu, khác bao nhiêu và đi cùng điều gì**. Dataset
không tự trả lời **vì sao** hoặc chứng minh tác động chính sách. Muốn phân tích nguyên nhân cần ghép
thêm biến kinh tế–xã hội/chính sách, kiểm soát nhiễu và dùng thiết kế thống kê phù hợp.

## 12. Giới hạn và quy tắc diễn giải

1. PAPI phản ánh trải nghiệm và cảm nhận của người dân; không phải toàn bộ hiệu quả quản trị khách quan.
2. Dữ liệu repo là aggregate cấp tỉnh, không phân tích được khác biệt cá nhân hoặc nhóm dân cư.
3. D7–D8 chỉ có từ 2018; không tạo dữ liệu giả cho giai đoạn trước.
4. Không so trực tiếp tổng 6 lĩnh vực với tổng 8 lĩnh vực qua mốc 2018.
5. Không giả định luôn có 63 tỉnh trong mọi thống kê; phải công bố số quan sát thực tế.
6. Xếp hạng phụ thuộc năm, phạm vi và các tỉnh đủ dữ liệu; chênh lệch nhỏ không mặc nhiên có ý nghĩa
   thống kê.
7. Pearson, hồi quy và phân cụm là công cụ mô tả; không chứng minh quan hệ nhân quả hoặc tạo phân loại
   chính thức về chất lượng chính quyền.
8. Các nhóm KMeans mô tả profile tương đồng, không nên đặt tên “tốt/xấu” nếu không có quy tắc độc lập.

## 13. Quy tắc duy trì tài liệu

- Chỉ cập nhật số liệu snapshot sau khi đối chiếu trực tiếp `data/processed/`.
- Không sửa `processing-log.md` bằng tay; thay đổi thông điệp log tại pipeline và chạy lại có chủ đích.
- Khi thêm nguồn hoặc đổi phương pháp, cập nhật tài liệu này cùng code và quality checks.
- Không tạo thêm tài liệu “data understanding”, “processed schema” hoặc “EDA findings” song song;
  bổ sung đúng mục trong file này để tránh nhiều nguồn sự thật.
- Mọi chuyển đổi dữ liệu phải có code tái lập, không chỉ mô tả bằng văn bản hoặc thao tác thủ công.
