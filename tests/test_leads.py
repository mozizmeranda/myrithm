import pytest
from unittest.mock import patch, AsyncMock

@pytest.fixture(autouse=True)
def mock_redis():
    with patch("app.rate_limiter.redis_client.get", new_callable=AsyncMock) as mock_get, \
         patch("app.rate_limiter.redis_client.pipeline") as mock_pipe, \
         patch("app.services.lead_service.increment_lead_counter", new_callable=AsyncMock):
        mock_get.return_value = "0"
        pipe_obj = AsyncMock()
        mock_pipe.return_value.__aenter__.return_value = pipe_obj
        yield

def test_create_lead(client):
    res = client.post("/api/v1/leads", json={"email": "lead_user@example.com", "stream_code": "dance"})
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "lead_user@example.com"
    assert data["stream_code"] == "dance"
