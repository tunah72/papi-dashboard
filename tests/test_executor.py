import pandas as pd

from server import executor


def _data():
    return {"prov_year": pd.DataFrame({"year": [2024, 2024], "score": [1.0, 2.0]})}


def test_execute_returns_result():
    out = executor.execute("result = prov_year.groupby('year')['score'].mean()", _data())
    assert out["error"] is None
    assert float(out["result"].iloc[0]) == 1.5


def test_execute_catches_error_without_raising():
    out = executor.execute("result = missing_name", _data())
    assert out["result"] is None
    assert "NameError" in out["error"]


def test_execute_truncates_stdout():
    out = executor.execute("print('x' * 10000)\nresult = prov_year.head()", _data())
    assert out["error"] is None
    assert len(out["stdout"]) < 5000
    assert "đã cắt stdout" in out["stdout"]


def test_execute_does_not_mutate_input_dataframe():
    data = _data()
    out = executor.execute("prov_year.loc[:, 'score'] = 99\nresult = prov_year", data)
    assert out["error"] is None
    assert data["prov_year"]["score"].tolist() == [1.0, 2.0]


def test_execute_times_out_infinite_loop():
    out = executor.execute("while True:\n    pass", _data(), timeout=1)
    assert out["result"] is None
    assert "TimeoutError" in out["error"]


def test_execute_captures_settingwithcopy_warning():
    data = {"prov_year": pd.DataFrame({"year": [2023, 2024], "score": [1.0, 2.0]})}
    code = """
data = prov_year[prov_year['year'] == 2024]
data['z_score'] = data['score']
result = data
"""
    out = executor.execute(code, data)
    assert out["error"] is None
    assert any("SettingWithCopyWarning" in warning for warning in out["warnings"])
    assert "SettingWithCopyWarning" in out["stdout"]
