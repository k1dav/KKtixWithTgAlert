import abc
from typing import Any, Optional

import httpx
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


# Exception
class NoResponseException(Exception):
    pass


class BaseCrawlerMethod(metaclass=abc.ABCMeta):
    """爬蟲方法"""

    # NOTE: method_ is requests method
    # NOTE: url and method_ is necessary
    URL_PATH = None

    @abc.abstractmethod
    def get_params(self, **kwargs):
        return NotImplemented

    @abc.abstractmethod
    def parse_response(self, result: Any):
        return NotImplemented


class CrawlerAPI:
    """爬蟲 api"""

    TIMEOUT = 10
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    }
    selenium_url = "http://localhost:4444/wd/hub"

    def __init__(
        self,
        headers: Optional[dict] = None,
        selenium_url: Optional[str] = None,
    ):
        if headers:
            self.headers = headers
        if selenium_url:
            self.selenium_url = selenium_url

    async def execute(self, api_method: BaseCrawlerMethod, **kwargs):
        params = api_method.get_params(**kwargs)
        self.url = params.pop("url")

        result = await self._run_query(params)
        return api_method.parse_response(result)

    async def _run_query(self, params: dict) -> Any:
        method = params.pop("method_").lower()
        timeout = httpx.Timeout(self.TIMEOUT)

        if method == "selenium":
            try:
                browser = webdriver.Remote(
                    command_executor=self.selenium_url,
                    desired_capabilities=DesiredCapabilities.CHROME,
                )
                browser.get(self.url)
                source = browser.page_source
            finally:
                browser.quit()
            return source
        async with httpx.AsyncClient(headers=self.headers, timeout=timeout) as client:
            handler = getattr(client, method)

            if method == "get":
                req = handler(self.url, params=params)
            else:
                req = handler(self.url, data=params)

            try:
                resp = await req
                assert resp.status_code == 200
                return resp.content
            except AssertionError:
                pass
            raise NoResponseException
