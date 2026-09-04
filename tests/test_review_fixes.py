import pytest
from app.models.user import User
from app.models.stream import Stream
from app.security import hash_password, create_refresh_token, create_access_token
from app.services.media_service import MediaService

def test_c3_refresh_token_rejected_as_access_token(client, db_session):
    email = "c3_test@example.com"
    password = "Password123!"
    user = User(email=email, password_hash=hash_password(password), role="user")
    db_session.add(user)
    db_session.commit()

    # Generate a refresh token
    refresh_token, _, _ = create_refresh_token(user.id)

    # Try using refresh_token in Bearer Authorization header
    res = client.get("/api/v1/user/profile", headers={"Authorization": f"Bearer {refresh_token}"})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "UNAUTHORIZED"

def test_h2_email_case_insensitivity_normalization(client):
    email_upper = "CaseUser@Example.com"
    email_lower = "caseuser@example.com"
    password = "Password123!"

    # Register with uppercase email
    res1 = client.post("/api/v1/auth/register", json={"email": email_upper, "password": password})
    assert res1.status_code == 201
    assert res1.json()["email"] == email_lower

    # Register with lowercase email should be rejected as duplicate
    res2 = client.post("/api/v1/auth/register", json={"email": email_lower, "password": password})
    assert res2.status_code == 409

    # Login with mixed case email should succeed
    login_res = client.post("/api/v1/auth/login", json={"email": "CASEUSER@EXAMPLE.COM", "password": password})
    assert login_res.status_code == 200

def test_h7_admin_login_rejects_regular_user_without_issuing_token(client, db_session):
    user_email = "regular_user@example.com"
    user_pass = "Password123!"
    user = User(email=user_email, password_hash=hash_password(user_pass), role="user")
    db_session.add(user)
    db_session.commit()

    # Regular user attempting admin login
    res = client.post("/api/v1/admin/auth/login", json={"email": user_email, "password": user_pass})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "UNAUTHORIZED"
    assert "refresh_token" not in res.cookies

def test_c4_media_service_prevents_path_traversal():
    ref_count_fn = lambda url: 0
    # Traversal URL should be safely ignored and not raise or delete system files
    MediaService.delete_local_file_if_unused("/media/../victim.txt", ref_count_fn)
    MediaService.delete_local_file_if_unused("/media/videos/../../etc/passwd", ref_count_fn)
