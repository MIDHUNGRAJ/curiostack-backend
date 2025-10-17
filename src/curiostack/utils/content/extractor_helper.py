import sqlite3
from playwright.async_api import async_playwright
import re, json
from ...config import get_db_path
from ...logger import get_logger


async def RedirectHelper(url: str):
    if not url or not isinstance(url, str):
        raise ValueError(f"Invalid URL: {url}")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        final_url = url  # default: assume no redirect

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            if page.url and page.url != url:
                final_url = page.url
            print("Final URL:", final_url)
            print("----")
        except Exception as e:
            print(f"Navigation error for {url}: {e}")
        finally:
            await browser.close()

        return final_url


async def get_unprocessed_urls(niche, limit, debug=False):
    logger = get_logger(__name__, debug=False)

    db_path = get_db_path(niche)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, url FROM urls WHERE processed = 0 LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
    except Exception as e:
        logger.exception(f"Error connecting to SQLite database at {db_path}: {e}")
        return [], []

    urls_after = []
    url_ids = []
    for id, url in rows:
        if debug:
            print(f"Before: {url}")
        urls_red = await RedirectHelper(url)
        if urls_red is not None:
            urls_after.append(urls_red)
            url_ids.append(id)

    if debug:
        print(f"From utils: {urls_after}")
    return url_ids, urls_after


def mark_url_processed(url_ids, niche, debug=False):
    logger = get_logger(__name__, debug=debug)

    if not url_ids:
        logger.info("No URLs to mark as processed.")
        return

    db_path = get_db_path(niche)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            query = f"UPDATE urls SET processed = 1 WHERE id IN ({','.join('?' for _ in url_ids)})"
            cursor.execute(query, url_ids)
            conn.commit()
        logger.info(f"Marked {len(url_ids)} URLs as processed in {niche}.")
    except Exception as e:
        logger.exception(f"Failed to mark URLs as processed in {niche}: {e}")


# Extracting metadata from content
def extract_metadata_and_content(markdown_str):
    match = re.search(r"```json(.*?)```", markdown_str, re.DOTALL)
    metadata = {}
    if match:
        try:
            metadata = json.loads(match.group(1))
        except json.JSONDecodeError as e:
            print("Metadata parsing failed:", e)
        markdown_str = markdown_str.replace(match.group(0), "").strip()
    return metadata, markdown_str
