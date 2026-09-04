from app.models.user import User
from app.security import hash_password

def test_admin_flow(client, db_session):
    admin_email = "admin_test@example.com"
    admin_pass = "AdminPass123!"

    admin_user = User(email=admin_email, password_hash=hash_password(admin_pass), role="admin")
    db_session.add(admin_user)
    db_session.commit()

    # Admin Login
    login_res = client.post("/api/v1/admin/auth/login", json={"email": admin_email, "password": admin_pass})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Stream
    s_res = client.post(
        "/api/v1/admin/streams",
        json={"id": "adm_cardio", "title": "Admin Cardio", "description": "Desc", "is_active": True},
        headers=headers
    )
    assert s_res.status_code == 201
    assert s_res.json()["id"] == "adm_cardio"

    # Create Exercise
    e_res = client.post(
        "/api/v1/admin/exercises",
        json={
            "stream_id": "adm_cardio",
            "title": "Warmup",
            "video_url": "/media/videos/1234567890ab.mp4",
            "duration": 60,
            "steps_per_minute": 100,
            "sort_order": 1,
            "is_active": True
        },
        headers=headers
    )
    assert e_res.status_code == 201
    exercise_id = e_res.json()["id"]

    # Create Track
    t_res = client.post(
        "/api/v1/admin/tracks",
        json={
            "stream_id": "adm_cardio",
            "title": "Energetic Music",
            "audio_url": "/media/audio/1234567890ab.mp3",
            "duration": 180,
            "sort_order": 1,
            "is_active": True
        },
        headers=headers
    )
    assert t_res.status_code == 201
    track_id = t_res.json()["id"]

    # Admin stats
    stats_res = client.get("/api/v1/admin/stats", headers=headers)
    assert stats_res.status_code == 200
    assert "total_users" in stats_res.json()

    # Delete Exercise & Track
    del_e = client.delete(f"/api/v1/admin/exercises/{exercise_id}", headers=headers)
    assert del_e.status_code == 200

    del_t = client.delete(f"/api/v1/admin/tracks/{track_id}", headers=headers)
    assert del_t.status_code == 200

    # Now delete Stream
    del_s = client.delete("/api/v1/admin/streams/adm_cardio", headers=headers)
    assert del_s.status_code == 200
