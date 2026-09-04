from app.models.stream import Stream

def test_create_lead(client, db_session):
    stream = Stream(id="dance", title="Dance Workout", is_active=True)
    db_session.add(stream)
    db_session.commit()

    res = client.post("/api/v1/leads", json={"email": "lead_user@example.com", "stream_code": "dance"})
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "lead_user@example.com"
    assert data["stream_code"] == "dance"

