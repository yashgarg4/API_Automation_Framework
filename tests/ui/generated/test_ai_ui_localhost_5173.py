import pytest
import time
from playwright.sync_api import Page, expect

# Define the base URL for the application
BASE_URL = "http://localhost:5173"

def test_page_loads_successfully(page: Page):
    """
    Smoke test to verify that the application page loads, has the correct title,
    and a key element like the registration button is visible.
    """
    page.goto(BASE_URL)
    expect(page).to_have_title("frontend")
    expect(page.get_by_test_id("register-button")).to_be_visible()
    expect(page.get_by_test_id("login-button")).to_be_visible()

def test_successful_registration(page: Page):
    """
    Tests the happy path for user registration.
    Uses a unique email each run and asserts the success message shown in the UI.
    """
    page.goto(BASE_URL)

    # Use a unique email so test is not flaky on repeated runs
    unique_email = f"newuser_{int(time.time())}@example.com"

    # Fill out the registration form
    page.get_by_test_id("register-email").fill(unique_email)
    page.get_by_test_id("register-fullname").fill("New Test User")
    page.get_by_test_id("register-password").fill("SecurePass123!")

    # Click the Register button
    page.get_by_test_id("register-button").click()

    # Assert that success message appears (AuthSection sets this on success)
    expect(page.get_by_text("Registered successfully")).to_be_visible()

def test_successful_login(page: Page):
    """
    Tests the happy path for user login.
    Assumes the credentials belong to an existing user and checks
    for the 'Login successful' status message.
    """
    page.goto(BASE_URL)

    # TODO: Replace with real existing user credentials
    valid_email = "tester@example.com"
    valid_password = "test1234"

    # Fill out the login form
    page.get_by_test_id("login-email").fill(valid_email)
    page.get_by_test_id("login-password").fill(valid_password)

    # Click the Login button
    page.get_by_test_id("login-button").click()

    # Assert the success message appears
    expect(page.get_by_text("Login successful")).to_be_visible()

def test_registration_with_empty_fields(page: Page):
    """
    Tests a negative scenario: attempting to register with no information provided.
    We expect the registration to fail, meaning the register button should
    still be visible and no successful state change should occur.
    """
    page.goto(BASE_URL)

    # Do not fill any fields.
    # Click the Register button
    page.get_by_test_id("register-button").click()

    # Assert that the Register button is still visible, indicating no successful submission.
    expect(page.get_by_test_id("register-button")).to_be_visible()
    # If specific error messages were expected (e.g., "Email is required"),
    # we would assert their visibility here.

def test_login_with_invalid_credentials(page: Page):
    """
    Tests a negative scenario: attempting to log in with incorrect credentials.
    We expect the login to fail, meaning the login button should
    still be visible and no successful state change should occur.
    """
    page.goto(BASE_URL)

    # Fill out the login form with invalid credentials
    page.get_by_test_id("login-email").fill("unknown@example.com")
    page.get_by_test_id("login-password").fill("wrongpass")

    # Click the Login button
    page.get_by_test_id("login-button").click()

    # Assert that the Login button is still visible, indicating unsuccessful login.
    expect(page.get_by_test_id("login-button")).to_be_visible()
    # If an error message (e.g., "Invalid credentials") was expected,
    # we would assert its visibility here.

def test_interaction_with_url_inspect_input(page: Page):
    """
    Tests interaction with the text input field intended for URL inspection.
    This field lacks a data-testid and a label, so we use its placeholder text.
    """
    page.goto(BASE_URL)

    url_input_placeholder = "URL to inspect, e.g. http://127.0.0.1:5173"
    url_input_field = page.get_by_placeholder(url_input_placeholder)

    test_url_value = "https://playwright.dev"
    url_input_field.fill(test_url_value)

    # Assert that the value has been correctly set
    expect(url_input_field).to_have_value(test_url_value)

def test_click_generate_ui_tests_button(page: Page):
    """
    Tests clicking a button that does not have a data-testid,
    using its text content for selection.
    """
    page.goto(BASE_URL)

    # Select the button by its exact text content
    generate_button = page.get_by_text("Generate UI Tests", exact=True)
    expect(generate_button).to_be_visible()

    generate_button.click()

    # Without further information on post-click state, we just assert the button
    # remains visible, indicating the page didn't navigate away unexpectedly.
    # A real test would check for a specific result (e.g., a modal appearing,
    # a new element, or a log entry).
    expect(generate_button).to_be_visible()