# Chế độ phóng to biểu đồ

## 1. Mục tiêu

Mọi biểu đồ chính trong năm trang Dashboard phải có **chế độ xem riêng** để người dùng quan sát nhãn,
điểm dữ liệu và interaction ở kích thước lớn hơn. Đây là lớp trình bày của cùng một biểu đồ, không phải
một route phân tích mới và không tạo ra kết quả khác với chart card ban đầu.

Phân biệt hai hành vi:

- **Phóng to biểu đồ:** mở toàn bộ chart card trong popup gần toàn màn hình.
- **Zoom trục dữ liệu:** kéo/chọn một miền trên trục để xem chi tiết; chỉ bật ở biểu đồ có trục liên tục
  và không thay thế nút phóng to.

## 2. Điểm vào trên chart card

Mỗi chart card có một icon button ở góc trên bên phải của header:

```text
┌────────────────────────────────────────────────────────────┐
│ 01 · Nhóm câu hỏi                         [⛶ Phóng to]     │
│ Tiêu đề dưới dạng câu hỏi phân tích                        │
├────────────────────────────────────────────────────────────┤
│                         plot                               │
├────────────────────────────────────────────────────────────┤
│ Insight · ...                                              │
│ Nguồn · đơn vị · n                                         │
└────────────────────────────────────────────────────────────┘
```

- Vùng bấm tối thiểu 44 × 44 px, dùng icon mở rộng nhất quán với hệ icon hiện tại.
- Tooltip và accessible name đều là `Phóng to biểu đồ: {tên biểu đồ}`; không chỉ dùng icon không nhãn.
- Button là tertiary action, nền trong suốt ở trạng thái thường; hover/focus mới hiện nền và border.
- Không đặt button đè lên plot hoặc Plotly modebar. Header luôn chừa một cột control cố định để tiêu đề
  dài không đẩy button xuống hàng riêng.
- Nhấn `Enter` hoặc `Space` khi focus button có cùng hành vi với click.

## 3. Popup mở rộng

### Kích thước và cấu trúc

Popup dùng semantic dialog thay vì Browser Fullscreen API để hành vi ổn định, không xin quyền và vẫn
giữ được navigation của Dashboard.

- Desktop từ 1280 px: rộng `min(94vw, 1600px)`, cao `min(90dvh, 960px)`.
- Tablet 768–1279 px: rộng 96vw, cao 92dvh.
- Mobile dưới 768 px: full-screen `100vw × 100dvh`, không bo góc.
- Backdrop xanh-than 64–72% opacity; blur tối đa 4 px để không cạnh tranh với dữ liệu.
- Z-index dùng token overlay của design system, không đặt giá trị tùy ý.

```text
┌──────────────────────────────────────────────────────────────────────┐
│ 01 · Tiêu đề biểu đồ       Trạng thái đang xem        [Thu nhỏ ✕]   │
├───────────────────────────────────────────────┬──────────────────────┤
│                                               │ Insight              │
│                                               │ Kết luận động...     │
│            plot mở rộng                       ├──────────────────────┤
│                                               │ Chú giải / lựa chọn  │
│                                               ├──────────────────────┤
│                                               │ Nguồn · đơn vị · n   │
│                                               │ Chi tiết phương pháp │
├───────────────────────────────────────────────┴──────────────────────┤
│ Bảng dữ liệu thay thế / hướng dẫn bàn phím trong <details>          │
└──────────────────────────────────────────────────────────────────────┘
```

- Desktop rộng: plot chiếm phần còn lại; rail phải rộng 280–320 px chứa insight, legend/control và
  metadata. Rail không được làm plot hẹp dưới 720 px.
- Khi không đủ 1120 px chiều rộng hữu dụng: chuyển thành một cột; plot ở trên, insight và metadata ở
  dưới. Không tạo cuộn ngang toàn popup.
- Header popup cố định trong dialog khi nội dung cần cuộn. Chỉ body của dialog cuộn.
- Plot mở rộng dùng `ResizeObserver`/Plotly resize sau khi transition hoàn tất để không bị méo hoặc
  giữ kích thước của card cũ.

### Nội dung phải được giữ

Popup không chỉ hiển thị hình vẽ. Nó phải giữ đủ ngữ cảnh để người dùng hiểu biểu đồ độc lập:

- số thứ tự và câu hỏi phân tích;
- đối tượng tỉnh/vùng đang được chọn, nếu có;
- không lặp lại phạm vi, năm và cỡ mẫu ở header popup; các giá trị này đã nằm trong URL, trục và
  metadata của biểu đồ;
- cùng trace, màu, legend, selection, tooltip và guide line với chart card;
- `ChartInsight` động ngay cạnh hoặc ngay dưới plot;
- nguồn PAPI, đơn vị, `n` thực tế, caveat và bảng dữ liệu thay thế.

Không fetch hoặc tính lại một định nghĩa phân tích chỉ vì mở popup. Popup dùng cùng view-model và chart
state với card gốc; việc hover, bật/tắt legend hoặc chọn đối tượng phải đồng bộ hai chiều.

## 4. Hành vi mở, đóng và trạng thái

1. Người dùng click nút phóng to; button phản hồi pressed ngắn trước khi backdrop xuất hiện.
2. Dialog mở trong 200–260 ms bằng opacity và scale nhẹ `0.98 → 1`; nội dung không bay xa khỏi vị trí
   chart vì có thể gây mất định hướng.
