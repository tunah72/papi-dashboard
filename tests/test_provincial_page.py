import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))


def test_provincial_page_boots_with_default_data():
    """Smoke test H2: các control, bản đồ và chart phải render không lỗi."""
    app = AppTest.from_file(str(ROOT / "app" / "pages" / "provincial.py"))

    app.run(timeout=30)

    assert not app.exception
    assert len(app.select_slider) >= 2
    assert len(app.get("plotly_chart")) == 6
    assert app.segmented_control[1].value == "Cực trị"


def test_provincial_page_switches_to_eight_dimension_scale():
    from lib import config

    app = AppTest.from_file(str(ROOT / "app" / "pages" / "provincial.py"))
    app.run(timeout=30)
    app.segmented_control[0].set_value(config.SCALE_8DIM).run(timeout=30)

    assert not app.exception
    assert app.session_state["dash_context"]["total_col"] == "total_papi"


def test_provincial_page_only_renders_delta_chart_when_change_view_is_selected():
    app = AppTest.from_file(str(ROOT / "app" / "pages" / "provincial.py"))

    app.run(timeout=30)
    app.segmented_control[1].set_value("Thay đổi").run(timeout=30)

    assert not app.exception
    assert len(app.get("plotly_chart")) == 5
