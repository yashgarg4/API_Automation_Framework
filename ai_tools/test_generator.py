import json
import requests
from typing import Any, Dict, List

from ai_tools.gemini_client import get_gemini_model


def fetch_openapi_schema(base_url: str = "http://127.0.0.1:8000") -> Dict[str, Any]:
    """
    Fetch the OpenAPI schema from the running FastAPI app.
    Make sure the app is running before calling this.
    """
    resp = requests.get(f"{base_url.rstrip('/')}/openapi.json", timeout=10)
    resp.raise_for_status()
    return resp.json()


def generate_test_cases_from_openapi(
    base_url: str = "http://127.0.0.1:8000",
    max_endpoints: int = 10,
) -> List[Dict[str, Any]]:
    schema = fetch_openapi_schema(base_url)
    paths = schema.get("paths", {})

    # Pre-select a subset of endpoints to avoid huge prompts
    selected_paths = {}
    for i, (path, methods) in enumerate(paths.items()):
        if i >= max_endpoints:
            break
        selected_paths[path] = methods

    model = get_gemini_model()

    prompt = (
        "You are an expert SDET. Given this OpenAPI snippet, generate a list of high-quality API test cases.\n\n"
        "Return ONLY valid JSON, no markdown, in this format:\n"
        "[\n"
        "  {\n"
        '    "name": "short human-readable test name",\n'
        '    "endpoint": "HTTP_METHOD PATH",\n'
        '    "category": "positive" | "negative" | "edge",\n'
        '    "preconditions": ["..."],\n'
        '    "request": {\n'
        '        "method": "GET/POST/PUT/... etc",\n'
        '        "path": "/example",\n'
        '        "body": { ... },\n'
        '        "requires_auth": true/false\n'
        "    },\n"
        '    "expected": ["list of expected outcomes, status codes, body checks"]\n'
        "  }\n"
        "]\n\n"
        "OpenAPI snippet:\n"
        f"{json.dumps(selected_paths, indent=2)}"
    )

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Try to parse JSON from the model response
    try:
        test_cases = json.loads(raw_text)
    except json.JSONDecodeError:
        # Best-effort: try to extract JSON between first [ and last ]
        start = raw_text.find("[")
        end = raw_text.rfind("]")
        if start != -1 and end != -1:
            json_str = raw_text[start : end + 1]
            test_cases = json.loads(json_str)
        else:
            raise ValueError("Could not parse JSON from Gemini response")

    if not isinstance(test_cases, list):
        raise ValueError("Model did not return a list of test cases")

    return test_cases


if __name__ == "__main__":
    # CLI usage example
    cases = generate_test_cases_from_openapi()
    print(json.dumps(cases, indent=2))
