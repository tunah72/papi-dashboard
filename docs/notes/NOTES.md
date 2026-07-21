# Ghi chú và Quy luật Định dạng (Báo cáo & Slides)

Tài liệu này tổng hợp các quy luật định dạng, cấu trúc, phong cách thiết kế và văn phong được áp dụng thống nhất trong toàn bộ mã nguồn LaTeX của **Báo cáo (Report)** và **Slides (Beamer)** của đồ án. Khi viết hoặc chỉnh sửa tài liệu, cần tuân thủ nghiêm ngặt các quy luật này.

---

## Về báo cáo

### 1. Bố cục & Thiết lập trang
* **Thụt dòng**: Không thụt đầu dòng đối với các đoạn văn mới (`\setlength{\parindent}{0pt}`).
* **Giãn dòng**: Sử dụng giãn dòng 1.5 (`\renewcommand{\baselinestretch}{1.5}`).
* **Các danh mục bắt buộc**:
  * Phải có Danh sách bảng (`\listoftables`) và Danh sách hình vẽ (`\listoffigures`).
  * Phải có Bảng thuật ngữ tiếng Anh - tiếng Việt (`content/glossary.tex`).
* **Giới hạn dung lượng**: Báo cáo chính không vượt quá 30 trang (không bao gồm phần phụ lục) và khoảng 7000 từ để đảm bảo tính súc tích, cô đọng.

### 2. Định dạng Bảng biểu (Tables)
* **Kiểu bảng**: Bắt buộc sử dụng gói `booktabs` với các lệnh kẻ ngang chuyên dụng: `\toprule` (đường kẻ đậm trên cùng), `\midrule` (đường kẻ phân cách), `\bottomrule` (đường kẻ đậm dưới cùng).
* **Đường kẻ dọc**: Tuyệt đối không sử dụng đường kẻ dọc trong bất kỳ bảng nào.
* **Tiêu đề cột (Header)**: Phải được in đậm (`\textbf{...}`).
* **Chú thích bảng (Caption)**:
  * Chú thích phải nằm **phía trên** bảng biểu.
  * Khoảng cách caption của bảng thiết lập là 0.2cm (`\captionsetup[table]{skip=0.2cm}`).
* **Giãn dòng trong bảng**: Thiết lập khoảng cách giữa các hàng là 1.3 (`\renewcommand{\arraystretch}{1.3}`).
* **Tự động điều chỉnh kích thước**: Với bảng có dữ liệu rộng, sử dụng `\resizebox{\textwidth}{!}{...}` hoặc gói `tabularx` để tự động xuống dòng và co dãn cột cho khít trang.

