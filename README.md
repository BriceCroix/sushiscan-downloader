# Sushiscan Downloader

A high-performance, asynchronous CLI downloader for SushiScan.

## Installation

```bash
pip install uv
uv sync
```

## Usage

```bash
uv run python -m sushiscan_downloader [URL] [OPTIONS]
```

### Options

- `-o, --output`: Output directory (default: `downloads`)
- `-c, --cookie`: **Required** Cloudflare cookie (`cf_clearance=...`)
- `--volumes`: Select volumes (e.g., `1`, `1-5`, `1,3`, `all`)
- `--save-as`: Export format (`raw`, `pdf`, `cbz`, `epub`, `cb7`) suffixes `-single` or `-volume` supported.

> **Note:** The `cf_clearance` cookie is almost always required to bypass Cloudflare protection. You can get it from your browser's devtools (Application -> Cookies).

## Examples

Download specific volumes as PDF:
```bash
uv run python -m sushiscan_downloader "https://sushiscan.net/catalogue/manga-url" --volumes "1-3" --save-as pdf
```

Download all volumes into a single CBZ file:
```bash
uv run python -m sushiscan_downloader "https://sushiscan.net/catalogue/manga-url" --save-as cbz-single
```
