from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.test_run import TestRun as TestRunSchema
from backend.crud.test_run import (
    create_test_run,
    finish_test_run,
    list_test_runs,
)
from ai_tools.test_generator import generate_test_cases_from_openapi
from ai_tools.ai_test_executor import execute_ai_tests
from ai_tools.failure_analyzer import analyze_failures_api

router = APIRouter(prefix="/ai/dashboard", tags=["ai-dashboard"])

@router.get("/generated-tests")
def get_generated_tests(
    max_endpoints: int = Query(10, ge=1, le=50),
) -> Any:
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
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Run AI-executed tests, persist the run in DB, and return summary + results.
    """
    # create DB record (status = running)
    test_run = create_test_run(db, run_type="ai_executor", status="running")

    try:
        data = execute_ai_tests(
            base_url="http://127.0.0.1:8000",
            max_endpoints=max_endpoints,
            use_auth=True,
            config_path="tests/api/config/config.yaml",
        )

        summary = data.get("summary", {})
        results = data.get("results", [])

        status = "passed" if summary.get("failed", 0) == 0 else "failed"
        test_run = finish_test_run(db, test_run, status=status, summary=summary, results=results)

        return {
            "test_run_id": test_run.id,
            "summary": summary,
            "results": results,
        }

    except Exception as e:
        # mark run as error
        finish_test_run(
            db,
            test_run,
            status="error",
            summary={"error": str(e)},
            results=[],
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-runs", response_model=List[TestRunSchema])
def get_test_runs(
    limit: int = Query(10, ge=1, le=100),
    run_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    List recent test runs (default: AI executor runs).
    """
    runs = list_test_runs(db, run_type=run_type, limit=limit)
    return runs


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
