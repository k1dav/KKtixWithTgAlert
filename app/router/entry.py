from datetime import datetime

import pytz
import telegram
from fastapi import APIRouter
from telegram.parsemode import ParseMode

from app.core.config import BOT_TOKEN
from app.resources.kktix_crawler import Tickets, search_empty_position

router = APIRouter()
MY_IDs = [1234321231]
TZ = pytz.timezone("Asia/Taipei")


@router.get("/kktix", name="entry:fire_kktix")
async def find_fish_activity():
    bot = telegram.Bot(BOT_TOKEN)

    list_ = []
    fish_26: Tickets = await search_empty_position("fish20202026")
    if fish_26.tickets:
        list_.append(fish_26)
        for ticket in fish_26.tickets:
            text = f"[26 場次 \- {ticket.price} 有 {ticket.quantity} 張釋出]({fish_26.url})"
            for id in MY_IDs:
                bot.send_message(
                    chat_id=id, text=text, parse_mode=ParseMode.MARKDOWN_V2
                )

    fish_27: Tickets = await search_empty_position("fish20202027")
    if fish_27.tickets:
        list_.append(fish_27)
        for ticket in fish_27.tickets:
            text = f"[27 場次 \- {ticket.price} 有 {ticket.quantity} 張釋出]({fish_27.url})"
            for id in MY_IDs:
                bot.send_message(
                    chat_id=id, text=text, parse_mode=ParseMode.MARKDOWN_V2
                )
    if not list_:
        for id in MY_IDs:
            bot.send_message(
                chat_id=id,
                text=f"目前沒有釋出的票 \n{datetime.utcnow().astimezone(TZ).strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode=ParseMode.HTML,
            )
    return list_
