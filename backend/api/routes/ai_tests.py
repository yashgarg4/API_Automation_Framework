from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query

from ai_tools.test_generator import generate_test_cases_from_openapi

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/generate-tests", response_model=List[Dict[str, Any]])
def generate_tests(
    max_endpoints: int = Query(10, ge=1, le=50),
):
    """
    Use Gemini + OpenAPI schema to generate suggested API test cases.
    NOTE: Requires GEMINI_API_KEY env var and outbound internet access.
    """
    try:
        cases = generate_test_cases_from_openapi(
            base_url="http://127.0.0.1:8000",
            max_endpoints=max_endpoints,
        )
        return cases
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
