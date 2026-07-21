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

1. Control bar chung chọn phạm vi 6/8 lĩnh vực, năm snapshot và hai mốc thời gian hợp lệ.
2. Snapshot năm dùng duy nhất `prov_year`, loại điểm thiếu và luôn ghi số tỉnh thật.
3. Map choropleth vẽ tổng điểm theo thang đang chọn. `st.plotly_chart(..., on_select="rerun", selection_mode="points")` cập nhật tỉnh đang drill; selectbox vẫn là fallback rõ ràng.
4. Xếp hạng top/bottom toàn snapshot, boxplot theo vùng, summary vùng và z-score chỉ mô tả phân bố — không suy ra nguyên nhân.
5. Slopegraph hiển thị nhóm tỉnh tăng/giảm mạnh nhất giữa hai mốc; chỉ dùng tỉnh có đủ cả hai mốc.
6. Drill-down tỉnh giữ ranking trong vùng, benchmark vùng/toàn bộ snapshot và radar lĩnh vực cùng năm/cùng thang đo.
7. `dash_context` phải chứa thang đo, năm, vùng, tỉnh, cột điểm, hai mốc và chart context để AI chỉ đề xuất theo phạm vi người dùng đang xem.

## Ranh giới module

- `src/analysis/provincial.py`: snapshot, summary vùng, ranking/top-bottom, z-score, pair hai mốc, benchmark/profile. Không import Streamlit/Plotly và không đọc file.
- `app/pages/provincial.py`: controls, state selection, chart composition và narrative bám số liệu.
- `tests/test_provincial.py`: test behavior/edge case của từng helper.
- `tests/test_provincial_page.py`: AppTest boot/filter/selection fallback, không gọi LLM hay dữ liệu raw.

## Tiêu chí hoàn thành

- H2 có header, KPI, map, ranking top/bottom, boxplot vùng, slopegraph, outlier, radar/benchmark và nguồn/dữ liệu thiếu rõ ràng.
- Mọi kết luận lấy giá trị từ DataFrame trong lần render; không hard-code insight/số liệu.
- Có click-to-drill trên map và fallback selectbox.
- Unit test, AppTest, `pytest -q`, Streamlit smoke test 6/8 lĩnh vực đều đạt trong môi trường dự án.
- Báo cáo H2 dùng số tái tạo được; docs trạng thái khớp code/test.

## Rủi ro và giảm thiểu

- Selection API Streamlit có thể khác AppTest: guard event rỗng, fallback selectbox, test riêng hành vi pure helper.
- Thiếu dữ liệu theo năm/thang: snapshot/slope/profile phải trả rỗng có thông báo, không index dòng đầu.
- Khác biệt với nhánh cũ: chỉ port theo test/contract đã chốt, không copy nguyên file.