3. Focus chuyển vào dialog theo implementation semantic dialog chuẩn.
4. Người dùng đóng bằng một nút `Thu nhỏ ×`, phím `Esc` hoặc Back của trình duyệt nếu URL có
   `focus={chart_id}`.
5. Khi đóng, focus trở lại đúng button đã mở popup và trang giữ nguyên vị trí cuộn.

Click backdrop có thể đóng trên desktop nhưng không phải cách đóng duy nhất. Event từ plot, modebar hoặc
brush/lasso không được lan ra backdrop.

### URL và deep link

- Dùng query param `focus={chart_id}` với ID ổn định, ví dụ `focus=time-regional-yoy`.
- Refresh hoặc mở link có `focus` hợp lệ sẽ mở đúng popup sau khi dữ liệu sẵn sàng.
- `focus` không thay thế các param `scale`, `year`, `region`, `province`, `dimension` hiện có.
- ID không hợp lệ được bỏ qua và thông báo nhẹ; không biến cả trang thành error state.

## 5. Interaction trong popup

- Tooltip, hover-dim, unified guide, click selection và legend toggle hoạt động như chart card.
- Tăng không gian không đồng nghĩa tăng số trace/annotation; giữ cùng dữ liệu để tránh thay đổi câu trả
  lời khi chuyển chế độ.
- Chart có trục liên tục có thể bật zoom/pan/reset phù hợp. Choropleth dùng pan/zoom bản đồ; radar,
  Sankey và 100% stacked bar chỉ cần focus mode nếu axis zoom không có ý nghĩa.
- Modebar chỉ hiện các action đã duyệt: zoom/pan/select/reset/download nếu sản phẩm cho phép. Loại bỏ
  action không dùng để giảm nhiễu.
- Nút `Đặt lại góc nhìn` chỉ reset viewport của biểu đồ, không xóa page filter hoặc selection.
- Không tự mở AI, tự tạo insight bằng AI hoặc chạy code khi người dùng phóng to biểu đồ.

## 6. Accessibility

- Dialog có `role="dialog"`, `aria-modal="true"`, `aria-labelledby` trỏ tới tiêu đề và
  `aria-describedby` trỏ tới phụ đề/insight ngắn.
- Giữ focus trong dialog; nội dung nền là `inert` trong lúc popup mở.
- Có một nút đóng gồm chữ `Thu nhỏ` và ký hiệu `×`, không tạo hai action trùng chức năng.
- Thứ tự tab: đóng/thu nhỏ → chart controls → legend/control thay thế → bảng/details.
- Chart vẫn phải có bảng dữ liệu hoặc control tương đương cho người dùng bàn phím; tooltip không phải
  kênh duy nhất chứa số liệu.
- Ở zoom trình duyệt 200%, dialog reflow thành một cột và không che nút đóng.
- Với `prefers-reduced-motion`, bỏ scale; chỉ dùng fade ngắn hoặc mở ngay.

## 7. Trạng thái biên

- **Loading:** popup có skeleton đúng vùng plot và giữ header/close dùng được.
- **Empty:** giữ popup, giải thích filter nào làm không còn dữ liệu và cung cấp `Đặt lại bộ lọc`.
- **Error:** thông báo lỗi trong body, có `Thử lại`; nút đóng luôn hoạt động.
- **Partial data:** vẫn vẽ chart, hiển thị `n` và caveat như card gốc.
- **Route/filter đổi:** nếu chart vẫn hợp lệ, cập nhật popup tại chỗ; nếu không còn tồn tại, đóng popup
  có thông báo `Biểu đồ không còn phù hợp với bộ lọc mới`.

## 8. Yêu cầu component

Nên triển khai một contract dùng chung thay vì tạo popup riêng ở từng page:

```ts
type ChartFocusProps = {
  chartId: string;
  title: string;
  insight: string;
  activeContext?: string;
  metadata: ChartMetadata;
  children: React.ReactNode;
};
```

- `ChartCard` render `ChartFocusTrigger` và truyền cùng chart content/state vào `ChartFocusDialog`.
- Dialog được lazy-mount khi mở nhưng không tạo thêm API request nếu dữ liệu đã có.
- Mỗi lần chỉ có một chart focus; chuyển `focus` phải đóng sạch listener/Plotly instance cũ.
- Dùng portal tại app shell và dialog primitive hiện có nếu dự án đã có; không tự viết focus trap mới
  nếu thư viện UI hiện tại cung cấp primitive đạt accessibility.

## 9. Acceptance criteria

- Cả 20 chart card có button phóng to ở cùng một vị trí và accessible name cụ thể.
- Popup hiển thị đúng chart, filter, insight, nguồn, đơn vị và `n` của card đã mở.
- Selection/legend/viewport hợp lệ được giữ khi mở và đóng; không fetch dữ liệu trùng lặp.
- `Esc`, nút đóng, Back và focus return hoạt động; body phía sau không cuộn khi dialog mở.
- Không overflow ở 1440 × 900, 1024 × 768, 768 × 1024 và 390 × 844; kiểm tra zoom 200%.
- Loading, empty, error, partial data và deep link `focus` đều có test.
- Mở popup không chạy code AI, không đổi dữ liệu và không tạo insight khác với chart gốc.
