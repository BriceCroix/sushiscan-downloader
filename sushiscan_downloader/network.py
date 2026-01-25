import asyncio

import curl_cffi
from bs4 import BeautifulSoup


class Net:
    def __init__(self, user_agent: str = None, cookie: str = None):
        self.headers = {
            "referer": "https://sushiscan.net/",
            "user-agent": user_agent
            or "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        }
        if cookie:
            self.headers["cookie"] = cookie

        self.session = curl_cffi.Session(impersonate="chrome")
        self.session.headers.update(self.headers)

    def get(self, url: str) -> curl_cffi.Response:
        return self.session.get(url)

    def get_soup(self, url: str) -> BeautifulSoup:
        response = self.get(url)
        return BeautifulSoup(response.text, "html.parser")

    def update_cookie(self, cookie: str):
        self.headers["cookie"] = cookie
        self.session.headers.update({"cookie": cookie})


class AsyncNet:
    def __init__(self, user_agent: str = None, cookie: str = None):
        self.headers = {
            "referer": "https://sushiscan.net/",
            "user-agent": user_agent
            or "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        }
        if cookie:
            self.headers["cookie"] = cookie

        self.session = curl_cffi.AsyncSession(impersonate="chrome")
        self.session.headers.update(self.headers)

    async def get(self, url: str) -> curl_cffi.Response:
        return await self.session.get(url)

    async def get_content(self, url: str) -> bytes:
        response = await self.get(url)
        return response.content

    async def close(self):
        if asyncio.iscoroutinefunction(self.session.close):
            await self.session.close()
        else:
            res = self.session.close()
            if asyncio.iscoroutine(res):
                await res
