from conftest import csrf


def register(client, username="testuser", email="test@example.com"):
    token = csrf(client)
    return client.post("/api/create_user", json={
        "user_name": username,
        "password": "secure-password-123",
        "email": email,
        "mobile_number": "9876543210",
        "gender": "Other",
        "dob": "1990-01-15",
    }, headers={"X-CSRF-Token": token})


def login(client, email="test@example.com"):
    token = csrf(client)
    return client.post("/api/users/login", json={
        "email": email,
        "password": "secure-password-123",
    }, headers={"X-CSRF-Token": token})


def test_registration_defaults_to_user(client):
    response = register(client)
    assert response.status_code == 201
    assert response.get_json()["user"]["role"] == "user"


def test_public_registration_cannot_escalate_role(client):
    token = csrf(client)
    response = client.post("/api/create_user", json={
        "user_name": "attacker",
        "password": "secure-password-123",
        "email": "attacker@example.com",
        "mobile_number": "9876543211",
        "gender": "Other",
        "dob": "1990-01-15",
        "role": "ngo",
    }, headers={"X-CSRF-Token": token})
    assert response.status_code == 403


def test_login_and_current_user(client):
    register(client)
    response = login(client)
    assert response.status_code == 200
    me = client.get("/api/users/me")
    assert me.status_code == 200
    assert me.get_json()["user"]["email"] == "test@example.com"


def test_state_change_requires_csrf(client):
    register(client)
    response = client.post("/api/users/logout")
    assert response.status_code == 403


def test_logout_invalidates_session(client):
    register(client)
    login(client)
    token = csrf(client)
    response = client.post("/api/users/logout", headers={"X-CSRF-Token": token})
    assert response.status_code == 200
    assert client.get("/api/users/me").status_code == 401
