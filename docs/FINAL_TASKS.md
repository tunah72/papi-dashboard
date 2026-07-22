# Phân công hoàn thiện báo cáo và slide

Tài liệu này phân công các phần còn lại của báo cáo và slide đồ án PAPI. Mỗi thành viên chỉ chỉnh sửa
đúng phần được giao, đối chiếu số liệu với Dashboard và tài liệu nguồn trước khi viết, không tự suy
diễn hoặc tạo thêm số liệu.

## 1. Bảng phân công

| Thành viên | MSSV | Phạm vi | File báo cáo | File slide | Trạng thái |
|---|---:|---|---|---|---|
| Dương Tuấn Anh | 23120208 | Giới thiệu; dữ liệu và tiền xử lý; Bức tranh tổng quan; Diễn biến theo thời gian; thiết kế Dashboard | `report/content/01_introduction.tex`, `report/content/02_data_preprocessing.tex`, các phần tương ứng trong `report/content/03_visual_analysis.tex`, `report/content/04_dashboard_design.tex` | `slides/content/2-introduction.tex` đến `slides/content/5-time-trend.tex`, `slides/content/9-dashboard.tex` | Đã hoàn thành |
| Lê Xuân Trí | 23120199 | Phân tích Khác biệt giữa vùng và tỉnh | Chỉ sửa `\subsection{Phân tích Khác biệt giữa vùng và tỉnh}` trong `report/content/03_visual_analysis.tex` | `slides/content/6-regional-province.tex` | Cần hoàn thành |
| Nguyễn Trần Trung Kiên | 23122038 | Phân tích Mối quan hệ giữa các lĩnh vực | Chỉ sửa `\subsection{Phân tích Mối quan hệ giữa các lĩnh vực}` trong `report/content/03_visual_analysis.tex` | `slides/content/7-dimension-relationships.tex` | Cần hoàn thành |
| Lê Đức Phúc | 23122045 | Phân tích Thay đổi và phân nhóm tỉnh; tổng hợp kết quả; kết luận, hạn chế và hướng phát triển | Chỉ sửa `\subsection{Phân tích Thay đổi và phân nhóm tỉnh}` và `\subsection{Tổng hợp các kết quả phân tích chính}` trong `report/content/03_visual_analysis.tex`; hoàn thiện `report/content/05_conclusion.tex` | `slides/content/8-dynamics-clustering.tex`, `slides/content/10-conclusion.tex` | Cần hoàn thành |

Các phần phân tích cùng nằm trong `report/content/03_visual_analysis.tex`. Khi làm việc song song,
không thay toàn bộ file và không sửa nội dung thuộc thành viên khác. Mỗi người chỉ thay phần `TODO`
trong đúng `subsection` được giao; nên tạo một commit riêng để Tuấn Anh hợp nhất và biên dịch cuối.

## 2. Quy cách chung khi viết báo cáo

Mỗi hướng phân tích cần trình bày đủ bốn biểu đồ theo cùng một cấu trúc:

1. Một đoạn mở đầu ngắn nêu câu hỏi phân tích, phạm vi năm, số lĩnh vực và đối tượng so sánh.
2. Với từng biểu đồ: nêu loại biểu đồ, cách mã hóa dữ liệu, lý do lựa chọn và cách đọc cần thiết.
3. Chèn hình ngay sau phần mô tả; hình phải rõ, không chứa thông tin thừa và không dùng ảnh do AI tạo.
4. Sau hình chỉ giữ hai gạch đầu dòng: `Nhận xét` và `Định hướng`.

Yêu cầu bắt buộc:

- Dùng văn phong tiếng Việt trang trọng, khách quan và ngắn gọn; không mô tả dài dòng về mã nguồn,
  đường dẫn nội bộ hoặc quy trình triển khai giao diện.
- Mọi nhận xét phải có số liệu nhìn thấy trên biểu đồ hoặc được xác nhận từ cùng dữ liệu của Dashboard.
  Nếu chưa xác nhận được số liệu, để `TODO: kiểm tra trên Dashboard`, không ước lượng.
- Ghi rõ năm, phạm vi 6 hoặc 8 lĩnh vực và số quan sát thực tế `n` khi kết quả phụ thuộc dữ liệu thiếu.
- Không so sánh trực tiếp tổng 6 lĩnh vực với tổng 8 lĩnh vực qua mốc năm 2018.
- Không diễn giải tương quan, hồi quy, PCA hoặc phân nhóm thành quan hệ nhân quả, chất lượng quản trị
  chính thức hay tác động chính sách.
- Dùng số thập phân với dấu phẩy; dùng gạch ngang ngắn; chỉ giải thích thuật ngữ tiếng Anh ở lần xuất
  hiện đầu tiên.
