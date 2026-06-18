import sys
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))


def test_ai_assistant_happy_path(monkeypatch, tmp_path):
    from ai import api_ai, api_logs
    from lib import data
    captured = {}

    demo_data = {
        "prov_year": pd.DataFrame({"year": [2024, 2024], "total_papi": [40.0, 42.0]}),
        "national": pd.DataFrame({"year": [2024], "code": ["D1"], "mean_score": [5.0]}),
        "geojson": {"type": "FeatureCollection", "features": []},
    }

    monkeypatch.setattr(data, "load_data", lambda: demo_data)
    def fake_generate(request, data, context=None, system_instruction=None, model=api_ai.DEFAULT_MODEL):
        captured["request"] = request
        return {
            "code": "result = prov_year.head()",
            "explanation": "Lấy vài dòng đầu để kiểm tra.",
        }

    monkeypatch.setattr(api_ai, "generate", fake_generate)
    monkeypatch.setattr(api_logs, "LOG_FILE", tmp_path / "ai_sessions.jsonl")

    app = AppTest.from_file(str(ROOT / "app" / "pages" / "ai_assistant.py"))
    app.run()
    assert not app.exception

    app.text_area[0].set_value("Lấy vài dòng đầu")
    app.text_area[1].set_value("Chỉ lấy năm 2024")
    app.button[0].click().run()
    assert not app.exception
    assert "Lấy vài dòng đầu" in captured["request"]
    assert "Yêu cầu phân tích bổ sung của người dùng" in captured["request"]
    assert "Chỉ lấy năm 2024" in captured["request"]
    assert "result = prov_year.head()" in app.text_area[2].value

    app.button[2].click().run()
    assert not app.exception
    assert app.dataframe


def test_changing_technique_clears_previous_code_and_result(monkeypatch, tmp_path):
    from ai import api_ai, api_logs
    from lib import data

    demo_data = {
        "prov_year": pd.DataFrame({"year": [2024, 2024], "total_papi": [40.0, 42.0]}),
        "national": pd.DataFrame({"year": [2024], "code": ["D1"], "mean_score": [5.0]}),
        "geojson": {"type": "FeatureCollection", "features": []},
    }

    monkeypatch.setattr(data, "load_data", lambda: demo_data)
    monkeypatch.setattr(
        api_ai,
        "generate",
        lambda request, data, context=None, system_instruction=None, model=api_ai.DEFAULT_MODEL: {
            "code": "result = prov_year.head()",
            "explanation": "Lấy vài dòng đầu để kiểm tra.",
        },
    )
    monkeypatch.setattr(api_logs, "LOG_FILE", tmp_path / "ai_sessions.jsonl")

    app = AppTest.from_file(str(ROOT / "app" / "pages" / "ai_assistant.py"))
    app.run()
    app.selectbox[0].set_value("Phát hiện tỉnh bất thường").run()
    app.button[0].click().run()
    app.button[2].click().run()
    assert app.dataframe
    assert len(app.text_area) == 3

    app.selectbox[0].set_value("Gom nhóm tỉnh theo hồ sơ lĩnh vực").run()

    assert not app.dataframe
    assert len(app.text_area) == 2
    assert "gom nhóm" in app.text_area[0].value.lower()
    assert app.text_area[1].value == ""


def test_selected_technique_uses_edited_suggestion_not_default(monkeypatch, tmp_path):
    from ai import api_ai, api_logs
    from lib import data
    captured = {}

    demo_data = {
        "prov_year": pd.DataFrame({"year": [2024, 2024], "total_papi": [40.0, 42.0], "D8": [1.0, 3.0]}),
        "national": pd.DataFrame({"year": [2024], "code": ["D8"], "mean_score": [5.0]}),
        "geojson": {"type": "FeatureCollection", "features": []},
    }

    monkeypatch.setattr(data, "load_data", lambda: demo_data)

    def fake_generate(request, data, context=None, system_instruction=None, model=api_ai.DEFAULT_MODEL):
        captured["request"] = request
        captured["system_instruction"] = system_instruction
        return {
            "code": "result = prov_year[['province_vi']] if 'province_vi' in prov_year else prov_year.head()",
            "explanation": "test",
        }

    monkeypatch.setattr(api_ai, "generate", fake_generate)
    monkeypatch.setattr(api_logs, "LOG_FILE", tmp_path / "ai_sessions.jsonl")

    app = AppTest.from_file(str(ROOT / "app" / "pages" / "ai_assistant.py"))
    app.run()
    app.selectbox[0].set_value("Phát hiện tỉnh bất thường").run()

    edited_question = "Hãy phát hiện tỉnh bất thường riêng cho lĩnh vực D8 trong năm mới nhất."
    app.text_area[0].set_value(edited_question)
    app.button[0].click().run()

    assert captured["request"] == edited_question
    assert "D8" in captured["request"]
    assert "total_papi bất thường so với mặt bằng chung" not in captured["request"]
    assert "Nếu câu hỏi người dùng nêu rõ" in captured["system_instruction"]


