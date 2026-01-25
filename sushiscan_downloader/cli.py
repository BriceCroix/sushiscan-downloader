import argparse
import asyncio
import sys

from .downloader import Downloader


def main():
    parser = argparse.ArgumentParser(description="Sushiscan Downloader CLI")
    parser.add_argument("url", help="URL of the manga on sushiscan.net")
    parser.add_argument("-o", "--output", default="downloads", help="Output directory")
    parser.add_argument("-c", "--cookie", help="Cloudflare cookie (cf_clearance=...)")
    parser.add_argument(
        "--volumes", default="all", help="Volumes to download (e.g. '1,3,5-7' or 'all')"
    )
    parser.add_argument(
        "--save-as",
        default="raw",
        choices=[
            "raw",
            "raw-volume",
            "raw-single",
            "pdf",
            "pdf-volume",
            "pdf-single",
            "cbz",
            "cbz-volume",
            "cbz-single",
            "cb7",
            "cb7-volume",
            "cb7-single",
            "epub",
            "epub-volume",
            "epub-single",
        ],
        help="Output format",
    )
    parser.add_argument("--user-agent", help="User Agent to use")

    args = parser.parse_args()

    cookie = args.cookie

    downloader = Downloader(args.output, cookie, user_agent=args.user_agent)
    try:
        asyncio.run(
            downloader.start(args.url, selection=args.volumes, save_as=args.save_as)
        )
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