- Mỗi hình phải nằm trong môi trường `figure`, có `\caption`, `\label` và được tham chiếu bằng
  `Hình~\ref{...}`. Chú thích hình đặt dưới hình; chú giải chỉ giữ thông tin cần để đọc màu, ký hiệu,
  đường chuẩn hoặc dữ liệu thiếu.
- Nếu có bảng, dùng `booktabs`, không dùng đường kẻ dọc và đặt chú thích phía trên.
- Không thêm dòng “Nguồn: nhóm tác giả tổng hợp từ dữ liệu PAPI”. Nguồn dữ liệu chung được trích dẫn
  bằng tài liệu PAPI hiện có trong báo cáo.

Có thể dùng phần Bức tranh tổng quan và Diễn biến theo thời gian đang hoàn thiện trong
`report/content/03_visual_analysis.tex` làm mẫu về độ dài, cấu trúc hình và cặp gạch đầu dòng
`Nhận xét` - `Định hướng`.

## 3. Quy cách chung khi soạn slide

- Giữ nguyên tiêu đề các khung slide đã có.
- Mỗi hướng phân tích có thể dùng hai slide hiện tại; chỉ tách thêm khi bốn biểu đồ không còn đọc được
  ở tỷ lệ 16:9. Không thu nhỏ hình đến mức mất nhãn hoặc chú giải.
- Mỗi slide ưu tiên hai biểu đồ đặt cạnh nhau. Dưới mỗi biểu đồ ghi một dòng loại biểu đồ và một đến
  hai gạch đầu dòng kết quả chính.
- Slide cuối của mỗi hướng có một dòng `Định hướng` gắn trực tiếp với kết quả vừa trình bày.
- Chỉ giữ từ khóa và số liệu chính; không sao chép nguyên đoạn văn từ báo cáo.
- Dùng `\item[-]`, hạn chế khối hộp màu, không in đậm tùy tiện và không dùng ảnh do AI tạo.
- Hình phải có chú thích phía dưới. Màu, tên vùng, tên lĩnh vực và ký hiệu tăng/giảm phải nhất quán
  với Dashboard và các slide đã hoàn thành.
- Có thể dùng `slides/content/5-time-trend.tex` làm mẫu bố cục hai biểu đồ, kết quả và định hướng.

## 4. Hướng dẫn cho Lê Xuân Trí

### Phần Khác biệt giữa vùng và tỉnh

Nguồn cần đọc:

- `docs/design/regional_province.md`: câu hỏi, bốn biểu đồ, tương tác và giới hạn diễn giải.
- `docs/data/README.md`: phạm vi dữ liệu, lĩnh vực và dữ liệu thiếu.
- `docs/design/README.md`: ma trận biểu đồ và nguyên tắc trực quan chung.
- `report/img/dashboard/dashboard_regional_province_page.png`: bố cục trang hiện tại.

Bốn nội dung phải trình bày:

| Thứ tự | Biểu đồ | Câu hỏi cần trả lời | Điểm cần nhấn mạnh |
|---:|---|---|---|
| 1 | Biểu đồ hộp kết hợp điểm phân tán theo vùng | Vùng nào có mặt bằng cao, thấp và phân hóa rộng? | Trung vị, khoảng tứ phân vị, từng tỉnh và `n` của vùng |
| 2 | Biểu đồ kẹo mút xếp hạng tỉnh trong vùng | Tỉnh được chọn đứng ở đâu trong vùng? | Hạng, tổng số tỉnh hợp lệ và khoảng cách với tỉnh dẫn đầu |
| 3 | Biểu đồ chuẩn đối chiếu tổng điểm | Tỉnh cao hoặc thấp hơn trung bình vùng và toàn bộ mẫu bao nhiêu? | Ba mốc trên cùng thang đo và `n` của từng chuẩn đối chiếu |
| 4 | Biểu đồ radar hồ sơ lĩnh vực | Tỉnh mạnh hoặc hạn chế ở lĩnh vực nào so với vùng và toàn bộ mẫu? | Cùng thang 1-10, tối đa ba đường và không so diện tích đa giác |

Ảnh nên lưu trong `report/img/regional_province/` với tên dễ nhận biết, chẳng hạn
`regional_province_distribution_2024.png`, `regional_province_ranking_2024.png`,
`regional_province_benchmark_2024.png` và `regional_province_profile_2024.png`.

Trong slide 12 trình bày biểu đồ 1-2; slide 13 trình bày biểu đồ 3-4, các kết quả chính và định hướng.
Mọi so sánh phải cùng năm và cùng phạm vi 6 hoặc 8 lĩnh vực. Không gọi tỉnh hoặc vùng là “tốt”, “xấu”;
dùng “điểm cao hơn”, “điểm thấp hơn” hoặc “phân hóa rộng hơn”.

