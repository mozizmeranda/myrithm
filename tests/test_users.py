import pytest
from unittest.mock import patch, AsyncMock

@pytest.fixture(autouse=True)
def mock_redis():
    with patch("app.rate_limiter.redis_client.get", new_callable=AsyncMock) as mock_get, \
         patch("app.rate_limiter.redis_client.pipeline") as mock_pipe, \
         patch("app.services.auth_service.add_refresh_token", new_callable=AsyncMock):
        mock_get.return_value = "0"
        pipe_obj = AsyncMock()
        mock_pipe.return_value.__aenter__.return_value = pipe_obj
        yield

def test_user_profile(client):
    email = "profile_user@example.com"
    password = "ProfilePassword123!"

    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]

    res = client.get("/api/v1/user/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == email
    assert "total_duration_seconds" in data
    assert "total_estimated_steps" in data
    assert "total_sessions" in data
