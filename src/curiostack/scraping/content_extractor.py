import asyncio
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
)
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..utils import (
    get_unprocessed_urls,
    mark_url_processed,
    extract_metadata_and_content,
)
from ..config import filter, embeddings, client, collection_name_creator
from ..logger import get_logger


class ContentExtractor:
    def __init__(self, niche, limit, debug=False):
        self.niche = niche
        self.limit = limit
        self.debug = debug
        self.logger = get_logger(__name__, debug=self.debug)
        self.logger.info(f"Content Extractor intialized with niche: {self.niche}")

    async def start(self):
        url_id, urls = await get_unprocessed_urls(niche=self.niche, limit=self.limit, debug=self.debug)

        # MD generator
        md_generator = DefaultMarkdownGenerator(
            content_filter=filter, options={"ignore_links": True}
        )

        # Crawler Config
        config = CrawlerRunConfig(
            markdown_generator=md_generator,
        )

        # Text Splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )

        # Checking the collection name exists or not
        collection_name_creator(collection_name=self.niche)

        vector_store = QdrantVectorStore(
            client=client,
            collection_name=self.niche,
            embedding=embeddings,
            retrieval_mode=RetrievalMode.DENSE,
        )

        # Browser config
        browser_config = BrowserConfig(headless=True, verbose=True)

        # Crawling scraping data
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                results = await crawler.arun_many(urls, config=config)
                for result in results:
                    if result.success:
                        # print(result.markdown.fit_markdown)  # Debug only
                        metadata, cleaned_markdown = extract_metadata_and_content(
                            result.markdown.fit_markdown
                        )

                    # print(metadata) # Debug only
                    text_chunk = text_splitter.split_text(cleaned_markdown)
                    try:
                        vector_store.add_texts(
                            texts=text_chunk, metadatas=[metadata] * len(text_chunk)
                        )

                    except Exception as e:
                        print("Embedding/Storage Error:", e)

                else:
                    print("Error:", result.error_message)
        except Exception as e:
            self.logger.info(f"Error during content extraction: {e}")

        mark_url_processed(url_ids=url_id, niche=self.niche, debug=False)
        self.logger.info("Saved to Database Qdrant")


if __name__ == "__main__":
    con_scrap = ContentExtractor(niche="ai_ml")
    asyncio.run(con_scrap.start())
