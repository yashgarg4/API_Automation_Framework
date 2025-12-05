from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai_tools.ui_test_generator import generate_and_optionally_save_ui_tests


class UiTestGenRequest(BaseModel):
    url: str
    save: bool = True


class UiTestGenResponse(BaseModel):
    url: str
    saved: bool
    saved_path: str | None
    code: str


router = APIRouter(prefix="/ai/ui", tags=["ai-ui"])


@router.post("/generate-tests", response_model=UiTestGenResponse)
def generate_ui_tests(req: UiTestGenRequest) -> Dict[str, Any]:
    """
    Generate Python Playwright pytest UI tests for a given URL using Gemini,
    optionally saving them under tests/ui/generated/.
    """
    try:
        result = generate_and_optionally_save_ui_tests(
            url=req.url,
            save=req.save,
            output_dir="tests/ui/generated",
        )
        return {
            "url": result["url"],
            "saved": result["saved"],
            "saved_path": result["saved_path"],
            "code": result["code"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
