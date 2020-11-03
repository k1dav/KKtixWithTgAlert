from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.resources.kktix_crawler import Tickets, search_empty_position

router = APIRouter()


@router.get("/kktix", name="entry:fire_kktix")
async def find_fish_activity():
    list_ = []
    fish_26: Tickets = await search_empty_position("fish20202026")
    if fish_26.tickets:
        list_.append(fish_26)

    fish_27: Tickets = await search_empty_position("fish20202027")
    if fish_27.tickets:
        list_.append(fish_27)
    return list_
