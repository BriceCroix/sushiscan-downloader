import asyncio

import curl_cffi
from bs4 import BeautifulSoup


class Net:
    def __init__(self, user_agent: str = None, cookie: str = None):

        cookies_dict = {}
        if cookie:
            for item in cookie.split(";"):
                if "=" in item:
                    k, v = item.split("=", 1)
                    cookies_dict[k.strip()] = v.strip()

        self.session = curl_cffi.Session(
            impersonate="chrome",
            cookies=cookies_dict,
            retry=curl_cffi.RetryStrategy(count=10, delay=1, jitter=1),
        )

        self.session.headers["referer"] = "https://sushiscan.net/"
        if user_agent:
            self.session.headers["user-agent"] = user_agent

    def get(self, url: str):
        return self.session.get(url, timeout=600)

    def get_soup(self, url: str) -> BeautifulSoup:
        response = self.get(url)
        return BeautifulSoup(response.text, "html.parser")

    def update_cookie(self, cookie: str):
        if "=" in cookie:
            k, v = cookie.split("=", 1)
            self.session.cookies.set(k.strip(), v.strip())


class AsyncNet:
    def __init__(self, user_agent: str = None, cookie: str = None):
        cookies_dict = {}
        if cookie:
            for item in cookie.split(";"):
                if "=" in item:
                    k, v = item.split("=", 1)
                    cookies_dict[k.strip()] = v.strip()

        self.session = curl_cffi.AsyncSession(
            impersonate="chrome",
            cookies=cookies_dict,
            retry=curl_cffi.RetryStrategy(count=10, delay=1, jitter=1),
        )

        self.session.headers["referer"] = "https://sushiscan.net/"
        if user_agent:
            self.session.headers["user-agent"] = user_agent

    async def get(self, url: str) -> curl_cffi.Response:
        return await self.session.get(url, timeout=600)

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
