import json
import re
from typing import List

from .models import Chapter, Manga, Page
from .network import Net


class Scraper:
    def __init__(self, net: Net):
        self.net = net

    def get_manga(self, url: str) -> Manga:
        soup = self.net.get_soup(url)

        title_tag = soup.find("h1", class_="entry-title")
        title = title_tag.text.strip() if title_tag else "Unknown Manga"

        manga = Manga(title=title, url=url)

        chapter_list = soup.find("div", id="chapterlist")
        if chapter_list:
            for li in chapter_list.find_all("li"):
                data_num = li.get("data-num")
                link = li.find("a")

                if data_num and link:
                    chapter_title_span = li.find("span", class_="chapternum")
                    chapter_title = (
                        chapter_title_span.text.strip()
                        if chapter_title_span
                        else f"Chapter {data_num}"
                    )

                    chapter_url = link.get("href")

                    chapter = Chapter(id=data_num, url=chapter_url, title=chapter_title)
                    manga.chapters.append(chapter)

        return manga

    def get_chapter_pages(self, chapter: Chapter) -> List[Page]:
        response_text = self.net.get(chapter.url).text

        match = re.search(r'"images"\s*:\s*(\[.*?\])', response_text)
        pages = []
        if match:
            images_raw = match.group(1)
            images_raw = images_raw.replace("\\/", "/")
            try:
                images_urls = json.loads(images_raw)
                for idx, img_url in enumerate(images_urls):
                    ext = img_url.split(".")[-1]
                    filename = f"{idx + 1:03d}.{ext}"
                    pages.append(Page(url=img_url, filename=filename))
            except json.JSONDecodeError:
                pass

        chapter.pages = pages
        return pages
