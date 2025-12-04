import uuid
from playwright.sync_api import Page

from .pages.login_page import LoginPage
from .pages.projects_page import ProjectsPage
from .pages.bugs_page import BugsPage


def test_e2e_create_project_and_bug(page: Page, base_url: str):
    """
    Full UI flow:
    - open /app
    - register unique user
    - login
    - create project
    - select project
    - create bug
    - verify bug appears in list
    """
    login_page = LoginPage(page, base_url)
    projects_page = ProjectsPage(page)
    bugs_page = BugsPage(page)

    # Use unique email so tests can run repeatedly
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"ui_tester+{unique_suffix}@example.com"
    password = "ui-test-password"
    full_name = "UI Test User"

    # Go to app & register
    login_page.goto()
    login_page.register(email=email, full_name=full_name, password=password)

    # Login
    login_page.login(email=email, password=password)
    login_page.assert_logged_in_as(email)

    # Create a project
    project_name = f"UI Project {unique_suffix}"
    projects_page.create_project(name=project_name, description="Created via UI automation")
    projects_page.select_project_by_name(project_name)
    projects_page.assert_current_project_name_contains(project_name)

    # Create a bug in this project
    bug_title = f"UI bug {unique_suffix}"
    bugs_page.create_bug(
        title=bug_title,
        description="Bug created via UI E2E test",
        severity="high",
        priority="high",
    )
    bugs_page.assert_bug_list_contains(bug_title)
