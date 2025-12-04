import pytest


@pytest.fixture
def project(api_client, auth_headers):
    payload = {
        "name": "Bug Lifecycle Project",
        "description": "For bug lifecycle tests",
    }
    r = api_client.post("/projects/", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture
def bug(api_client, auth_headers, project):
    project_id = project["id"]
    payload = {
        "title": "Sample bug",
        "description": "Bug created for lifecycle testing",
        "severity": "high",
        "priority": "high",
        "assignee_id": None,
    }
    r = api_client.post(f"/projects/{project_id}/bugs", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_bug_creation_and_listing(api_client, auth_headers, project, bug):
    project_id = project["id"]

    # Bug from fixture
    assert bug["title"] == "Sample bug"
    assert bug["status"] == "open"
    bug_id = bug["id"]

    # List bugs for project
    r = api_client.get(f"/projects/{project_id}/bugs", headers=auth_headers)
    assert r.status_code == 200, r.text
    bugs = r.json()
    assert any(b["id"] == bug_id for b in bugs)


def test_bug_status_valid_transitions(api_client, auth_headers, bug):
    bug_id = bug["id"]

    # open -> in_progress
    r1 = api_client.patch(
        f"/bugs/{bug_id}/status",
        json={"status": "in_progress"},
        headers=auth_headers,
    )
    assert r1.status_code == 200, r1.text
    assert r1.json()["status"] == "in_progress"

    # in_progress -> resolved
    r2 = api_client.patch(
        f"/bugs/{bug_id}/status",
        json={"status": "resolved"},
        headers=auth_headers,
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["status"] == "resolved"

    # resolved -> closed
    r3 = api_client.patch(
        f"/bugs/{bug_id}/status",
        json={"status": "closed"},
        headers=auth_headers,
    )
    assert r3.status_code == 200, r3.text
    assert r3.json()["status"] == "closed"


def test_bug_status_invalid_transition(api_client, auth_headers, project):
    # Create a fresh bug
    project_id = project["id"]
    payload = {
        "title": "Invalid transition bug",
        "description": "Test invalid status change",
        "severity": "medium",
        "priority": "medium",
        "assignee_id": None,
    }
    r = api_client.post(f"/projects/{project_id}/bugs", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    bug = r.json()
    bug_id = bug["id"]
    assert bug["status"] == "open"

    # Try invalid transition: open -> closed directly
    r_invalid = api_client.patch(
        f"/bugs/{bug_id}/status",
        json={"status": "closed"},
        headers=auth_headers,
    )
    assert r_invalid.status_code == 400
    assert "Invalid status transition" in r_invalid.text
