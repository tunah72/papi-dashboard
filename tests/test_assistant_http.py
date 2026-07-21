import pandas as pd
import pytest
from fastapi.testclient import TestClient

from server import assistant
from server.main import create_app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(assistant, "LOG_FILE", tmp_path / "assistant.jsonl")
    return TestClient(create_app())


def _message(message="Chỉ số PAPI là gì?", session_id=None, revision_of=None):
    return {
        "sessionId": session_id,
        "message": message,
        "context": {"route": "/overview", "search": {"scale": "eight", "year": "2024"}},
        "revisionOf": revision_of,
    }


def test_knowledge_context_has_eight_dimensions_years_and_source():
    knowledge = assistant._knowledge_context()
    assert all(f"D{index}:" in knowledge for index in range(1, 9))
    assert "D7" in knowledge and "có từ 2018" in knowledge
    assert assistant.SOURCE in knowledge
    assert "không diễn giải" in knowledge


def test_answer_is_logged_without_execution(client, monkeypatch):
    executed = []
    monkeypatch.setattr(assistant, "generate_reply", lambda *args, **kwargs: {"kind": "answer", "answer": "PAPI phản ánh trải nghiệm của người dân."})
    monkeypatch.setattr(assistant.api_exec, "execute", lambda *args, **kwargs: executed.append(True))

    response = client.post("/api/v1/assistant/messages", json=_message())
    assert response.status_code == 200
    payload = response.json()
    assert payload["kind"] == "answer"
    assert payload["source"] == assistant.SOURCE
    assert executed == []
    events = client.get(f"/api/v1/assistant/logs?sessionId={payload['sessionId']}").json()["events"]
    assert [event["event"] for event in events] == ["request_received", "answer_returned"]


def test_revision_supersedes_old_proposal_and_only_latest_executes(client, monkeypatch):
    replies = iter([
        {"kind": "proposal", "explanation": "Bản đầu", "code": "# Tính mẫu\nresult = prov_year.head(1)"},
        {"kind": "proposal", "explanation": "Bản mới", "code": "# Tính lại\nresult = prov_year.head(2)"},
    ])
    monkeypatch.setattr(assistant, "generate_reply", lambda *args, **kwargs: next(replies))
    monkeypatch.setattr(assistant.api_exec, "execute", lambda code, data: {
        "result": pd.DataFrame({"value": [1, 2]}), "fig": None, "stdout": "ok", "warnings": [], "error": None,
    })

    first = client.post("/api/v1/assistant/messages", json=_message("Tính thử")).json()
    second = client.post("/api/v1/assistant/messages", json=_message("Lấy hai dòng", first["sessionId"], first["proposalId"])).json()
    assert first["proposalId"] != second["proposalId"]
    stale = client.post("/api/v1/assistant/executions", json={"sessionId": first["sessionId"], "proposalId": first["proposalId"], "approved": True})
    assert stale.status_code == 409
    latest = client.post("/api/v1/assistant/executions", json={"sessionId": first["sessionId"], "proposalId": second["proposalId"], "approved": True})
    assert latest.status_code == 200
    assert latest.json()["result"]["totalRows"] == 2
    assert latest.json()["status"] == "succeeded"
    events = client.get(f"/api/v1/assistant/logs?sessionId={first['sessionId']}").json()["events"]
    names = [event["event"] for event in events]
    assert "proposal_superseded" in names
    assert names[-2:] == ["proposal_approved", "execution_succeeded"]


def test_revision_must_target_latest_pending(client, monkeypatch):
    monkeypatch.setattr(assistant, "generate_reply", lambda *args, **kwargs: {"kind": "proposal", "code": "result = prov_year.head()", "explanation": "ok"})
    first = client.post("/api/v1/assistant/messages", json=_message("Tính thử")).json()
    bad = client.post("/api/v1/assistant/messages", json=_message("Sửa", first["sessionId"], "proposal-khac"))
    assert bad.status_code == 409


def test_executor_guard_rejects_file_and_dunder_access():
    with pytest.raises(assistant.ProviderError):
        assistant.normalize_and_validate_code("result = prov_year.to_csv('x.csv')")
    with pytest.raises(assistant.ProviderError):
        assistant.normalize_and_validate_code("result = prov_year.__class__")
    assert assistant.normalize_and_validate_code("import pandas as pd\nresult = prov_year.head()") == "result = prov_year.head()"


def test_result_table_is_bounded_to_500_rows():
    result = assistant._serialize_result(pd.DataFrame({"value": range(501)}))
    assert result["totalRows"] == 501
    assert len(result["rows"]) == 500
    assert result["truncated"] is True


def test_openapi_exposes_three_assistant_contracts_and_post_cors(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "post" in paths["/api/v1/assistant/messages"]
    assert "post" in paths["/api/v1/assistant/executions"]
    assert "get" in paths["/api/v1/assistant/logs"]
    response = client.options(
        "/api/v1/assistant/messages",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