### 3. Định dạng Hình vẽ & Sơ đồ (Figures)
* **Đặt trong môi trường**: Mọi hình ảnh phải đặt trong môi trường `figure` kèm theo căn giữa (`\centering`).
* **Chú thích hình (Caption)**: Chú thích phải nằm **phía dưới** hình vẽ.
* **Khoảng cách caption**: Khoảng cách caption của hình thiết lập là 0.2cm (`\captionsetup[figure]{skip=0.2cm}`).
* **Định vị hình vẽ**: Sử dụng các tùy chọn định vị vị trí linh hoạt `[htbp]` hoặc `[H]` (yêu cầu gói `float`) để tránh lỗi trôi hình.
* **Hình ảnh con**: Để hiển thị nhiều ảnh con cạnh nhau, sử dụng môi trường `subfigure` (ví dụ: `\begin{subfigure}[b]{0.48\textwidth}`).
* **Ảnh do AI tạo**: Tuyệt đối không được sử dụng ảnh do AI sinh ra.
* **Tham chiếu**: Mọi hình vẽ, bảng biểu phải được đánh nhãn `\label{fig:...}` hoặc `\label{tab:...}` và được tham chiếu trong nội dung văn bản (ví dụ: `Hình~\ref{fig:...}`, `Bảng~\ref{tab:...}`).
* **Sơ đồ quy trình (TikZ)**: Các sơ đồ luồng dữ liệu, pipeline nên được vẽ trực tiếp bằng TikZ (`\begin{tikzpicture}`) để giữ độ phân giải vector cao. Sử dụng các khối định dạng phong cách thống nhất như đã cấu hình trong [main.tex](../../report/main.tex#L17-L29) (`base`, `step1`, `step2`...).

### 4. Công thức Toán học
* **Đánh số**: Các công thức toán chính thức cần được trình bày trong môi trường `equation` để đánh số tự động.
* **Dấu câu sau công thức**: Nếu công thức nằm ở giữa câu và câu chưa kết thúc, cần thêm dấu phẩy `,` ở cuối công thức. Nếu công thức nằm ở cuối câu kết thúc đoạn, cần chèn dấu chấm `.` ở cuối công thức.
* **Viết biến số**: Các ký hiệu toán học, biến số phải được đưa vào môi trường toán học (ví dụ: ảnh `$I \in \mathbb{R}^{H \times W \times 3}$`, nhãn lớp `$c_k$`).

### 5. Định dạng Danh sách & Văn bản
* **Ký hiệu danh sách**: Thay đổi ký hiệu đầu dòng của danh sách không đánh số (`itemize`) thành dấu gạch ngang ngắn bằng lệnh `\renewcommand{\labelitemi}{\textendash}`.
* **Dấu gạch ngang**: Phải sử dụng dấu gạch ngang ngắn `-` hoặc `\textendash`, tránh dùng dấu gạch ngang dài `—` hoặc `--`.
* **Trích dẫn khoa học**: Trích dẫn đầy đủ nguồn tài liệu, bài báo và kiến trúc mô hình gốc bằng lệnh `\cite{...}` (ví dụ: `\cite{he2017mask}`).
* **Số thập phân**: Đối với văn bản tiếng Việt, số thập phân dùng dấu phẩy `,` (ví dụ: `97,93\%`, `0,75`), ngoại trừ khi viết mã lệnh hoặc công thức toán học (dùng dấu chấm `.`).

### 6. Văn phong & Thuật ngữ
* **Văn phong**: Trang trọng, khoa học, khách quan và súc tích.
* **Thuật ngữ Tiếng Anh**: Không mở ngoặc giải thích thuật ngữ tiếng Anh đi kèm đằng sau thuật ngữ tiếng Việt nếu thuật ngữ đó đã xuất hiện trước đó (chỉ mở ngoặc ở lần xuất hiện đầu tiên). Ví dụ: `phân vùng thực thể (instance segmentation)`.
* **Định dạng thuật ngữ**: In nghiêng các thuật ngữ chuyên ngành tiếng Anh chưa dịch nghĩa bằng lệnh `\textit{...}`.

---

## Về slides

### 1. Bố cục & Thiết lập Trang (Layout & Theme)
* **Tỉ lệ slide**: Sử dụng tỷ lệ khung hình chuẩn màn hình rộng 16:9 (`\documentclass[aspectratio=169]{beamer}`).
* **Trình biên dịch & Phông chữ**: Sử dụng trình biên dịch `pdflatex` (thay vì `XeTeX` hay `XeLaTeX`). Thiết lập phông chữ tiếng Việt chuẩn thông qua gói `\usepackage[utf8]{inputenc}` và `\usepackage[T5]{fontenc}`.
* **Theme chính**: Sử dụng Beamer theme `Madrid`, inner theme `circles`, và tắt các ký hiệu điều hướng mặc định (`\setbeamertemplate{navigation symbols}{}`).
* **Hệ màu chủ đạo (Màu thương hiệu)**: Cấu hình hệ màu nhận diện thống nhất dựa trên hai màu chính:
  * `Logo1` (Xanh lá đậm - mã HTML `#1B5E20`).
  * `Logo2` (Nâu đất - mã HTML `#3E2723`).
  * Palette primary, secondary, structure được ánh xạ trực tiếp từ hai màu này.
* **Tiêu đề tự động**: Hệ thống đã được thiết lập tự động chèn tên của `subsection` làm tiêu đề slide (`frametitle`) trong trường hợp slide không được khai báo tiêu đề thủ công.
* **Mục lục phân mục**: Tự động hiển thị slide Mục lục đánh dấu phân mục hiện tại mỗi khi bắt đầu một `section` mới (`\AtBeginSection[]{...}`). Có thể tắt bằng cách gán `\boolfalse{showtocatsection}`.

### 2. Trình bày văn bản (Typography)
* **Căn đều hai bên**: Tự động căn đều hai bên (`\justifying`) đối với toàn bộ khối văn bản trong slide thông qua các lệnh vá cấu hình trong [preamble/settings.tex](../../slides/preamble/settings.tex#L34-L39).
* **Cấu trúc cột (Columns)**: Sử dụng môi trường `columns` với định vị `[T]` để chia slide thành 2 cột cân đối (độ rộng thông dụng: `0.48\textwidth` hoặc `0.45\textwidth` / `0.51\textwidth`).
* **Tiêu đề cột**: Phải được căn giữa và in đậm bằng lệnh `\centerline{\textbf{...}}`.
* **Hạn chế chữ**: Slides phải tối giản, súc tích, chỉ chứa từ khóa chính, sơ đồ và thông tin tóm tắt có liên quan từ báo cáo.
* **Thuật ngữ**: Chỉ sử dụng tiếng Việt trừ các thuật ngữ tiếng Anh không có bản dịch phổ biến. Tuân thủ quy tắc không dịch/giải thích lặp lại nhiều lần.
* **Kích thước định nghĩa & công thức**: Các câu định nghĩa dài hoặc biểu diễn toán học nên được rút gọn hoặc giảm cỡ chữ phù hợp (`\small` hoặc `\footnotesize`) để hiển thị trọn vẹn trên một dòng, tránh xuống dòng lẻ loi.
* **Dấu gạch ngang & Chữ đậm**: Dùng gạch ngang ngắn `-`. Không in đậm/in nghiêng tùy tiện, đặc biệt là không in đậm các từ khóa trước dấu hai chấm của các mục liệt kê.

### 3. Danh sách (Lists)
* **Hạn chế bullet points**: Hạn chế lạm dụng danh sách liệt kê tròn mặc định. Thay vào đó nên sử dụng danh sách liệt kê dấu gạch ngang đơn giản `\item[-]` không dùng box để slide trông thoáng rộng hơn.
* **Độ giãn dòng danh sách**: Sử dụng lệnh `\setlength{\itemsep}{1pt}` (hoặc `8pt` tùy độ dày thông tin) để điều chỉnh khoảng cách giữa các mục cho thoáng mắt.
* **Khối hộp màu (Blocks)**: Không lạm dụng các khối hộp màu (`block`, `exampleblock`) cho định nghĩa hay đoạn văn thông thường; chỉ sử dụng box cho công thức toán học hoặc những điểm cực kỳ quan trọng cần gây chú ý.

### 4. Bảng biểu trong Slide (Tables)
* **Cỡ chữ & Khoảng cách**: Bảng biểu trong slide cần được co nhỏ cỡ chữ (`\footnotesize` hoặc `\scriptsize`) và giảm khoảng cách cột (`\setlength{\tabcolsep}{5pt}` hoặc `3pt`) để đảm bảo không tràn lề.
* **Cấu trúc**: Tuân thủ định dạng bảng không có đường kẻ dọc, sử dụng `booktabs` (`\toprule`, `\midrule`, `\bottomrule`).
* **Vị trí caption**: Chú thích bảng phải nằm ở phía **trên** bảng.

### 5. Hình vẽ & Sơ đồ trong Slide (Figures)
* **Môi trường & Căn giữa**: Hình minh họa hoặc sơ đồ phải được đặt trong môi trường `figure`, căn giữa, có chú thích `\caption{...}` hoặc `\captionof{figure}{...}` nằm **phía dưới** hình vẽ.
* **Màu sắc sơ đồ**: Màu sắc của các sơ đồ (ví dụ: hình vẽ TikZ, biểu đồ vẽ tay) phải đồng bộ với màu chủ đạo của slide (ưu tiên sử dụng màu thương hiệu `Logo1!10`, `Logo2!10` thay vì màu mặc định của thư viện như `blue!10`).
* **Nhóm hình ảnh**: Khi xếp nhiều ảnh con cạnh nhau, dùng môi trường `minipage` bên trong `figure` và chú thích không đánh số bằng `\caption*{...}`.

### 6. Công thức toán học
* **Đánh số**: Các công thức toán hiển thị trong slide được đánh số tự động (`\setbeamertemplate{equations}[numbered]`).
* **Môi trường**: Trình bày trong môi trường `equation` hoặc dấu đô la kép `$$...$$` khi muốn xuống dòng, canh giữa.
