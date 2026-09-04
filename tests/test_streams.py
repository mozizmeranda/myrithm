import pytest
from app.models.stream import Stream

def test_streams_and_content(client, db_session):
    # Seed a test stream
    stream_active = Stream(id="test_cardio", title="Test Cardio", description="Active test stream", is_active=True)
    stream_inactive = Stream(id="test_dance", title="Test Dance", description="Inactive test stream", is_active=False)
    db_session.add_all([stream_active, stream_inactive])
    db_session.commit()

    # Get all streams
    res = client.get("/api/v1/streams")
    assert res.status_code == 200
    streams = res.json()
    assert len(streams) >= 2

    # Active stream content
    res_active = client.get("/api/v1/streams/test_cardio/content")
    assert res_active.status_code == 200
    assert res_active.json()["stream_id"] == "test_cardio"

    # Inactive stream content -> 403 STREAM_INACTIVE
    res_inactive = client.get("/api/v1/streams/test_dance/content")
    assert res_inactive.status_code == 403
    assert res_inactive.json()["error"]["code"] == "STREAM_INACTIVE"

    # Non-existent stream -> 404 STREAM_NOT_FOUND
    res_404 = client.get("/api/v1/streams/non_existent/content")
    assert res_404.status_code == 404
    assert res_404.json()["error"]["code"] == "STREAM_NOT_FOUND"
