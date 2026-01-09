from fastapi import APIRouter, Depends
from auth.security import require_api_key

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/check")
def check_key(_: None = Depends(require_api_key)):
    return {"ok": True, "message": "API key is valid."}
