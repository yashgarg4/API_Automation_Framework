def test_create_and_list_projects(api_client, auth_headers):
    # Create a project
    project_payload = {
        "name": "API Test Project",
        "description": "Project created via API tests",
    }
    r = api_client.post("/projects/", json=project_payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    project = r.json()
    assert project["name"] == project_payload["name"]
    assert project["description"] == project_payload["description"]
    project_id = project["id"]

    # List projects
    r2 = api_client.get("/projects/", headers=auth_headers)
    assert r2.status_code == 200, r2.text
    projects = r2.json()
    assert any(p["id"] == project_id for p in projects)


def test_get_update_delete_project(api_client, auth_headers):
    # Create a project first
    payload = {"name": "Temp Project", "description": "To be updated"}
    r = api_client.post("/projects/", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    project = r.json()
    project_id = project["id"]

    # Get project
    r_get = api_client.get(f"/projects/{project_id}", headers=auth_headers)
    assert r_get.status_code == 200, r_get.text
    assert r_get.json()["id"] == project_id

    # Update project
    update_payload = {"name": "Updated Project", "description": "Updated description"}
    r_put = api_client.put(f"/projects/{project_id}", json=update_payload, headers=auth_headers)
    assert r_put.status_code == 200, r_put.text
    updated = r_put.json()
    assert updated["name"] == "Updated Project"
    assert updated["description"] == "Updated description"

    # Delete project
    r_del = api_client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert r_del.status_code == 204, r_del.text

    # Verify 404 after delete
    r_get2 = api_client.get(f"/projects/{project_id}", headers=auth_headers)
    assert r_get2.status_code == 404
