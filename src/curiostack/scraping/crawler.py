import json
import asyncio
from crawl4ai import AsyncWebCrawler
from ..config import browser_conf, run_config
from ..utils import save_data, niches_urls
from ..logger import get_logger


class Crawler:
    def __init__(self, niche, debug=False):
        self.logger = get_logger(__name__, debug=debug)
        self.niche = niche
        self.logger.info(f"Crawler initialized with niche={niche}")

    async def start(self):
        # Load URLs
        self.logger.info(f"Starting crawl for niche={self.niche}")

        self.urls = niches_urls(niche=self.niche)

        # Crawl config
        self.run_conf = run_config()

        self.browser_conf = browser_conf()
        final_filtered_data = []

        try:
            # Crawl and extract using recommended loop
            async with AsyncWebCrawler(config=self.browser_conf) as crawler:
                results = await crawler.arun_many(urls=self.urls, config=self.run_conf)
                for result in results:
                    if result.success and result.extracted_content:
                        blog = result.extracted_content

                        # print(blog)  # For Debug

                        raw_json_string = blog  # your entire JSON string goes here
                        try:
                            blog_data = json.loads(raw_json_string)
                        except json.JSONDecodeError:
                            print("Invalid JSON string.")
                            blog_data = []

                        # Optional: filter out error entries
                        filtered_data = [
                            item for item in blog_data if not item.get("error", False)
                        ]

                        final_filtered_data.extend(filtered_data)

            save_data(final_filtered_data, niche=self.niche)
        except Exception as e:
            self.logger.exception(f"Crawling failed for niche={self.niche}: {e}")


if __name__ == "__main__":
    ai_ml = Crawler(niche="ai_ml")
    asyncio.run(ai_ml.start())
