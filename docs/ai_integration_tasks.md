# Kế hoạch tích hợp AI — task chi tiết & phân việc

Bản chi tiết hoá của `docs/ai_integration_plan.md` xuống mức task thực thi được.
Mỗi task có: spec kỹ thuật, file, DoD kiểm chứng, phụ thuộc, **owner** (🤖 Sonnet = agent code thuần;
👤 Human = cần con người/API key/demo).

Quy ước bất biến (mọi task tuân thủ): không đụng `app/ai/api_exec.py`, `app/lib/*` chữ ký,
`.streamlit/config.toml`, `data/processed/dim_indicator.csv`. Chỉ thêm tham số có default, không đổi chữ ký cũ.

---

## Gói WP-A — Nền tảng api_ai + test (🤖 Sonnet, độc lập file)

**A1. Thêm dependency** — `requirements.txt`: thêm dòng `google-genai`. Thử `pip install google-genai`;
nếu mạng chặn, vẫn ghi vào requirements và ghi chú lại. *DoD:* requirements có entry.

**A4. Làm chắc `api_ai._parse_response`** (`app/ai/api_ai.py`). Hàm phải **không bao giờ ném lỗi** và
chịu 4 dạng output của model, theo thứ tự thử:
1. JSON sạch → `json.loads`.
2. Fence ```json ... ``` → bóc rồi `json.loads` (đã có regex, giữ).
3. Fence ```python ... ``` → coi là `code`, `explanation=""`.
4. Không khớp gì → `code=text.strip()`, `explanation=""`.
Trả `{"code": str, "explanation": str}` — `code` luôn là str (không None). Không đổi chữ ký.
*DoD:* `tests/test_api_ai.py` xanh.

**D3a. Test `_parse_response`** — tạo `tests/test_api_ai.py` (pytest, offline, không gọi mạng).
Ca kiểm: JSON sạch · fence json · fence python · text thuần · JSON có ký tự xuống dòng trong code.
Mỗi ca khẳng định `code`/`explanation` đúng kỳ vọng. *DoD:* `pytest tests/test_api_ai.py` xanh.

> Phụ thuộc: không. Đụng file: `api_ai.py`, `requirements.txt`, `tests/test_api_ai.py` (mới). KHÔNG đụng file khác.

---

## Gói WP-Plugins — 4 plugin technique (🤖 Sonnet viết nháp · 👤 nghiệm thu bằng Gemini)

Mỗi file `app/ai/techniques/<key>.py` chỉ gọi `registry.register(key, label, description, default_request)`
theo mẫu `app/ai/techniques/example_describe.py`. `default_request` PHẢI: nêu rõ **bảng + cột** dùng,
**ngưỡng/tham số** cụ thể, và **bắt gán `result` (DataFrame/Series) + `fig` (plotly)**. Tiếng Việt.

Schema dữ liệu cho code AI (nhắc trong default_request khi cần):
- `prov_year`: wide 63 tỉnh × năm — cột `province_vi, region, year, D1..D8, total_papi, total_papi_6dim, rank_year, tier`.
- `national`: long trung bình 63 tỉnh — cột `year, code, mean_score, min_score, max_score, std_score`.
- Tên hiển thị lĩnh vực: D1 Tham gia · D2 Công khai minh bạch · D3 Trách nhiệm giải trình · D4 Kiểm soát tham nhũng
  · D5 Thủ tục hành chính công · D6 Cung ứng dịch vụ công · D7 Quản trị môi trường · D8 Quản trị điện tử.

| File | key / label | default_request mô tả (tóm tắt) |
|---|---|---|
| `trend_classification.py` | `trend_classification` / "Phân loại lĩnh vực cải thiện/ổn định/suy giảm" | Trên `national`, tính delta mỗi lĩnh vực = mean_score năm cuối − năm đầu; phân loại theo ngưỡng ±0.03 (>0.03 cải thiện, <−0.03 suy giảm, còn lại ổn định); `result` = bảng [lĩnh vực, delta, nhãn]; `fig` = diverging bar. |
| `anomaly.py` | `anomaly` / "Phát hiện tỉnh bất thường" | Trên `prov_year` năm mới nhất, tính z-score của `total_papi` (hoặc `total_papi_6dim`); đánh dấu \|z\|>2 là bất thường; `result` = bảng tỉnh bất thường + z; `fig` = bar/scatter tô màu nhóm bất thường. |
| `insight.py` | `insight` / "Nhận xét tự động một lĩnh vực" | Cho một lĩnh vực (vd D4): trên `national` mô tả xu hướng (đầu/cuối/đỉnh/đáy), trên `prov_year` nêu tỉnh cao/thấp nhất năm mới nhất; `result` = bảng số liệu chốt; `fig` = line theo năm. |
| `clustering.py` | `clustering` / "Gom nhóm tỉnh theo hồ sơ lĩnh vực" | Trên `prov_year` năm mới nhất, lấy D1..D8 (hoặc D1..D6); `StandardScaler` + `KMeans(n=4)`; `result` = bảng tỉnh + nhãn cụm; `fig` = scatter 2 lĩnh vực tô màu cụm. |

