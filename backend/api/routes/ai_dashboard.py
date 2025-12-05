from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from ai_tools.test_generator import generate_test_cases_from_openapi
from ai_tools.ai_test_executor import execute_ai_tests
from ai_tools.failure_analyzer import analyze_failures_api

router = APIRouter(prefix="/ai/dashboard", tags=["ai-dashboard"])


@router.get("/generated-tests")
def get_generated_tests(
    max_endpoints: int = Query(10, ge=1, le=50),
) -> Any:
    """
    Return AI-generated test cases (same logic as /ai/generate-tests, but for dashboard use).
    """
    try:
        cases = generate_test_cases_from_openapi(
            base_url="http://127.0.0.1:8000",
            max_endpoints=max_endpoints,
        )
        return {"count": len(cases), "items": cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-tests")
def execute_tests(
    max_endpoints: int = Query(10, ge=1, le=50),
) -> Dict[str, Any]:
    """
    Run AI-executed tests and return summary + per-test results.
    """
    try:
        data = execute_ai_tests(
            base_url="http://127.0.0.1:8000",
            max_endpoints=max_endpoints,
            use_auth=True,
            config_path="tests/api/config/config.yaml",
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze-failures")
def analyze_failures(
    xml_path: str = Query("reports/api-results.xml"),
) -> Dict[str, Any]:
    """
    Analyze failures from a pytest JUnit XML and return AI-written analysis.
    """
    try:
        data = analyze_failures_api(xml_path)
        return data
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"JUnit XML not found at {xml_path}. Run pytest with --junitxml first.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
