# Hệ layout, chart card và interaction

## 1. Hướng thẩm mỹ

Phong cách: **civic editorial** — nghiêm túc, dễ tin cậy, nhiều khoảng thở nhưng vẫn đủ mật độ cho
phân tích dữ liệu. Giao diện dùng nền xanh-xám rất nhạt, mặt phẳng trắng, chữ xanh than và một accent
teal. Không dùng gradient tím/xanh kiểu sản phẩm AI, shadow đậm hoặc hiệu ứng trang trí cạnh tranh với
dữ liệu.

Be Vietnam Pro tiếp tục là font chính vì hỗ trợ tiếng Việt tốt và đã có trong sản phẩm. KPI, bảng và
tooltip bật `font-variant-numeric: tabular-nums`. Sự khác biệt đến từ phân cấp chữ, khoảng trắng, hệ
màu PAPI và composition; không thêm font chỉ để trang trí.

## 2. Khung desktop

### Kích thước

- Viewport mục tiêu: từ 1280 px; kiểm tra chuẩn ở 1440 × 900.
- Sidebar desktop: 248 px, có thể thu gọn còn 72 px.
- Vùng nội dung: `minmax(0, 1440px)`, căn giữa.
- Padding ngang: 32–48 px tùy chiều rộng.
- Grid: 12 cột, gutter 20 px.
- Bốn biểu đồ: hai hàng, mỗi card chiếm 6 cột.
- Khoảng cách dọc giữa các lớp: 12 / 16 / 20 / 24 / 32 px; không đặt nhiều khoảng 40–60 px liên tiếp.

### Thứ tự và chiều cao

| Lớp | Chiều cao mục tiêu | Ghi chú |
|---|---:|---|
| Page header | 72–88 px | Tiêu đề tối đa 2 dòng; mô tả 1 dòng trên desktop |
| Filter bar | 64–72 px | Một hàng; trạng thái chọn hiển thị rõ |
| KPI strip | 88–96 px | Bốn card bằng nhau |
| Khoảng trước chart | 20–24 px | Không thêm callout insight toàn trang |
| Chart card | 500–540 px | Hai card cùng hàng cao bằng nhau |
| Plot viewport | 300–340 px | Không tính header, insight và metadata |

Mục tiêu là chart grid bắt đầu khoảng `y = 300–340` ở 1440 × 900. Chart chính không được nằm sau một
khối mô tả dài hoặc bộ lọc cao hơn 100 px.

### Wireframe chung

```text
┌───────────────────────────────────────────────────────────────────────┐
│ Tên trang + mô tả ngắn                                             │
├───────────────────────────────────────────────────────────────────────┤
│ Filter 1  Filter 2  Filter 3              Đang xem: ...   Đặt lại    │
├──────────────┬──────────────┬──────────────┬─────────────────────────┤
│ KPI 1        │ KPI 2        │ KPI 3        │ KPI 4                   │
├────────────────────────────────┬──────────────────────────────────────┤
│ Chart 01                       │ Chart 02                             │
│ [header]                 [⛶]  │ [header]                       [⛶]  │
│ [plot khoảng 320 px]           │ [plot khoảng 320 px]                 │
│ Insight: ...                   │ Insight: ...                         │
│ Nguồn · đơn vị · n             │ Nguồn · đơn vị · n                   │
├────────────────────────────────┼──────────────────────────────────────┤
│ Chart 03                       │ Chart 04                             │
│ ...                            │ ...                                  │
└────────────────────────────────┴──────────────────────────────────────┘
```

## 3. Page header và filter

- Bỏ breadcrumb dài và badge lặp lại khoảng năm nếu sidebar đã thể hiện route.
- Eyebrow chỉ dùng cho tên nhóm trang, không nhắc lại tiêu đề.
- Mô tả trang tối đa 100–120 ký tự, nói người dùng sẽ trả lời câu hỏi gì.
- Filter page-level đặt trên một hàng và không sticky mặc định.
- Trạng thái lựa chọn dùng văn bản/chip rõ: `Đang xem: 6 lĩnh vực · 2011–2024 · Toàn quốc`.
- Nút `Đặt lại` là secondary action, chỉ bật khi filter khác mặc định.
- Filter riêng một chart đặt trong header của chính card, không chen vào filter toàn trang.
- Khi đổi phạm vi 6/8 lĩnh vực, năm không hợp lệ được điều chỉnh và thông báo bằng `aria-live`.

