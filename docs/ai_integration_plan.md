# Kế hoạch tích hợp AI

Người đảm nhiệm: **Dương Tuấn Anh** (toàn bộ module AI). Khung thời gian: **16–26/6** (cùng deadline dashboard).

Phạm vi đã chốt: **toàn bộ module AI + 4 plugin**, mức **đạt guide v2 + điểm cộng tích hợp**, mốc **26/6**.
Spec gốc: `docs/ai-guide-v2.pdf`. Ràng buộc chung của đề: `CLAUDE.md` §4–5.

> Lưu ý tải: 26/6 cũng là deadline dashboard và Tuấn Anh còn chủ trì P4 (merge/verify cả nhóm).
> Kế hoạch cố tình đẩy việc nền tảng (GĐ A, B) lên sớm để tránh dồn cuối kỳ.

## 0. Nguyên tắc bất biến (không vi phạm khi code)
Không thực thi ngầm · hiển thị code · giải thích ngôn ngữ tự nhiên · duyệt trước khi chạy · log đủ ·
chạy local · AI không bịa số · **AI không tự sửa dashboard / dữ liệu gốc**.

Mọi thay đổi giữ chữ ký hàm freeze (thêm tham số có default), **không đụng `app/ai/api_exec.py`** (sandbox)
và `app/lib/*` / `.streamlit/config.toml` / `data/processed/dim_indicator.csv`.

## 1. Điểm xuất phát

| Hạng mục | Trạng thái |
|---|---|
| 3 API + `ai_assistant` + `registry` + plugin `describe` | ✅ skeleton có |
| `groq` cài | ✅ đã cài trong `.venv`, đã ghi requirements |
| `GROQ_API_KEY` | ⚠️ cần có trong `secrets.toml` hoặc biến môi trường |
| 4 plugin thật | ❌ chưa |
| Context-aware / diff log / nút giải thích | ❌ chưa |
| Câu hỏi vấn đáp / mục báo cáo / test | ❌ chưa |

## 2. Bốn giai đoạn

### GĐ A — Làm module CHẠY THẬT (nền tảng) · 16–18/6
- **A1.** `pip install groq` → ghim vào `requirements.txt`.
- **A2.** Lấy key tại https://console.groq.com/keys → `secrets.toml`; tạo `secrets.toml.example` (key rỗng) cho
  nhóm; xác nhận `.gitignore` đã chặn `secrets.toml`.
- **A3.** Smoke test end-to-end với plugin `describe`: chọn → sinh code → duyệt → chạy → `result` → log ghi file.
- **A4.** Làm chắc `api_ai._parse_response`: model trả sai JSON → báo lỗi rõ + nút sinh lại (đã có fallback, cần test).
- **DoD:** chạy `describe` ra bảng thật; `logs/ai_sessions.jsonl` có bản ghi.

### GĐ B — Bốn plugin technique · 18–21/6
Mỗi plugin = 1 file `app/ai/techniques/<key>.py`, chỉ gọi `register(...)` với `default_request`
**nêu rõ bảng/cột/ngưỡng + ép gán `result`/`fig`** (theo mẫu `example_describe.py`).

| Plugin | Hướng | Nội dung |
|---|---|---|
| `trend_classification` | H1 | phân loại lĩnh vực cải thiện/ổn định/suy giảm (ngưỡng ±0.03) — đối chiếu `src/analysis/trend.py` |
| `anomaly` | H2 | phát hiện tỉnh bất thường (z-score / IQR) |
| `insight` | H3 | nhận xét tự động cho một lĩnh vực/tỉnh |
| `clustering` | H4 | gom nhóm tỉnh theo hồ sơ lĩnh vực (StandardScaler + KMeans) |

Quy trình mỗi plugin: viết `default_request` → chạy thật với Groq → tinh chỉnh tới khi code sinh ra
chạy sạch và **số khớp dashboard**.
- **DoD:** cả 4 hiện trong dropdown; mỗi cái sinh→duyệt→chạy ra `result`+`fig` hợp lý.

### GĐ C — Điểm cộng tích hợp · 21–24/6
- **C1. Context-aware** (3 thay đổi nhỏ): page ghi `session_state["dash_context"]`;
  `api_ai.generate(..., context=None)` + `_format_context()`; `api_logs` log thêm `context`. Không đụng `api_exec`.
- **C2. Diff log** (rẻ nhất, làm trước): render diff `code_ai` ↔ `code_run` trong expander nhật ký
  → bằng chứng "người đã can thiệp".
- **C3. Nút "Giải thích biểu đồ này"** dưới mỗi chart: seed câu hỏi + filter hiện tại → chuyển sang
  AI Assistant qua `session_state`.
- **DoD:** cùng câu mơ hồ ra kết quả khác theo filter; nhật ký hiện diff; nút giải thích chạy.

### GĐ D — Vấn đáp, báo cáo, test · 24–26/6
- **D1.** ≥4 câu hỏi phân tích chuẩn bị sẵn (mỗi hướng 1) + tập demo; lường câu ngoài lề.
- **D2.** Mục báo cáo (guide §4 / đề §7): tóm tắt quá trình dùng AI, **trích log thật**.
- **D3.** Test: `pytest` cho `_parse_response`; AppTest cho `ai_assistant` (mock `api_ai`, không gọi mạng).
- **DoD:** demo 4 câu mượt; mục báo cáo xong; test xanh.

## 3. Thứ tự ưu tiên (hụt giờ thì cắt từ dưới lên)
- **Must (không cắt):** A + B(≥1 plugin) + D1 + D2.
- **Nên:** B đủ 4 plugin + C2 (diff log).
- **Cộng:** C1 (context-aware) + C3 (nút giải thích).

## 4. Rủi ро & giảm thiểu
- **Quota/mạng Groq:** dùng model mặc định `llama-3.3-70b-versatile`; giữ chế độ "tự nhập yêu cầu"; **chụp sẵn vài kết quả**
  phòng rớt mạng lúc demo.
- **Model trả sai JSON / code lỗi runtime:** fallback parse + sandbox bắt exception, hiện lỗi, người sửa chạy lại.
- **Xung đột tải 24–26/6** (vừa P4 merge cả nhóm vừa D): đẩy A+B xong sớm; nếu kẹt, hạ scope theo mục 3.
- **Bảo mật sandbox:** nêu trung thực giới hạn — lớp bảo vệ thật là người duyệt code, không phải sandbox.

## 5. File sẽ đụng
- **Tạo:** `app/ai/techniques/{trend_classification,anomaly,insight,clustering}.py` · `.streamlit/secrets.toml.example`
  · `tests/test_api_ai.py`, `tests/test_ai_assistant.py` · mục báo cáo trong `report/`.
- **Sửa (thêm tham số default, không đổi chữ ký cũ):** `api_ai.py` (+context) · `api_logs.py` (+context)
  · `ai_assistant.py` (diff, badge, seed) · các page (1 dòng publish context + nút giải thích) · `requirements.txt`.
- **Không đụng:** `api_exec.py`, `lib/*` chữ ký, `config.toml`, `dim_indicator.csv`.

## 6. Việc làm ngay khi bắt đầu
1. Tách branch `feat/ai-module`.
2. **A1 + A2** (cài SDK + dựng `secrets.toml.example` + key) — mọi thứ phía sau phụ thuộc luồng chạy thật.
