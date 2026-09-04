

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
