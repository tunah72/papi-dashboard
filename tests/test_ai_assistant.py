import sys
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))


def test_ai_assistant_happy_path(monkeypatch, tmp_path):
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
    assert not app.exception

    app.text_area[0].set_value("Lấy vài dòng đầu")
    app.button[0].click().run()
    assert not app.exception
    assert "result = prov_year.head()" in app.text_area[1].value

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
    assert len(app.text_area) == 2

    app.selectbox[0].set_value("Gom nhóm tỉnh theo hồ sơ lĩnh vực").run()

    assert not app.dataframe
    assert len(app.text_area) == 1
    assert "gom nhóm" in app.text_area[0].value.lower()
