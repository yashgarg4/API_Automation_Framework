from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def goto(self):
        self.page.goto(f"{self.base_url}/app")

    def register(self, email: str, full_name: str, password: str):
        self.page.fill('[data-testid="register-email"]', email)
        self.page.fill('[data-testid="register-fullname"]', full_name)
        self.page.fill('[data-testid="register-password"]', password)
        self.page.click('[data-testid="register-button"]')
        # Wait for some visible feedback
        self.page.get_by_text("Registered:", exact=False).wait_for(timeout=5000)

    def login(self, email: str, password: str):
        self.page.fill('[data-testid="login-email"]', email)
        self.page.fill('[data-testid="login-password"]', password)
        self.page.click('[data-testid="login-button"]')
        # Wait for status
        self.page.get_by_text("Login successful").wait_for(timeout=5000)

    def assert_logged_in_as(self, email: str):
        self.page.get_by_text(f"Logged in as: {email}").wait_for(timeout=5000)
