# Kiến trúc dự án

Kiến trúc tách theo separation of concerns: data layer, app layer và AI layer độc lập, giao tiếp qua
các interface rõ ràng.

## 1. Cây thư mục

```
final-project/
├── data/
│   ├── raw/                 # 14 tệp Excel gốc (chỉ đọc)
│   └── processed/           # output của pipeline (parquet, csv)
├── notebooks/               # bản trình bày: logic viết thẳng trong notebook
│   ├── data_understanding.ipynb
│   ├── preprocessing.ipynb  # tự chứa logic + ô cross-check với src
│   └── eda.ipynb
├── src/                     # bản kỹ thuật: library tái sử dụng cho app, và để đối chiếu
│   ├── papi_lib.py          # lookup table, chuẩn hóa, hai parser
│   ├── build_dataset.py     # pipeline raw -> processed + quality checks
│   └── analysis.py          # các analysis function thuần (thêm ở Phase 3-4)
├── app/                     # Streamlit app
│   ├── main.py              # entry point, multipage navigation
│   ├── pages/               # overview, time_trend, provincial, dimension, dynamics, ai_assistant
│   ├── lib/                 # data, charts, filters, config (dùng chung)
│   └── ai/                  # AI module human-in-the-loop
│       ├── api_ai.py · api_exec.py · api_logs.py
│       └── techniques/      # plugin của từng kỹ thuật
├── logs/ · reports/figures/ · report/ · docs/
└── requirements.txt · CLAUDE.md
```

## 2. Hai bản của data layer

Notebook trong `notebooks/` là bản trình bày và verify. Logic viết thẳng trong các ô để đọc và chạy
độc lập. Đây là sản phẩm dùng cho trình bày với giảng viên.

`src/` là bản engineering: cùng logic dưới dạng library `papi_lib.py` và pipeline `build_dataset.py`,
được app và AI module gọi lại. Giữ để phát triển về sau và để đối chiếu.

Hai bản giữ đồng bộ bằng cross-check: ô cuối của `preprocessing.ipynb` chạy lại pipeline trong `src/`
và assert kết quả notebook trùng khớp với `src/`. Nếu lệch, ô này báo lỗi.

## 3. Ba layer của app

Data layer (`notebooks/`, `src/`, `data/`) chuyển raw thành dataset chuẩn và cung cấp các analysis
function thuần, không phụ thuộc giao diện.

App layer (`app/`) là Streamlit dashboard. Chỉ đọc dữ liệu đã xử lý, lọc và hiển thị; tính toán nặng
đã làm sẵn ở data layer. Nạp dữ liệu dùng `@st.cache_data` để tránh đọc lại tệp mỗi lần tương tác.

AI layer (`app/ai/`) là AI module human-in-the-loop, gồm ba API và gọi lại các analysis function thuần
trong `src/` khi execute, nên logic phân tích chỉ tồn tại một nơi.

## 4. AI module human-in-the-loop

Ba API phản ánh yêu cầu của đề. `api_ai.py` nhận yêu cầu bằng ngôn ngữ tự nhiên kèm context là schema
dataset, gọi LLM, trả về code kèm giải thích ở trạng thái chờ duyệt. `api_exec.py` nhận code đã sửa
và duyệt, execute tại máy trong một namespace hạn chế chỉ cung cấp bản sao read-only của dữ liệu.
`api_logs.py` ghi lại request, code gốc, code đã sửa, kết quả và giải thích vào `logs/`. Trạng thái
chờ duyệt và đã duyệt quản lý qua session state của Streamlit; API key của LLM lưu trong secrets,
không đưa vào source.

## 5. Nguyên tắc

Dependency một chiều: app và AI layer phụ thuộc `src/`, còn `src/` không phụ thuộc giao diện (không có
`import streamlit` trong `src/`). Analysis logic chỉ ở một nơi. Raw data bất khả xâm phạm; mọi biến
đổi đi qua pipeline có log. Code do AI sinh không execute nếu chưa được duyệt. Config và secrets tách
khỏi source. Các page không chứa tính toán nặng.

## 6. Tech stack

pandas và pyarrow cho xử lý dữ liệu; plotly cho biểu đồ tương tác trong app, matplotlib và seaborn cho
biểu đồ tĩnh trong EDA; scipy và scikit-learn cho thống kê và machine learning; Streamlit cho giao
diện; LLM gọi qua API, trong khi mọi code phân tích execute tại máy.
