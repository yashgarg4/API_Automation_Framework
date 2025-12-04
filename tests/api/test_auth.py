def test_register_and_login_flow(api_client, unique_email, config):
    # Register
    register_payload = {
        "email": unique_email,
        "full_name": "Test User",
        "password": config["default_user"]["password"],
    }
    r = api_client.post("/auth/register", json=register_payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["email"] == unique_email
    assert data["is_active"] is True
    assert data["role"] == "tester"

    # Login
    login_data = {
        "username": unique_email,
        "password": config["default_user"]["password"],
    }
    r2 = api_client.post("/auth/login", data=login_data)
    assert r2.status_code == 200, r2.text
    token_data = r2.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_with_wrong_password(api_client, registered_user, config):
    login_data = {
        "username": registered_user["email"],
        "password": "wrongpassword",
    }
    r = api_client.post("/auth/login", data=login_data)
    assert r.status_code == 400
    assert "Incorrect email or password" in r.text
