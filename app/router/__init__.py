from fastapi import APIRouter

from .entry import router as EntryRouter

router = APIRouter()
router.include_router(EntryRouter, prefix="/entry", tags=["entry"])
