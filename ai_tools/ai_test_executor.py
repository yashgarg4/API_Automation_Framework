import argparse
import os
import sys
from typing import Any, Dict, List, Optional

import requests
import yaml

from ai_tools.test_generator import generate_test_cases_from_openapi


def load_api_config(config_path: str = "tests/api/config/config.yaml") -> Dict[str, Any]:
    """
    Load API test config to reuse default user credentials.
    """
    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_auth_token(base_url: str, email: str, password: str) -> Optional[str]:
    """
    Perform login via /auth/login and return access token.
    """
    url = f"{base_url.rstrip('/')}/auth/login"
    data = {
        "username": email,
        "password": password,
    }

    resp = requests.post(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )

    if not resp.ok:
        print(f"[AUTH] Login failed: {resp.status_code} {resp.text}")
        return None

    try:
        token = resp.json()["access_token"]
        print(f"[AUTH] Login successful for {email}")
        return token
    except Exception as e:
        print(f"[AUTH] Failed to parse access token: {e}")
        return None


def infer_expected_result(category: str, status_code: int) -> bool:
    """
    Simple heuristic:
    - positive / edge: expect 2xx
    - negative: expect >=400
    """
    cat = (category or "").lower()
    if cat == "negative":
        return status_code >= 400
    # positive or edge (or unknown)
    return 200 <= status_code < 300


def execute_ai_tests(
    base_url: str,
    max_endpoints: int = 10,
    use_auth: bool = True,
    config_path: str = "tests/api/config/config.yaml",
) -> Dict[str, Any]:
    """
    Core executor used by both CLI and API.
    Returns structured data instead of exiting.
    """
    token = None
    config = load_api_config(config_path) if use_auth else {}
    default_user = config.get("default_user") if config else None

    if use_auth and default_user:
        email = default_user.get("email")
        pwd = default_user.get("password")
        if email and pwd:
            token = get_auth_token(base_url, email, pwd)

    # Generate AI test cases
    test_cases = generate_test_cases_from_openapi(
        base_url=base_url,
        max_endpoints=max_endpoints,
    )

    session = requests.Session()
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})

    results: List[Dict[str, Any]] = []

    for idx, tc in enumerate(test_cases, start=1):
        name = tc.get("name", f"test_{idx}")
        category = tc.get("category", "positive")
        request_spec = tc.get("request", {}) or {}

        method = (request_spec.get("method") or "GET").upper()
        path = request_spec.get("path") or "/"
        body = request_spec.get("body", None)

        url = f"{base_url.rstrip('/')}{path}"

        entry: Dict[str, Any] = {
            "index": idx,
            "name": name,
            "category": category,
            "method": method,
            "path": path,
            "request_body": body,
            "status_code": None,
            "passed": False,
            "error": None,
        }

        try:
            kwargs: Dict[str, Any] = {"timeout": 15}
            if method in ("POST", "PUT", "PATCH"):
                kwargs["json"] = body

            resp = session.request(method, url, **kwargs)
            status_code = resp.status_code
            entry["status_code"] = status_code
            entry["passed"] = infer_expected_result(category, status_code)
        except Exception as e:
            entry["error"] = str(e)
            entry["passed"] = False

        results.append(entry)

    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = total - passed_count

    summary = {
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "base_url": base_url,
        "max_endpoints": max_endpoints,
        "used_auth": use_auth and bool(default_user),
    }

    return {
        "summary": summary,
        "results": results,
    }


def run_ai_tests(
    base_url: str,
    max_endpoints: int = 10,
    use_auth: bool = True,
    config_path: str = "tests/api/config/config.yaml",
) -> int:
    """
    CLI wrapper around execute_ai_tests.
    Prints to console and returns exit code.
    """
    print(f"[EXECUTOR] Base URL: {base_url}")
    print(f"[EXECUTOR] Max endpoints: {max_endpoints}")
    print(f"[EXECUTOR] Use auth: {use_auth}")

    data = execute_ai_tests(
        base_url=base_url,
        max_endpoints=max_endpoints,
        use_auth=use_auth,
        config_path=config_path,
    )

    summary = data["summary"]
    results = data["results"]

    for r in results:
        idx = r["index"]
        name = r["name"]
        method = r["method"]
        path = r["path"]
        category = r["category"]
        status_code = r["status_code"]
        passed = r["passed"]
        error = r["error"]

        print(f"[{idx}] {name}")
        print(f"     Endpoint: {method} {path}")
        print(f"     Category: {category}")
        if error:
            print(f"     ERROR: {error}")
        else:
            print(f"     HTTP {status_code} → {'PASS' if passed else 'FAIL'}")
        print()

    print("=== AI Test Execution Summary ===")
    print(f"Total tests:  {summary['total']}")
    print(f"Passed tests: {summary['passed']}")
    print(f"Failed tests: {summary['failed']}")
    print("==========")

    return 0 if summary["failed"] == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="AI Test Executor - Run Gemini-generated API tests against FastAPI backend."
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://127.0.0.1:8000",
        help="Base URL of the FastAPI backend",
    )
    parser.add_argument(
        "--max-endpoints",
        type=int,
        default=10,
        help="Maximum number of endpoints from OpenAPI to generate tests for",
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Disable auth even if default_user exists in config",
    )
    parser.add_argument(
        "--config-path",
        type=str,
        default="tests/api/config/config.yaml",
        help="Path to API test config YAML (for default_user credentials)",
    )

    args = parser.parse_args()

    exit_code = run_ai_tests(
        base_url=args.base_url,
        max_endpoints=args.max_endpoints,
        use_auth=not args.no_auth,
        config_path=args.config_path,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