## 5. Hướng dẫn cho Nguyễn Trần Trung Kiên

### Phần Mối quan hệ giữa các lĩnh vực

Nguồn cần đọc:

- `docs/design/dimension_relationships.md`: định nghĩa bốn biểu đồ và giới hạn phương pháp.
- `docs/data/README.md`: thang điểm, số lĩnh vực và quy tắc dữ liệu thiếu.
- `docs/design/README.md`: quan hệ giữa trang này với các hướng phân tích khác.
- `report/img/dashboard/dashboard_dimension_relationships_page.png`: bố cục trang hiện tại.

Bốn nội dung phải trình bày:

| Thứ tự | Biểu đồ | Câu hỏi cần trả lời | Điểm cần nhấn mạnh |
|---:|---|---|---|
| 1 | Bản đồ nhiệt tương quan | Cặp lĩnh vực nào cùng biến thiên mạnh nhất? | Thang từ -1 đến 1, hệ số Pearson và `n` hợp lệ của từng cặp |
| 2 | Biểu đồ phân tán và đường hồi quy | Quan hệ của cặp được chọn thể hiện ra sao giữa các tỉnh? | Mỗi điểm là một tỉnh; nêu hệ số tương quan, $R^2$ và nhóm điểm nổi bật |
| 3 | Biểu đồ phần dư | Tỉnh nào lệch nhiều nhất khỏi xu hướng tuyến tính? | Dấu và độ lớn phần dư; không gọi phần dư lớn là lỗi dữ liệu |
| 4 | Biểu đồ khoảng trung bình và độ lệch chuẩn | Lĩnh vực nào có mặt bằng cao và phân hóa lớn? | Trung bình, độ lệch chuẩn và `n`; độ lệch chuẩn không phải khoảng tin cậy |

Ảnh nên lưu trong `report/img/dimension_relationships/` với tên
`dimension_correlation_heatmap_2024.png`, `dimension_pair_scatter_2024.png`,
`dimension_residual_plot_2024.png` và `dimension_variation_range_2024.png`.

Trong slide 14 trình bày biểu đồ 1-2; slide 15 trình bày biểu đồ 3-4, các kết quả chính và định hướng.
Mọi kết luận chỉ mô tả mức cùng biến thiên trong năm đang chọn. Không dùng các từ “tác động”, “dẫn
đến” hoặc “quyết định” khi chỉ có tương quan và hồi quy mô tả.

## 6. Hướng dẫn cho Lê Đức Phúc

### Phần Thay đổi và phân nhóm tỉnh

Nguồn cần đọc:

- `docs/design/dynamics_clustering.md`: bốn biểu đồ, phương pháp phân nhóm và giới hạn diễn giải.
- `docs/data/README.md`: điều kiện đủ dữ liệu ở hai mốc và phạm vi lĩnh vực.
- `docs/design/README.md`: vai trò của phân nhóm trong mạch kể chung.
- `report/img/dashboard/dashboard_dynamics_clustering_page.png`: bố cục trang hiện tại.

Bốn nội dung phải trình bày:

| Thứ tự | Biểu đồ | Câu hỏi cần trả lời | Điểm cần nhấn mạnh |
|---:|---|---|---|
| 1 | Biểu đồ nối điểm đầu và cuối | Tỉnh nào tăng hoặc giảm nhiều nhất giữa hai mốc? | Điểm đầu, điểm cuối, chênh lệch có dấu và số tỉnh đủ dữ liệu |
| 2 | Các biểu đồ thanh phân kỳ theo nhóm | Mỗi nhóm nổi bật hoặc thấp hơn mặt bằng ở lĩnh vực nào? | Giá trị chuẩn hóa, cỡ nhóm và nhãn nhóm không phải thứ hạng |
| 3 | Biểu đồ quỹ đạo PCA | Tỉnh nào dịch chuyển xa trong không gian nhiều lĩnh vực? | Hai vị trí đầu-cuối, tỷ lệ phương sai giải thích và khoảng cách trên mặt phẳng PCA |
| 4 | Biểu đồ luồng Sankey | Luồng chuyển nhóm nào phổ biến và bao nhiêu tỉnh giữ nhóm? | Số lượng, tỷ lệ, nhóm đầu-cuối và bảng số liệu thay thế |

Ảnh nên lưu trong `report/img/dynamics_clustering/` với tên `dynamics_province_change.png`,
`dynamics_cluster_profiles.png`, `dynamics_pca_trajectory.png` và
`dynamics_cluster_transitions.png`.