def test_selected_technique_sends_edited_topic_and_extra_feedback(monkeypatch, tmp_path):
    from ai import api_ai, api_logs
    from lib import data
    captured = {}

    demo_data = {
        "prov_year": pd.DataFrame({
            "year": [2024, 2024, 2024],
            "province_vi": ["A", "B", "C"],
            "region": ["Đông Nam Bộ", "Đồng bằng sông Cửu Long", "Đông Nam Bộ"],
            "D1": [5.0, 6.0, 7.0],
            "D2": [5.0, 6.0, 7.0],
            "D3": [5.0, 6.0, 7.0],
            "D4": [5.0, 6.0, 7.0],
            "D5": [5.0, 6.0, 7.0],
            "D6": [5.0, 6.0, 7.0],
            "D7": [5.0, 6.0, 7.0],
            "D8": [5.0, 6.0, 7.0],
        }),
        "national": pd.DataFrame({"year": [2024], "code": ["D8"], "mean_score": [5.0]}),
        "geojson": {"type": "FeatureCollection", "features": []},
    }

    monkeypatch.setattr(data, "load_data", lambda: demo_data)

    def fake_generate(request, data, context=None, system_instruction=None, model=api_ai.DEFAULT_MODEL):
        captured["request"] = request
        captured["system_instruction"] = system_instruction
        return {
            "code": "result = prov_year.head()\nfig = None",
            "explanation": "test",
        }

    monkeypatch.setattr(api_ai, "generate", fake_generate)
    monkeypatch.setattr(api_logs, "LOG_FILE", tmp_path / "ai_sessions.jsonl")

    app = AppTest.from_file(str(ROOT / "app" / "pages" / "ai_assistant.py"))
    app.run()
    app.selectbox[0].set_value("Gom nhóm tỉnh theo hồ sơ lĩnh vực").run()

    edited_topic = (
        "Hãy gom nhóm các tỉnh miền Nam thành 3 cụm dựa trên 8 lĩnh vực PAPI "
        "trong năm mới nhất, vẽ scatter D1 và D8."
    )
    extra_feedback = "Chỉ dùng region thật trong dữ liệu và nếu thiếu dữ liệu thì trả bảng giải thích."
    app.text_area[0].set_value(edited_topic)
    app.text_area[1].set_value(extra_feedback)
    app.button[0].click().run()

    assert "Câu hỏi chính" in captured["request"]
    assert edited_topic in captured["request"]
    assert "Yêu cầu phân tích bổ sung của người dùng" in captured["request"]
    assert extra_feedback in captured["request"]
    assert "3 cụm" in captured["request"]
    assert "D1 và D8" in captured["request"]
    assert "4 cụm" not in captured["request"]
    assert "D4 (Kiểm soát tham nhũng) và D8" not in captured["request"]
    assert "miền Nam" in captured["system_instruction"]


