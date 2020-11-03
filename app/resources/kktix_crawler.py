from typing import Any, List, Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel

from app.resources.crawler import BaseCrawlerMethod, CrawlerAPI

SELENIUM_URL = "http://192.168.66.125:4444/wd/hub"


class Ticket(BaseModel):
    name: str
    price: str
    quantity: str


class Tickets(BaseModel):
    tickets: List[Ticket]
    url: Optional[str] = None


def remove_useless_string(origin_str: str) -> str:
    """去除不必要的字元"""
    return origin_str.replace("\n", "").strip()


class KKTixActivityMethod(BaseCrawlerMethod):
    """KKTix 的爬蟲"""

    URL_PATH = "https://kktix.com/events/{activity_id}/registrations/new"

    def __init__(self, activity_id: str) -> None:
        self.URL_PATH = self.URL_PATH.format(activity_id=activity_id)

    def get_params(self, **kwargs):
        return {
            "url": self.URL_PATH,
            "method_": "selenium",
        }

    def parse_response(self, result: Any):
        soup = BeautifulSoup(result, "html.parser")
        ticket_table = soup.find_all("div", class_="display-table")

        list_ = []
        for ticket_row in ticket_table:
            list_.append(
                Ticket(
                    name=remove_useless_string(
                        ticket_row.find("span", class_="ticket-name").text
                    ),
                    price=remove_useless_string(
                        ticket_row.find("span", class_="ticket-price").text
                    ),
                    quantity=remove_useless_string(
                        ticket_row.find("span", class_="ticket-quantity").text
                    ),
                )
            )
        return Tickets(tickets=list_, url=self.URL_PATH)


async def search_empty_position(activity_id: str) -> Tickets:
    """找尋空位"""
    crawler = CrawlerAPI(selenium_url=SELENIUM_URL)
    method = KKTixActivityMethod(activity_id)
    tickets = await crawler.execute(method)
    empty_tickets = list(filter(lambda i: i.quantity != "Sold Out", tickets.tickets))
    return Tickets(tickets=empty_tickets, url=tickets.url)
