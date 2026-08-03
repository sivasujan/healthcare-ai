"""Chat API tests with a mocked model router."""

SYMPTOM_JSON = """{"possible_conditions":[{"name":"Viral infection","confidence":0.6,"severity":"low"}],"overall_severity":"low","recommendations":[{"title":"Rest","detail":"Rest and hydrate"}],"precautions":["Monitor fever"],"doctor_specialty":"General Practitioner","doctor_reason":"Evaluation recommended","emergency_detected":false,"emergency_instructions":null,"disclaimer":"Educational only."}"""


def _auth_headers(client):
    client.post(
        "/api/auth/register",
        json={"full_name": "Chat User", "email": "chat@example.com", "password": "StrongPass1"},
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "chat@example.com", "password": "StrongPass1"},
    ).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_chats(client):
    headers = _auth_headers(client)
    resp = client.post("/api/chat", json={"title": "My Chat"}, headers=headers)
    assert resp.status_code == 201
    chat_id = resp.json()["data"]["id"]

    resp = client.get("/api/chat", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"][0]["id"] == chat_id


def test_chat_send_returns_response(client, mock_router):
    mock_router(
        {
            "symptom_analysis": SYMPTOM_JSON,
            "intent_detection": '{"intent":"symptom_analysis","confidence":0.9}',
            "symptom": SYMPTOM_JSON,
        }
    )
    headers = _auth_headers(client)
    resp = client.post(
        "/api/chat/send",
        json={"message": "I have a fever and headache for 2 days"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["chat_id"]
    assert data["agent"] == "symptom_analysis"
    assert data["response"]


def test_chat_history_persisted(client, mock_router):
    mock_router(
        {
            "intent_detection": '{"intent":"general","confidence":0.9}',
            "general": "Hello! How can I help?",
        }
    )
    headers = _auth_headers(client)
    resp = client.post(
        "/api/chat/send",
        json={"message": "Hello there"},
        headers=headers,
    )
    chat_id = resp.json()["data"]["chat_id"]

    history = client.get(f"/api/chat/history/{chat_id}", headers=headers)
    assert history.status_code == 200
    roles = [m["role"] for m in history.json()["data"]["messages"]]
    assert roles == ["user", "assistant"]


def test_chat_delete(client, mock_router):
    mock_router(
        {
            "intent_detection": '{"intent":"general","confidence":0.9}',
            "general": "OK",
        }
    )
    headers = _auth_headers(client)
    chat_id = client.post(
        "/api/chat/send", json={"message": "Hi"}, headers=headers
    ).json()["data"]["chat_id"]

    resp = client.delete(f"/api/chat/{chat_id}", headers=headers)
    assert resp.status_code == 200
    assert client.get(f"/api/chat/history/{chat_id}", headers=headers).status_code == 404


def test_stream_endpoint(client, mock_router):
    mock_router(
        {
            "intent_detection": '{"intent":"general","confidence":0.9}',
            "general": "Streamed answer",
        }
    )
    headers = _auth_headers(client)
    with client.stream(
        "POST", "/api/chat/stream", json={"message": "Tell me about health"}, headers=headers
    ) as resp:
        assert resp.status_code == 200
        body = "".join(resp.iter_text())
    assert "done" in body
