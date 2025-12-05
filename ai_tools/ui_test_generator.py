from __future__ import annotations

import os
import textwrap
from typing import Any, Dict, List

from playwright.sync_api import sync_playwright

from ai_tools.gemini_client import get_gemini_model


def inspect_page_structure(url: str) -> Dict[str, Any]:
    """
    Use Playwright to open the given URL and extract a compact summary of the UI:
    - title
    - forms
    - inputs (with data-testid/name/placeholder/label)
    - buttons (with text + testid)
    """
    summary: Dict[str, Any] = {
        "url": url,
        "title": "",
        "inputs": [],
        "buttons": [],
        "links": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")

        summary["title"] = page.title()

        # Inputs
        input_locators = page.locator("input, textarea, select")
        for i in range(input_locators.count()):
            el = input_locators.nth(i)
            input_info = {
                "tag": el.evaluate("e => e.tagName.toLowerCase()"),
                "type": el.get_attribute("type") or "",
                "name": el.get_attribute("name") or "",
                "placeholder": el.get_attribute("placeholder") or "",
                "data_testid": el.get_attribute("data-testid") or "",
                "label": "",
            }

            # Try to find label text
            label = el.evaluate(
                """(e) => {
                    const id = e.id;
                    if (id) {
                        const lab = document.querySelector(`label[for="${id}"]`);
                        if (lab) return lab.innerText.trim();
                    }
                    const parentLabel = e.closest('label');
                    if (parentLabel) return parentLabel.innerText.trim();
                    return "";
                }"""
            )
            input_info["label"] = label or ""
            summary["inputs"].append(input_info)

        # Buttons
        button_locators = page.locator("button, [role=button], input[type=submit]")
        for i in range(button_locators.count()):
            el = button_locators.nth(i)
            btn_text = el.inner_text().strip()
            summary["buttons"].append(
                {
                    "tag": el.evaluate("e => e.tagName.toLowerCase()"),
                    "text": btn_text,
                    "data_testid": el.get_attribute("data-testid") or "",
                }
            )

        # Links
        link_locators = page.locator("a[href]")
        for i in range(min(link_locators.count(), 30)):  # cap
            el = link_locators.nth(i)
            summary["links"].append(
                {
                    "text": el.inner_text().strip(),
                    "href": el.get_attribute("href") or "",
                    "data_testid": el.get_attribute("data-testid") or "",
                }
            )

        browser.close()

    return summary


def generate_ui_tests_code(page_summary: Dict[str, Any]) -> str:
    """
    Ask Gemini to generate Python Playwright + pytest tests from the inspected page.
    Returns a Python file content as a string.
    """
    model = get_gemini_model()

    url = page_summary.get("url", "")
    prompt = textwrap.dedent(
        f"""
        You are an expert SDET and Playwright test engineer.
        I will give you a JSON description of a web page (inputs, buttons, links, etc.)
        and you will generate a set of **Python Playwright + pytest** tests for it.

        Requirements:
        - Use Python Playwright sync API with pytest.
        - Assume there is a `page` fixture (from Playwright pytest plugin).
        - Write multiple tests, focusing on realistic user flows.
        - Use selectors that are robust: prefer `data-testid` if available, otherwise text-based selectors.
        - Include at least:
          - one basic "page loads" smoke test,
          - one "happy path" flow (e.g., login or form submission),
          - and one "negative" or edge case test if possible.
        - Use clear test names like `test_login_valid_credentials` etc.
        - Only output pure Python code that can be saved to a `.py` file. No markdown or explanations.

        Here is the page summary JSON (truncated for safety, but assume it's complete):
        {page_summary}
        """
    )

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # If the model accidentally adds ```python fences, strip them.
    if "```" in raw:
        # try to extract between first ``` and last ```
        parts = raw.split("```")
        if len(parts) >= 3:
            # something like: ['', 'python', 'code...', '']
            raw = parts[2].strip()

    return raw


def generate_and_optionally_save_ui_tests(
    url: str,
    output_dir: str = "tests/ui/generated",
    save: bool = True,
    filename_prefix: str = "test_ai_ui_",
) -> Dict[str, Any]:
    """
    High-level function used by API and CLI:
    - Inspect the page with Playwright
    - Ask Gemini to generate pytest+Playwright tests
    - Optionally save a .py file under tests/ui/generated

    Returns:
        dict with fields:
        - url
        - page_summary
        - code
        - saved (bool)
        - saved_path (str or None)
    """
    page_summary = inspect_page_structure(url)
    code = generate_ui_tests_code(page_summary)

    saved_path = None
    if save:
        os.makedirs(output_dir, exist_ok=True)
        safe_slug = (
            url.replace("http://", "")
            .replace("https://", "")
            .replace("/", "_")
            .replace(":", "_")
        )
        filename = f"{filename_prefix}{safe_slug}.py"
        saved_path = os.path.join(output_dir, filename)
        with open(saved_path, "w", encoding="utf-8") as f:
            f.write(code)

    return {
        "url": url,
        "page_summary": page_summary,
        "code": code,
        "saved": bool(save),
        "saved_path": saved_path,
    }


if __name__ == "__main__":
    # CLI usage example:
    result = generate_and_optionally_save_ui_tests("http://127.0.0.1:5173", save=False)
    print(result["code"])