## 4. KPI cards

- Mỗi trang dùng bốn KPI thực sự hỗ trợ bốn biểu đồ, không lặp nguyên con số trong page header.
- Tất cả KPI card dùng cùng bề mặt trung tính; không dùng border màu ngẫu nhiên ở một vài card.
- Tăng/giảm dùng đồng thời: mũi tên hoặc dấu `+/-`, nhãn `Tăng/Giảm`, và màu semantic.
- Không dùng thuật ngữ `YoY`; viết `so với năm trước`.
- Giá trị thiếu hiển thị `—` và giải thích `Không đủ dữ liệu`, không dùng 0.
- Tên KPI dùng ngôn ngữ tự nhiên, ví dụ `Mức thay đổi trong giai đoạn`, `Năm biến động mạnh nhất`.

## 5. Anatomy của chart card

```text
01 · Nhóm câu hỏi
Tiêu đề dưới dạng câu hỏi phân tích
[plot]

Insight  Câu trả lời động ngắn, có số liệu và đối tượng cụ thể.
Nguồn: PAPI · Đơn vị: ... · n = ... · Lưu ý phương pháp
```

### Header

- Tiêu đề là câu hỏi mà chart trả lời, không phải tên kỹ thuật như “Biểu đồ cột”.
- Không hiển thị dòng hướng dẫn cách đọc hoặc diễn giải encoding trong chart card. Tooltip, nhãn trục,
  legend và bảng dữ liệu thay thế phải tự cung cấp ngữ cảnh cần thiết.
- Không lặp phạm vi, năm và `n` cạnh tiêu đề trang khi các giá trị này đã hiện rõ trong filter; `n`
  vẫn phải xuất hiện ở metadata của biểu đồ vì đó là thông tin phương pháp.
- Control của chart căn góc phải, vùng bấm tối thiểu 44 × 44 px.
- Mỗi card luôn có button `Phóng to biểu đồ` ở góc phải header. Button mở chế độ xem riêng theo
  [`chart_focus_mode.md`](chart_focus_mode.md), không đặt đè lên plot hoặc modebar.

### Insight dưới biểu đồ

Tạo component `ChartInsight` hoặc prop `insight` của `ChartCard` và đặt ngay sau plot, trước metadata.

- Một câu, tối đa khoảng 140 ký tự hoặc hai dòng ở card 6 cột.
- Bắt đầu bằng kết luận, sau đó là số liệu: `Đồng bằng sông Hồng dẫn đầu với 44,3 điểm, cao hơn Tây
  Nguyên 3,1 điểm.`
- Dùng dữ liệu theo filter hiện tại, không dùng câu cố định từ EDA.
- Với dữ liệu thiếu: `Không đủ hai mốc để tính thay đổi cho 2 tỉnh; các tỉnh này không được xếp hạng.`
- Với tương quan/phân cụm, thêm qualifier ngắn: `r = 0,72, là liên hệ quan sát chứ không phải nhân quả.`
- Insight không được do AI tự sinh trong luồng Dashboard. Floating launcher mở Trợ lý AI với context
  trang hiện tại; code vẫn chờ người dùng duyệt.

### Metadata

- Luôn có nguồn, đơn vị, `n` thực tế và caveat dữ liệu thiếu.
- Metadata chữ nhỏ hơn insight nhưng đạt tương phản WCAG AA.
- Chi tiết phương pháp dài nằm trong `<details>`, không làm card cao thêm ở trạng thái đóng.

## 6. Màu và mã hóa

- Dùng token hiện có trong `chartTheme.ts`; không hard-code màu trong page.
- Mỗi lĩnh vực giữ một màu cố định trên mọi trang.
- Mỗi vùng giữ một màu cố định khi cần phân biệt sáu vùng.
- Sequential scale chỉ dùng cho mức điểm thấp → cao.
- Diverging scale có tâm 0 cho thay đổi và tâm phù hợp cho tương quan.
- Tăng/giảm không chỉ dựa vào xanh/đỏ: thêm dấu, hướng thanh, ký hiệu hoặc nhãn trực tiếp.
- Chuỗi không được chọn dùng xám 30–45% opacity; chuỗi active dùng màu và width lớn hơn.
- Dữ liệu thiếu dùng xám nhạt và pattern/nhãn `Thiếu dữ liệu`, không đưa vào thang màu điểm.