*DoD (Sonnet):* 4 file đăng ký đúng, import sạch (`python -c "import ai.techniques.<key>"` với `app` trên path
không lỗi); `default_request` đủ chi tiết. *DoD (Human):* chạy thật qua AI Assistant, code sinh ra chạy sạch,
số khớp dashboard.

> Phụ thuộc: không. Đụng file: 4 file MỚI trong `app/ai/techniques/`. KHÔNG đụng file khác → song song được với WP-A.

---

## Gói WP-Context — Context-aware (🤖 Sonnet) · ĐỢT 2 (sau WP-A vì cùng đụng api_ai.py)

**C1a. Page publish context.** Trong `app/pages/time_trend.py` (làm mẫu, sau nhân ra page khác), sau khi có
`mode, total_col, cfg, y0, y1`, thêm:
```python
st.session_state["dash_context"] = {
    "page": "Diễn biến theo thời gian",
    "scale_mode": mode, "total_col": total_col,
    "dims": {c: config.DIM_LABELS[c] for c in cfg["dims"]},
    "year_range": [int(y0), int(y1)],
}
```

**C1b. `api_ai` nhận context.** `app/ai/api_ai.py`:
- Đổi `def generate(request, data, model=DEFAULT_MODEL)` → `def generate(request, data, context=None, model=DEFAULT_MODEL)`.
- Thêm `_format_context(context) -> str`: None/rỗng → `""`; ngược lại trả khối
  `"NGỮ CẢNH DASHBOARD (người dùng đang xem):\n- Trang: ...\n- Phạm vi: ...\n- Cột tổng: ...\n- Lĩnh vực: ...\n- Khoảng năm: ..."`.
- Ghép `_format_context(context)` vào `prompt` giữa SCHEMA và "Yêu cầu của người dùng".

**C1c. `ai_assistant` truyền context.** `app/pages/ai_assistant.py`: khi gọi `api_ai.generate`, truyền
`context=st.session_state.get("dash_context")`; thêm `"context": st.session_state.get("dash_context")` vào
record `api_logs.log({...})`.

*DoD:* AppTest boot sạch; đổi filter ở time_trend rồi sang AI Assistant, prompt gửi đi có khối ngữ cảnh
(kiểm bằng test gọi `_format_context`). *Phụ thuộc:* WP-A (cùng đụng `api_ai.py`). Đụng: `api_ai.py`,
`ai_assistant.py`, `time_trend.py`.

---

## Gói WP-Frontend — Diff log + nút giải thích + badge (🤖 Sonnet) · ĐỢT 3 (sau C1, cùng đụng ai_assistant.py)

**C2. Diff log.** `app/pages/ai_assistant.py`, trong expander nhật ký: với mỗi bản ghi có `code_ai != code_run`,
render `difflib.unified_diff(code_ai.splitlines(), code_run.splitlines(), lineterm="")` qua
`st.code("\n".join(diff), language="diff")`. Nếu trùng → ghi "Người dùng không chỉnh sửa".

**C3. Nút "Giải thích biểu đồ này".** Dưới một biểu đồ ở `time_trend.py` (làm mẫu), thêm
`st.button("Giải thích biểu đồ này")`: khi bấm → set
`st.session_state["ai_seed"] = "<câu hỏi bám biểu đồ + filter hiện tại>"` rồi `st.switch_page("pages/ai_assistant.py")`.
Trong `ai_assistant.py`: `value` của ô yêu cầu lấy `st.session_state.pop("ai_seed", default_req)`.

**C2b/badge. Trạng thái chờ duyệt.** Cạnh tiêu đề "Code AI đề xuất", thêm badge `🟡 Chờ duyệt` (markdown);
giữ nguyên luồng nút "Phê duyệt và thực thi".

**D3b. AppTest cho ai_assistant.** `tests/test_ai_assistant.py`: monkeypatch `ai.api_ai.generate` trả
`{"code": "result = prov_year.shape", "explanation": "test"}` (KHÔNG gọi mạng); chạy AppTest, khẳng định
không exception. *DoD:* `pytest` xanh; AppTest boot sạch.

> *Phụ thuộc:* C1. Đụng: `ai_assistant.py`, `time_trend.py`, `tests/test_ai_assistant.py` (mới).

---

## Việc của con người (👤 — không giao agent)
- **A2.** Lấy `GEMINI_API_KEY` (aistudio.google.com) → `.streamlit/secrets.toml`. (Sonnet chỉ tạo `secrets.toml.example`.)
- **B-nghiệm thu.** Chạy thật 4 plugin qua AI Assistant, tinh chỉnh `default_request` tới khi số khớp dashboard.
- **D1.** Chốt ≥4 câu hỏi vấn đáp + tập demo + chụp ảnh dự phòng.
- **D2.** Viết mục báo cáo "quá trình dùng AI", trích `logs/ai_sessions.jsonl`.

## Trình tự thực thi
1. **Đợt 1 (song song):** WP-A ‖ WP-Plugins ‖ (Sonnet tạo `secrets.toml.example`). → review.
2. **Đợt 2:** WP-Context (sau WP-A). → review.
3. **Đợt 3:** WP-Frontend (sau WP-Context). → review.
4. **Con người:** A2 key → nghiệm thu plugin → D1 + D2.
