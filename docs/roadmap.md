# Roadmap đến bản demo hoàn chỉnh

Roadmap này chỉ chứa công việc chưa hoàn tất tại ngày 17/07/2026. Các kế hoạch tháng 06 đã được lưu
trong `archive/` và không dùng để theo dõi tiến độ mới.

## P0 — Nền tài liệu và tính tái lập

- [x] Tạo chỉ mục tài liệu và phân loại current/archive.
- [x] Viết lại trạng thái và kiến trúc dựa trên code.
- [x] Thêm `pytest` vào `requirements-dev.txt` cho môi trường phát triển.
- [ ] Chạy notebook preprocessing từ đầu và lưu bằng chứng cross-check với pipeline.
- [x] Chuẩn hoá GeoJSON khi nạp app: gộp hai phần ID `49`, rewind vòng cho Plotly/D3 và test 63 ID;
  giữ nguyên file nguồn.

## P1 — Hoàn thiện ba hướng dashboard còn thiếu

Thứ tự khuyến nghị: H2 → H3 → H4, mỗi hướng là một PR nhỏ có page, analysis module và test.

- [ ] H2: bản đồ/xếp hạng/so sánh vùng và drill-down tỉnh.
- [ ] H3: hồ sơ lĩnh vực, correlation và so sánh vùng/tỉnh.
- [ ] H4: mức thay đổi, clustering và chuyển dịch nhóm/tier.
- [ ] Thêm context thật và nút “Giải thích biểu đồ” cho từng trang.
- [ ] Review nhất quán design, dữ liệu thiếu và cách dùng tổng 6/8 lĩnh vực.

## P2 — Khép kín AI human-in-the-loop

- [ ] Log ngay khi AI sinh đề xuất, kể cả người dùng chưa thực thi.
- [ ] Ghi event rõ ràng cho generate/edit/approve/execute/error thay vì một record tổng hợp mơ hồ.
- [ ] Lưu kết quả đủ để truy xuất: bảng nhỏ hoặc artifact có checksum/path; không chỉ shape/type.
- [ ] Copy/deep-copy hoặc loại khỏi namespace các object không phải DataFrame như GeoJSON.
- [ ] Xác định rõ threat model; giữ demo local và không gọi executor là sandbox bảo mật.
- [ ] Chạy live smoke test Groq và bốn plugin bằng dữ liệu thật, lưu log/ảnh có kiểm soát.
- [ ] Cập nhật manual test theo đúng label và hành vi UI tại thời điểm nghiệm thu.

## P3 — Storytelling và chất lượng trực quan

- [ ] Chốt một câu chuyện xuyên suốt từ Tổng quan đến bốn hướng.
- [ ] Kiểm tra mọi tiêu đề kết luận bằng số liệu; tránh suy diễn nhân quả từ tương quan.
- [ ] Rà accessibility: tương phản, palette, keyboard, nội dung thay thế và kích thước màn hình.
- [ ] Kiểm tra trực quan trên viewport trình chiếu và máy dùng trong vấn đáp.

## P4 — Báo cáo

- [ ] Viết nguồn/phương pháp dữ liệu và toàn bộ bước xử lý.
- [ ] Viết thiết kế dashboard, bốn câu hỏi phân tích và kết luận có giới hạn phương pháp.
- [ ] Viết kiến trúc AI, human-in-the-loop, guard local và hạn chế bảo mật.
- [ ] Bổ sung bảng tóm tắt quá trình dùng AI: yêu cầu, kết quả, chỉnh sửa của người, nhận xét.
- [ ] Chèn hình, nguồn và tài liệu tham khảo; build LaTeX sạch.

## P5 — Vấn đáp và phát hành

- [ ] Chốt ít nhất bốn câu hỏi demo, mỗi thành viên sở hữu một câu.
- [ ] Chuẩn bị kịch bản khi Groq/API không hoạt động: dùng log/artifact đã lưu, không giả lập số liệu.
- [ ] Rehearsal toàn luồng: filter → chart → AI đề xuất → sửa → duyệt → kết quả → log.
- [ ] Chạy test, build dữ liệu/notebook cần thiết, build report và smoke test app.
- [ ] Gắn tag/commit demo sau khi mọi bằng chứng đã được kiểm tra.

## Tiêu chí hoàn tất toàn dự án

Dự án chỉ được gọi là hoàn chỉnh khi bốn hướng dashboard có nội dung thật; AI log chứng minh được vai
trò của con người; dữ liệu/map qua QC; báo cáo khớp code; và một máy mới có thể cài, chạy test, mở app
theo tài liệu mà không cần kiến thức truyền miệng.