## 7. Interaction thống nhất

### Hai mức tương tác

1. **Hover tạm thời:** highlight local, tooltip và vertical/cross guide; không gọi API hay làm layout
   nhảy.
2. **Click cam kết:** chọn tỉnh/vùng/lĩnh vực/profile, cập nhật URL và cross-filter các chart liên quan.

### Hành vi bắt buộc

- Tooltip tiếng Việt gồm đối tượng, thời gian, giá trị, đơn vị, `n` nếu có và chênh lệch liên quan.
- Hover một series làm đậm series đó và giảm opacity series khác.
- Click legend ẩn/hiện series; double-click cô lập series theo quy ước Plotly.
- Selection luôn có biểu hiện ngoài màu: stroke, marker lớn hơn, ký hiệu hoặc nhãn `Đang chọn`.
- `Esc` bỏ chọn cục bộ; `Đặt lại` xóa toàn bộ filter trang.
- Click một chart không tự cuộn trang hoặc thay đổi chiều cao card.
- Mở popup phóng to giữ nguyên filter, selection, legend và insight; đóng popup trả focus về button đã
  mở và giữ vị trí cuộn của trang.
- Drill-through giữ `scale`, `year/from/to`, `region`, `province`, `dimension` phù hợp trong URL.
- Animation chỉ dùng opacity/transform 160–240 ms; tắt theo `prefers-reduced-motion`.

### Contract component hiện tại

`CartesianChart` hỗ trợ `onClick`, `onHover`, `onUnhover`, `onSelected`, Plotly config, fallback table
và mô tả figure cho screen reader. Page chỉ truyền các callback thật sự cần dùng; brush/lasso và
modebar chỉ bật ở dạng biểu đồ có acceptance rõ.

`ChartFocusDialog` dùng chung đồng bộ chart state và URL `focus={chart_id}`.

Sankey nên có component/bundle riêng để không làm bundle Cartesian của mọi trang nặng hơn.

## 8. Accessibility

- Mọi control dùng semantic button/select/label, focus ring nhìn rõ và thứ tự tab theo luồng đọc.
- Chart click phải có control hoặc bảng tương đương cho bàn phím.
- Mỗi figure có tên, mô tả, insight và bảng tóm tắt trong `<details>`.
- Tooltip không phải kênh duy nhất chứa dữ liệu quan trọng.
- Text và UI đạt WCAG 2.1 AA; nét/marker active không nhỏ hơn 2 px/8 px.
- Không dùng font dưới 12 px cho nội dung chart và 11 px cho metadata.
- Khi filter thay đổi, công bố trạng thái bằng `aria-live="polite"`, không tự chuyển focus.

## 9. Responsive và trạng thái

- Từ 1280 px: grid 2 × 2.
- 900–1279 px: một cột hoặc 7/5 chỉ khi chart vẫn đọc được; ưu tiên một cột hơn nhãn bị cắt.
- Dưới 900 px: một cột, chart cao 320–380 px, control xuống dòng; không cuộn ngang toàn trang.
- Popup phóng to dùng gần toàn viewport trên desktop và full-screen trên mobile; khi thiếu chiều rộng,
  rail insight/metadata chuyển xuống dưới plot thay vì tạo overflow ngang.
- Loading dùng skeleton giữ đúng chiều cao page header, KPI và bốn card để tránh layout shift.
- Empty state nằm trong card bị ảnh hưởng; không xóa ba chart còn dữ liệu.
- Error page-level có thông báo nguyên nhân, `Thử lại` và `Đặt lại bộ lọc`.
- Partial data hiển thị chart với caveat và `n`, không biến toàn trang thành lỗi.

## 10. Kiểm tra trực quan bắt buộc khi triển khai

- 1440 × 900: first-fold, alignment hai card, tooltip, legend, insight hai dòng.
- 1280 × 800: không cắt nhãn và filter không cao quá hai hàng.
- 1024 × 768: một cột hợp lý, không overflow ngang.
- Keyboard-only: filter, legend thay thế, chart selection, details table và reset.
- Focus mode: mở từng chart, `Esc`/Back/nút đóng, focus trap/return, khóa cuộn nền và deep link.
- `prefers-reduced-motion`, zoom 200% và high-contrast mode.
- Loading, empty, error, thiếu dữ liệu và selection từ URL.
