

def test_register_and_login(client):
    email = "user_test@example.com"
    password = "Password123!"

    # Registration
    res = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == email
    assert data["role"] == "user"

    # Duplicate registration should return 409
    res_dup = client.post("/api/v1/auth/register", json={"email": email, "password": "NewPassword123!"})
    assert res_dup.status_code == 409
    assert res_dup.json()["error"]["code"] == "DUPLICATE_EMAIL"

    # Login
    res_login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    assert "refresh_token" in res_login.cookies

    # Invalid password login
    res_bad = client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword!"})
    assert res_bad.status_code == 401
    assert res_bad.json()["error"]["code"] == "UNAUTHORIZED"

def test_change_password(client):
    email = "change_pass@example.com"
    password = "OldPassword123!"
    new_password = "NewPassword123!"

    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Wrong current password
    res_wrong = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "WrongOldPassword!", "new_password": new_password},
        headers=headers
    )
    assert res_wrong.status_code == 401
    assert res_wrong.json()["error"]["code"] == "INVALID_CURRENT_PASSWORD"

    # Successful change password
    res_ok = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": password, "new_password": new_password},
        headers=headers
    )
    assert res_ok.status_code == 200

    # Login with new password
    res_new_login = client.post("/api/v1/auth/login", json={"email": email, "password": new_password})
    assert res_new_login.status_code == 200
