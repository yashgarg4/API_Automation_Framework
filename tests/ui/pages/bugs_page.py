from playwright.sync_api import Page


class BugsPage:
    def __init__(self, page: Page):
        self.page = page

    def create_bug(self, title: str, description: str, severity: str = "medium", priority: str = "medium"):
        self.page.fill('[data-testid="bug-title"]', title)
        self.page.fill('[data-testid="bug-description"]', description)
        self.page.select_option('[data-testid="bug-severity"]', severity)
        self.page.select_option('[data-testid="bug-priority"]', priority)
        self.page.click('[data-testid="create-bug-button"]')
        # Reload bugs
        self.page.click('[data-testid="load-bugs-button"]')

    def assert_bug_list_contains(self, title: str):
        self.page.click('[data-testid="load-bugs-button"]')
        self.page.locator('li[data-testid="bug-item"]', has_text=title).first.wait_for(timeout=5000)
