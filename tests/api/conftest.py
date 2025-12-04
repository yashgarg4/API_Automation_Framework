import os
import uuid
import yaml
import pytest

from typing import Dict

from .utils.api_client import APIClient


@pytest.fixture(scope="session")
def config() -> Dict:
    """
    Load YAML config once per test session.
    """
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def base_url(config) -> str:
    return config["base_url"]


@pytest.fixture(scope="session")
def api_client(base_url: str) -> APIClient:
    return APIClient(base_url=base_url)


@pytest.fixture
def unique_email(config) -> str:
    """
    Generate a unique email per test to avoid clashes.
    """
    default_email = config["default_user"]["email"]
    local, domain = default_email.split("@")
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{local}+{unique_suffix}@{domain}"


@pytest.fixture
def registered_user(api_client: APIClient, unique_email: str, config):
    """
    Register a user for the test and return its data.
    """
    payload = {
        "email": unique_email,
        "full_name": config["default_user"]["full_name"],
        "password": config["default_user"]["password"],
    }
    resp = api_client.post("/auth/register", json=payload)
    # For debugging if needed:
    assert resp.status_code == 200, f"Register failed: {resp.status_code}, {resp.text}"
    return resp.json()


@pytest.fixture
def access_token(api_client: APIClient, registered_user, config) -> str:
    """
    Login the registered user and return JWT access token.
    """
    login_data = {
        "username": registered_user["email"],
        "password": config["default_user"]["password"],
    }
    # OAuth2 login expects form data, not JSON
    resp = api_client.post("/auth/login", data=login_data)
    assert resp.status_code == 200, f"Login failed: {resp.status_code}, {resp.text}"
    token = resp.json()["access_token"]
    return token


@pytest.fixture
def auth_headers(access_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}
