from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")


@router.get("/health", tags=["system"])
def health():
    return {"status": "ok", "api_version": "v1"}
