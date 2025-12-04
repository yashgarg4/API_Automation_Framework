from playwright.sync_api import Page


class ProjectsPage:
    def __init__(self, page: Page):
        self.page = page

    def create_project(self, name: str, description: str):
        self.page.fill('[data-testid="project-name"]', name)
        self.page.fill('[data-testid="project-description"]', description)
        self.page.click('[data-testid="create-project-button"]')
        # After creating, we reload list
        self.page.click('[data-testid="load-projects-button"]')

    def select_project_by_name(self, name: str):
        # Ensure list is loaded
        self.page.click('[data-testid="load-projects-button"]')
        self.page.locator('li[data-testid="project-item"]', has_text=name).first.click()

    def assert_current_project_name_contains(self, text: str):
        locator = self.page.get_by_test_id("current-project-name")
        locator.wait_for(timeout=5000)
        assert text in locator.inner_text()
