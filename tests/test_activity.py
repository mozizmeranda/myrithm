import pytest
from unittest.mock import patch, AsyncMock
from app.models.stream import Stream

@pytest.fixture(autouse=True)
def mock_redis():
    with patch("app.rate_limiter.redis_client.get", new_callable=AsyncMock) as mock_get, \
         patch("app.rate_limiter.redis_client.pipeline") as mock_pipe, \
         patch("app.services.auth_service.add_refresh_token", new_callable=AsyncMock):
        mock_get.return_value = "0"
        pipe_obj = AsyncMock()
        mock_pipe.return_value.__aenter__.return_value = pipe_obj
        yield

def test_activity_sync_and_stats(client, db_session):
    stream = Stream(id="act_stream", title="Activity Stream", is_active=True)
    db_session.add(stream)
    db_session.commit()

    email = "act_user@example.com"
    password = "Password123!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Sync valid activity
    res = client.post(
        "/api/v1/activity/sync",
        json={"stream_id": "act_stream", "duration_seconds": 30, "estimated_steps": 45},
        headers=headers
    )
    assert res.status_code == 201
    assert res.json()["duration_seconds"] == 30
    assert res.json()["estimated_steps"] == 45

    # Invalid duration (>60 seconds) -> INVALID_DURATION 400
    res_bad_dur = client.post(
        "/api/v1/activity/sync",
        json={"stream_id": "act_stream", "duration_seconds": 90, "estimated_steps": 45},
        headers=headers
    )
    assert res_bad_dur.status_code == 400
    assert res_bad_dur.json()["error"]["code"] == "INVALID_DURATION"

    # Get stats
    res_stats = client.get("/api/v1/activity/stats", headers=headers)
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["today_seconds"] == 30
    assert stats["today_estimated_steps"] == 45
    assert len(stats["last_7_days"]) == 7