def test_selected_pattern_keeps_edited_chart_and_color_requirements(monkeypatch, tmp_path):
    from ai import api_ai, api_logs
    from lib import data
    captured = {}

    demo_data = {
        "prov_year": pd.DataFrame({
            "year": [2024, 2024, 2024, 2024],
            "province_vi": ["A", "B", "C", "D"],
            "D6": [6.1, 4.2, 5.5, 7.3],
            "D8": [3.1, 2.8, 4.0, 3.7],
            "total_papi": [42.0, 39.0, 41.0, 44.0],
            "total_papi_6dim": [36.0, 35.0, 37.0, 38.0],
        }),
        "national": pd.DataFrame({"year": [2024], "code": ["D6"], "mean_score": [5.0]}),
        "geojson": {"type": "FeatureCollection", "features": []},
    }

    monkeypatch.setattr(data, "load_data", lambda: demo_data)

    def fake_generate(request, data, context=None, system_instruction=None, model=api_ai.DEFAULT_MODEL):
        captured["request"] = request
        captured["system_instruction"] = system_instruction
        return {
            "code": (
                "df = prov_year[prov_year['year'] == prov_year['year'].max()].copy()\n"
                "result = df[['province_vi', 'D6']].head()\n"
                "fig = px.scatter(result, x='province_vi', y='D6')"
            ),
            "explanation": "test",
        }

    monkeypatch.setattr(api_ai, "generate", fake_generate)
    monkeypatch.setattr(api_logs, "LOG_FILE", tmp_path / "ai_sessions.jsonl")

    app = AppTest.from_file(str(ROOT / "app" / "pages" / "ai_assistant.py"))
    app.run()
    app.selectbox[0].set_value("Phát hiện tỉnh bất thường").run()

    edited_topic = (
        "Hãy phát hiện các tỉnh bất thường riêng cho lĩnh vực D6 trong năm mới nhất, "
        "không dùng tổng điểm PAPI."
    )
    visual_feedback = (
        "Không vẽ biểu đồ cột mặc định. Hãy vẽ scatter plot, trục x là province_vi, "
        "trục y là D6, tỉnh bất thường màu đỏ, tỉnh còn lại màu xám, hover hiển thị province_vi và z_score."
    )
    app.text_area[0].set_value(edited_topic)
    app.text_area[1].set_value(visual_feedback)
    app.button[0].click().run()

    assert "Câu hỏi chính" in captured["request"]
    assert edited_topic in captured["request"]
    assert "Yêu cầu phân tích bổ sung của người dùng" in captured["request"]
    assert visual_feedback in captured["request"]
    assert "D6" in captured["request"]
    assert "không dùng tổng điểm PAPI" in captured["request"]
    assert "scatter plot" in captured["request"]
    assert "màu đỏ" in captured["request"]
    assert "màu xám" in captured["request"]
    assert "hover hiển thị province_vi và z_score" in captured["request"]
    assert "biểu đồ cột mặc định" in captured["request"]
    assert "Nếu câu hỏi người dùng nêu rõ" in captured["system_instruction"]


def test_reset_returns_to_free_input_with_blank_prompt_fields(monkeypatch, tmp_path):
    from ai import api_ai, api_logs
    from lib import data

    demo_data = {
        "prov_year": pd.DataFrame({"year": [2024, 2024], "total_papi": [40.0, 42.0]}),
        "national": pd.DataFrame({"year": [2024], "code": ["D1"], "mean_score": [5.0]}),
        "geojson": {"type": "FeatureCollection", "features": []},
    }

    monkeypatch.setattr(data, "load_data", lambda: demo_data)
    monkeypatch.setattr(
        api_ai,
        "generate",
        lambda request, data, context=None, system_instruction=None, model=api_ai.DEFAULT_MODEL: {
            "code": "result = prov_year.head()",
            "explanation": "test",
        },
    )
    monkeypatch.setattr(api_logs, "LOG_FILE", tmp_path / "ai_sessions.jsonl")

    app = AppTest.from_file(str(ROOT / "app" / "pages" / "ai_assistant.py"))
    app.run()
    app.selectbox[0].set_value("Gom nhóm tỉnh theo hồ sơ lĩnh vực").run()
    app.text_area[1].set_value("Góp ý thêm trước khi reset")
    app.button[0].click().run()
    assert len(app.text_area) == 3

    app.button[1].click().run()

    assert app.selectbox[0].value == "(Tự nhập yêu cầu)"
    assert len(app.text_area) == 2
    assert app.text_area[0].value == ""
    assert app.text_area[1].value == ""
    assert not app.dataframe


def test_selecting_free_input_after_result_clears_generated_state(monkeypatch, tmp_path):
    from ai import api_ai, api_logs
    from lib import data

    demo_data = {
        "prov_year": pd.DataFrame({"year": [2024, 2024], "total_papi": [40.0, 42.0]}),
        "national": pd.DataFrame({"year": [2024], "code": ["D1"], "mean_score": [5.0]}),
        "geojson": {"type": "FeatureCollection", "features": []},
    }

    monkeypatch.setattr(data, "load_data", lambda: demo_data)
    monkeypatch.setattr(
        api_ai,
        "generate",
        lambda request, data, context=None, system_instruction=None, model=api_ai.DEFAULT_MODEL: {
            "code": "result = prov_year.head()",
            "explanation": "test",
        },
    )
    monkeypatch.setattr(api_logs, "LOG_FILE", tmp_path / "ai_sessions.jsonl")

    app = AppTest.from_file(str(ROOT / "app" / "pages" / "ai_assistant.py"))
    app.run()
    app.selectbox[0].set_value("Phát hiện tỉnh bất thường").run()
    app.button[0].click().run()
    app.button[2].click().run()
    assert app.dataframe
    assert len(app.text_area) == 3

    app.selectbox[0].set_value("(Tự nhập yêu cầu)").run()

    assert len(app.text_area) == 2
    assert app.text_area[0].value == ""
    assert app.text_area[1].value == ""
    assert not app.dataframe
