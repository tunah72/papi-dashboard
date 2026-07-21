# Thiết kế hoàn tất H2 — So sánh tỉnh và vùng

## Mục tiêu

Hoàn tất vertical slice của Lê Xuân Trí trên nền `main`: H2 có dữ liệu thật, các biểu đồ theo phân công, tương tác drill-down, logic thuần có test, context cho AI Assistant và bằng chứng để trình bày/vấn đáp.

## Phạm vi

- Giữ `app/pages/provincial.py` và `src/analysis/provincial.py` là implementation duy nhất.
- Port chọn lọc hành vi có giá trị từ `feature/task/Tri`: map tổng điểm, top/bottom tỉnh, outlier z-score và thay đổi giữa hai mốc.
- Giữ phần benchmark vùng/radar đang có trên `main`.
- Bổ sung tương tác chọn tỉnh từ choropleth, với selectbox dự phòng khi chưa có selection.
- Bổ sung unit test H2 và AppTest/smoke test có dữ liệu thật.
- Cập nhật section H2 của report, trạng thái và roadmap sau khi tính lại số liệu từ processed data.

## Ngoài phạm vi

- Không merge/cherry-pick commit `90da9f9`.
- Không đổi `app/pages/ai_assistant.py`, `app/ai/api_logs.py` hoặc executor AI.
- Không thay đổi pipeline/raw data, palette/theme hay public signature trong `app/lib/`.

## Thiết kế H2

### Câu hỏi phân tích

1. Trong cùng một năm và cùng thang đo, khoảng cách điểm giữa tỉnh/vùng cao và thấp là bao nhiêu?
2. Tỉnh nào có điểm khác thường so với phân bố tỉnh trong cùng năm, nhưng không suy diễn nguyên nhân?
3. Giữa hai mốc hợp lệ, tỉnh nào tăng/giảm mạnh nhất trong nhóm có dữ liệu đủ ở cả hai mốc?

### Contract dữ liệu và tương tác

1. Control bar chung chọn phạm vi 6/8 lĩnh vực, năm snapshot và hai mốc thời gian hợp lệ.
   `total_papi_6dim` chỉ dùng để so sánh liên tục 2011–2024; `total_papi` chỉ dùng từ 2018–2024.
   Không đặt hai tổng vào cùng một ranking, slopegraph hoặc kết luận.
2. Snapshot năm dùng duy nhất `prov_year`, loại điểm thiếu và luôn ghi số tỉnh thật.
3. Map choropleth vẽ tổng điểm theo thang đang chọn. `st.plotly_chart(..., on_select="rerun", selection_mode="points")` cập nhật tỉnh đang drill; selectbox vẫn là fallback rõ ràng.
4. Xếp hạng top/bottom toàn snapshot, boxplot theo vùng, summary vùng và z-score chỉ mô tả phân bố — không suy ra nguyên nhân. Outlier dùng z-score trong cùng năm, độ lệch chuẩn mẫu `ddof=1`, ngưỡng `|z| > 2`.
5. Slopegraph hiển thị nhóm tỉnh tăng/giảm mạnh nhất giữa hai mốc; chỉ dùng tỉnh có đủ cả hai mốc.
6. Drill-down tỉnh giữ ranking trong vùng, benchmark vùng/toàn bộ snapshot và radar lĩnh vực cùng năm/cùng thang đo.
7. `dash_context` phải chứa thang đo, năm, vùng, tỉnh, cột điểm, hai mốc và chart context để AI chỉ đề xuất theo phạm vi người dùng đang xem.

### Quy ước trực quan và nguồn

- Mỗi chart dùng palette/nhãn từ `config`, primitive `charts` hoặc `charts.apply_owid`, nguồn PAPI và ghi chú số tỉnh có dữ liệu.
- Không nội suy dữ liệu thiếu. UI không hiển thị mã D1–D8 khi có tên lĩnh vực đầy đủ.
- Tiêu đề và insight lấy số từ DataFrame tại lần render, dùng diễn đạt trung tính và không suy nguyên nhân từ outlier/chênh lệch.

## Ranh giới module

- `src/analysis/provincial.py`: snapshot, summary vùng, ranking/top-bottom, z-score, pair hai mốc, benchmark/profile. Không import Streamlit/Plotly và không đọc file.
- `app/pages/provincial.py`: controls, state selection, chart composition và narrative bám số liệu.
- `tests/test_provincial.py`: test behavior/edge case của từng helper.
- `tests/test_provincial_page.py`: AppTest boot/filter/selection fallback, không gọi LLM hay dữ liệu raw.
- `app/ai/techniques/anomaly.py`: không đổi contract registry; test/kiểm tra prompt để đảm bảo dùng score người dùng chỉ định, `.copy()` sau lọc, `result` và `fig` đúng giao kèo AI.

## Tiêu chí hoàn thành

- H2 có header, KPI, map, ranking top/bottom, boxplot vùng, slopegraph, outlier, radar/benchmark và nguồn/dữ liệu thiếu rõ ràng.
- Mọi kết luận lấy giá trị từ DataFrame trong lần render; không hard-code insight/số liệu.
- Có click-to-drill trên map và fallback selectbox.
- Test matrix gồm 6/8 lĩnh vực, năm có thiếu dữ liệu, vùng rỗng, không có outlier, tỉnh thiếu một mốc, selection event rỗng và click hợp lệ trên GeoJSON đã chuẩn hoá 63 ID.
- Unit test, AppTest, `pytest -q`, Streamlit smoke test 6/8 lĩnh vực và kiểm tra plugin anomaly theo manual test đều đạt trong môi trường dự án.
- Báo cáo H2 dùng số tái tạo được; docs trạng thái khớp code/test.

## Bằng chứng và cập nhật tài liệu

Completion cần có output pytest/AppTest, smoke test H2 ở hai thang đo, ảnh H2, bảng hoặc script tái tạo số report, diff sạch và review PR. Chỉ sau khi các bằng chứng này có thật mới cập nhật `project-status.md`, `roadmap.md`, `architecture.md`, `guides/team-guide.md` và thêm link design vào `docs/README.md`.

## Rủi ro và giảm thiểu

- Selection API Streamlit có thể khác AppTest: guard event rỗng, fallback selectbox, test riêng hành vi pure helper.
- Thiếu dữ liệu theo năm/thang: snapshot/slope/profile phải trả rỗng có thông báo, không index dòng đầu.
- Khác biệt với nhánh cũ: chỉ port theo test/contract đã chốt, không copy nguyên file.
