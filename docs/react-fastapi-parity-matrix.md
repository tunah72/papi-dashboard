# Ma trận parity React + FastAPI

Đây là acceptance source cho migration. Baseline content là Streamlit ở `697f5b2`; mô tả lịch sử không
thay thế cho kiểm thử. Route React dùng FastAPI local và cùng snapshot `data/processed/` với fallback.
**Parity content/numeric không có nghĩa giữ nguyên UX thiếu sót của Streamlit**: các cải tiến UX ở cột
riêng là bắt buộc cho target UI.

## Acceptance chung

- **Numeric/content parity:** cố định fixture/filter, so sánh reference analysis và API mới trên cùng
  snapshot với sai số tuyệt đối `<= 1e-9`. Giữ quy tắc làm tròn hiển thị, tập tỉnh/năm/dimension sau khi
  loại thiếu dữ liệu, và thứ tự score rồi tên tỉnh khi đồng điểm.
- **Semantic view-model:** mọi metric/chart/table trả về hoặc tham chiếu rõ `source`, `unit`, `n` và
  `caveats`; số không hợp lệ là `null`, không phải chuỗi hay `NaN`. UI hiện đủ metadata gần kết quả.
- **Trạng thái:** từng route có loading, empty, error và retry tiếng Việt; error không lộ secret, không
  render KPI/chart từ tập rỗng và không làm hỏng sidebar/điều hướng.
- **Sidebar và responsive:** kiểm tại 1440, 1280, 1024, 900, 768 và 390 px. Năm nhãn target theo thứ tự
  là **Tổng quan; Diễn biến theo thời gian; Vùng & tỉnh; Mối quan hệ lĩnh vực; Thay đổi & phân nhóm**;
  floating AI launcher hiện trên cả năm trang. Active state đúng, URL trực tiếp vẫn có sidebar. Keyboard đi được qua điều hướng/filter/
  chart action, focus-visible rõ và không có horizontal scroll ở bất kỳ viewport nào.
- **AI context:** action giải thích chuyển page, filters, data scope và chart sang Trợ lý AI qua API AI
  local. Không route nào tự chạy code.

| Legacy → target route | Content/numeric phải giữ | Cải tiến UX target bắt buộc | AI context/acceptance riêng |
|---|---|---|---|
| `overview.py` → `/overview` (**Tổng quan**) | Filter phạm vi 6/8 và năm; số tỉnh, mean, min/max, Top/Bottom 10, choropleth và ranking | Map-linked ranking: chọn/hover tỉnh trên map đồng bộ highlight/scroll ranking và ngược lại; metadata source/unit/n/caveat ở map/ranking | `prov_year`, total column, năm, mode, chart; kiểm hai ranking và selection không đổi số liệu |
| `time_trend.py` → `/time-trend` (**Diễn biến theo thời gian**) | Filter 6/8 + range; 4 KPI, endpoints, delta theo dimension, trend, COVID D6/D8, heatmap và drill-down | Dumbbell thay/đi kèm diverging change khi phù hợp; linked selection từ dimension sang trend; caption COVID/missing data và metadata đầy đủ | `prov_year` + `national`, total column, dimensions/range/chart; kiểm heatmap matrix, delta và selection |
| `provincial.py` → `/provincial` (**Vùng & tỉnh**) | Filter 6/8, năm, vùng, tỉnh; mean/spread/rank/benchmark, phân phối vùng và vector profile | Dot plot thay radar để đọc so sánh tỉnh-vùng-toàn quốc chính xác hơn; đổi vùng cập nhật tỉnh/benchmark, metadata đầy đủ | `prov_year` + `national`, năm/mode/vùng/tỉnh; kiểm profile vector và ranking nội vùng |
| `dimension.py` → `/dimension` (**Mối quan hệ lĩnh vực**) | Filter 6/8, năm, cặp X/Y; Pearson r, mean X/Y, n, correlation matrix, scatter quadrant, std theo dimension | Heatmap chỉ đọc lower triangle; click một ô mở/đồng bộ scatter của cặp đó; X/Y luôn khác nhau và metadata đầy đủ | `prov_year`, năm/mode/X/Y/chart; kiểm matrix, pair và scatter selection |
| `dynamics.py` → `/dynamics` (**Thay đổi & phân nhóm**) | Filter 6/8 + hai mốc; delta, thứ tự top/bottom, số profile, KMeans xác định (`random_state=42`) | Hiển thị top/bottom 8 và full table; profile view/hồ sơ A–D thay scatter đơn thuần; hover tỉnh/vùng và metadata đầy đủ | `prov_year`, total column/range/dimensions/chart; kiểm endpoint, delta, cluster assignment/profile |
| `ai_assistant.py` → floating assistant dùng chung | Câu hỏi/context; answer hoặc code/explanation; stdout/result/figure và lifecycle log | Code read-only chờ duyệt; revision tự nhiên sinh full code mới; chỉ proposal mới nhất được phê duyệt; route cũ redirect `/overview?assistant=open` | API AI nhận request/schema/context; API Thực thi chỉ nhận proposal ID đã duyệt; API Logs lưu pending/superseded/approval/execution và bounded artifact |

## Bằng chứng trước cutover

Mỗi trang cần fixture/filter, response reference/API, bảng sai khác numeric, assertion semantic view-model
và test browser cho loading/empty/error/retry, sidebar/keyboard/focus/no-scroll ở sáu viewport. Đính kèm
ảnh hoặc trace chứng minh cải tiến UX target. Trợ lý AI cần log một lần pending không execute và một lần
phê duyệt chạy local, cùng diff/hash-reset và full result log. Chỉ khi toàn bộ bằng chứng đạt mới đổi bề
mặt demo mặc định khỏi Streamlit fallback.
