import asyncio
import os
import tempfile
from typing import List

from .converter import Converter
from .models import Chapter, Manga, Page
from .network import AsyncNet, Net
from .scraper import Scraper
from .utils import parse_selection, sanitize_filename


class Downloader:
    def __init__(self, output_dir: str, cookie: str = None):
        self.output_dir = output_dir
        self.cookie = cookie
        self.net = Net(cookie=cookie)
        self.scraper = Scraper(self.net)
        self.async_net = None

    async def start(self, url: str, selection: str = "all", save_as: str = "raw"):
        self.async_net = AsyncNet(cookie=self.cookie)
        try:
            manga = self.scraper.get_manga(url)
            print(f"Manga: {manga.title}")

            available_ids = [ch.id for ch in manga.chapters]
            selected_ids = parse_selection(selection, available_ids)

            chapters_to_process = [ch for ch in manga.chapters if ch.id in selected_ids]
            print(f"Selected {len(chapters_to_process)}/{len(manga.chapters)} volumes.")

            if not chapters_to_process:
                print("No volumes selected.")
                return

            await self._process_chapters(manga, chapters_to_process, save_as)

        finally:
            await self.async_net.close()

    async def _process_chapters(
        self, manga: Manga, chapters: List[Chapter], save_as: str
    ):
        safe_title = sanitize_filename(manga.title)
        base_path = os.path.join(self.output_dir, safe_title)
        os.makedirs(base_path, exist_ok=True)

        if save_as.endswith("-single"):
            await self._process_single_bundled(manga, chapters, save_as, base_path)
        else:
            for chapter in chapters:
                await self._process_chapter_individual(
                    manga, chapter, save_as, base_path
                )

    async def _process_chapter_individual(
        self, manga: Manga, chapter: Chapter, save_as: str, base_path: str
    ):
        print(f"Processing {chapter.title}...")
        self.scraper.get_chapter_pages(chapter)

        if not chapter.pages:
            print(f"  No pages found for {chapter.title}")
            return

        safe_chapter = sanitize_filename(chapter.title)

        if save_as in ["raw", "raw-volume"]:
            chapter_path = os.path.join(base_path, safe_chapter)
            os.makedirs(chapter_path, exist_ok=True)
            await self._download_pages(chapter.pages, chapter_path)
            print(f"  Completed {save_as}: {chapter_path}")

        else:
            with tempfile.TemporaryDirectory() as temp_dir:
                await self._download_pages(chapter.pages, temp_dir)

                images = [os.path.join(temp_dir, p.filename) for p in chapter.pages]

                ext = save_as.split("-")[0]
                if ext == "pdf":
                    out_file = os.path.join(base_path, f"{safe_chapter}.pdf")
                    Converter.create_pdf(images, out_file)
                elif ext == "cbz":
                    out_file = os.path.join(base_path, f"{safe_chapter}.cbz")
                    Converter.create_cbz(images, out_file)
                elif ext == "cb7":
                    out_file = os.path.join(base_path, f"{safe_chapter}.cb7")
                    Converter.create_cb7(images, out_file)
                elif ext == "epub":
                    out_file = os.path.join(base_path, f"{safe_chapter}.epub")
                    Converter.create_epub(images, out_file, chapter.title)

                print(f"  Completed {ext}: {out_file}")

    async def _process_single_bundled(
        self, manga: Manga, chapters: List[Chapter], save_as: str, base_path: str
    ):
        print(f"Processing bundled download for {len(chapters)} volumes...")

        if len(chapters) == 1:
            bundle_name = sanitize_filename(chapters[0].title)
        else:
            bundle_name = f"{sanitize_filename(chapters[-1].title)} - {sanitize_filename(chapters[0].title)}"
            pass

        if save_as == "raw-single":
            target_dir = os.path.join(base_path, bundle_name)
            os.makedirs(target_dir, exist_ok=True)

            for chapter in chapters:
                print(f"  Fetching {chapter.title}...")
                self.scraper.get_chapter_pages(chapter)
                prefix = sanitize_filename(chapter.title)
                flattened_pages = []
                for p in chapter.pages:
                    new_filename = f"{prefix}_{p.filename}"
                    p.filename = new_filename
                    flattened_pages.append(p)

                await self._download_pages(flattened_pages, target_dir)
            print(f"  Completed raw-single: {target_dir}")
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            all_images = []
            for chapter in chapters:
                print(f"  Fetching {chapter.title}...")
                self.scraper.get_chapter_pages(chapter)

                prefix = sanitize_filename(chapter.title)

                chapter_images = []
                for p in chapter.pages:
                    p.filename = f"{prefix}_{p.filename}"
                    chapter_images.append(p)

                await self._download_pages(chapter_images, temp_dir)
                all_images.extend(
                    [os.path.join(temp_dir, p.filename) for p in chapter_images]
                )

            ext = save_as.split("-")[0]
            out_file = os.path.join(base_path, f"{bundle_name}.{ext}")

            if ext == "pdf":
                Converter.create_pdf(all_images, out_file)
            elif ext == "cbz":
                Converter.create_cbz(all_images, out_file)
            elif ext == "cb7":
                Converter.create_cb7(all_images, out_file)
            elif ext == "epub":
                Converter.create_epub(all_images, out_file, manga.title)

            print(f"  Completed single {ext}: {out_file}")

    async def _download_pages(self, pages: List[Page], folder: str):
        tasks = []
        total = len(pages)
        completed = 0

        async def progress_wrapper(coro):
            nonlocal completed
            await coro
            completed += 1
            print(f"\r  [{completed}/{total}] pages downloaded", end="", flush=True)

        for page in pages:
            tasks.append(progress_wrapper(self._download_page(page, folder)))

        await asyncio.gather(*tasks)
        print()

    async def _download_page(self, page: Page, folder: str):
        try:
            content = await self.async_net.get_content(page.url)
            path = os.path.join(folder, page.filename)
            with open(path, "wb") as f:
                f.write(content)
        except Exception as e:
            print(f"  Failed to download {page.url}: {e}")