Trong slide 16 trình bày biểu đồ 1-2; slide 17 trình bày biểu đồ 3-4, các kết quả chính và định hướng.
Phải nêu rõ PCA là phép chiếu và các nhóm chỉ mô tả hồ sơ tương đồng. Nhãn nhóm không phải phân loại
chính thức của PAPI và không mang nghĩa tốt hoặc xấu.

### Phần tổng hợp và kết luận

Chỉ viết `\subsection{Tổng hợp các kết quả phân tích chính}` sau khi nhận kết quả đã xác nhận từ Xuân
Trí và Trung Kiên. Phần này liên kết bốn hướng phân tích, không lặp lại toàn bộ số liệu của từng hình.

Hoàn thiện ba mục trong `report/content/05_conclusion.tex`:

- `Các kết quả chính`: dữ liệu PAPI 2011-2024 đã chuẩn hóa; các kết quả phân tích nổi bật; Dashboard
  tương tác; trợ lý AI có bước người dùng xem, yêu cầu sửa và phê duyệt trước khi chạy cục bộ.
- `Hạn chế`: dữ liệu tổng hợp cấp tỉnh; thiếu dữ liệu ở một số tỉnh-năm; D7-D8 chỉ có từ năm 2018;
  các phương pháp liên hệ và phân nhóm chỉ mang tính mô tả; trợ lý AI phụ thuộc dịch vụ mô hình bên ngoài.
- `Hướng phát triển`: cập nhật dữ liệu PAPI mới; bổ sung biến kinh tế - xã hội có nguồn đáng tin cậy;
  đánh giá trải nghiệm người dùng và mở rộng phân tích nhưng vẫn giữ bước phê duyệt của con người.

Đối chiếu thêm `docs/project-status.md`, `docs/dashboard-handoff.md`, các phần 01-04 của báo cáo và
phụ lục trước khi khẳng định kết quả hệ thống. Không đưa số lượng kiểm thử hoặc chi tiết kỹ thuật vào
kết luận nếu chúng không hỗ trợ trực tiếp mục tiêu đồ án.

Trong slide 21 chỉ giữ các kết quả nhóm đạt được; slide 22 nêu 3-5 hạn chế; slide 23 nêu 3-4 hướng
phát triển khả thi; slide 24 là lời cảm ơn ngắn. Tổng phần kết luận nên trình bày trong khoảng hai phút.

## 7. Quy trình kiểm tra trước khi bàn giao

Mỗi thành viên tự kiểm tra phần của mình theo thứ tự:

1. Đọc lại toàn bộ `docs/notes/NOTES.md` và tài liệu thiết kế được chỉ định.
2. Đối chiếu bốn biểu đồ trên Dashboard ở cùng bộ lọc; ghi lại năm, phạm vi, tỉnh hoặc lĩnh vực đang
   chọn và `n` trước khi viết nhận xét.
3. Kiểm tra đủ bốn hình, bốn nhãn, bốn tham chiếu, bốn nhận xét và bốn định hướng trong báo cáo.
4. Biên dịch báo cáo và slide:

```bash
cd report
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

cd ../slides
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

5. Kiểm tra cảnh báo và định dạng:

```bash
rg -n "LaTeX Error|undefined|Overfull|Warning" report/main.log slides/main.log
git diff --check
```

6. Mở hai file PDF để kiểm tra hình không mờ, caption không tràn, tiếng Việt đúng phông và slide có
   thể đọc được khi trình chiếu.
7. Gửi cho Tuấn Anh phần đã viết, các ảnh mới và bộ lọc đã dùng. Không tự sửa phần của thành viên khác,
   không tạo lại dữ liệu và không đưa dữ liệu cá nhân hoặc khóa API vào repository.

## 8. Tài liệu nguồn chung

- `docs/notes/NOTES.md`: quy định trình bày báo cáo và slide.
- `docs/data/README.md`: nguồn sự thật về dữ liệu, phạm vi, dữ liệu thiếu và giới hạn diễn giải.
- `docs/design/README.md`: cấu trúc năm trang và ma trận 20 biểu đồ.
- `docs/design/regional_province.md`: phần của Xuân Trí.
- `docs/design/dimension_relationships.md`: phần của Trung Kiên.
- `docs/design/dynamics_clustering.md`: phần của Đức Phúc.
- `docs/project-status.md`: kết quả hệ thống hiện tại.
- `docs/dashboard-handoff.md`: mạch trình bày và kiểm tra trước khi demo.
- `report/content/03_visual_analysis.tex`: mẫu viết phân tích đã thống nhất.
- `slides/content/5-time-trend.tex`: mẫu bố cục slide phân tích đã thống nhất.
