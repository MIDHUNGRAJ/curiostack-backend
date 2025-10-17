import os
from dotenv import load_dotenv
from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)
from crawl4ai import LLMConfig
from crawl4ai.content_filter_strategy import LLMContentFilter
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_voyageai import VoyageAIEmbeddings

# Loading env
load_dotenv()

# API KEY
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
QDRANT_CLIENT_URL = os.getenv("QDRANT_CLIENT_URL")


# Database path ###############
def get_db_path(niche, script_dir=False):
    """_summary_

    Args:
        niche (_str_): example: ai_ml, data science, cybersecurity
        script_dir (bool, optional): _description_. Defaults to False.

    Returns:
        _str_: path
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_name = f"{niche}_web_sources.db"
    db_path = os.path.join(base_dir, "database", db_name)
    if script_dir:
        return db_path, base_dir

    return db_path
# End #######################


# LLM Config ##############################
llm_conf = LLMConfig(
    provider="gemini/gemini-2.0-flash",
    api_token=GOOGLE_API_KEY,
)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# embeddings = VoyageAIEmbeddings(
#     model="voyage-3.5",
#     api_key=VOYAGE_API_KEY,
# )

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro", google_api_key=GOOGLE_API_KEY
)
# END ####################################


# Langchain related ######
class PageData(BaseModel):
    title: str = Field(..., description="The title of the blog post")
    author: str = Field(None, description="Author name if available")
    date: str = Field(None, description="Publication date YYYY-MM-DD")
    url: str = Field(..., description="URL of the blog post")
    source: str = Field(..., description="Source of the information")


def browser_conf():
    browser_conf = BrowserConfig(
        headless=True,
        text_mode=True,
        user_agent="Mozilla/5.0 Crawl4AI/1.0",
        verbose=False,
    )
    return browser_conf


def llm_strategy():
    llm_strategy = LLMExtractionStrategy(
        schema=PageData.model_json_schema(),
        extraction_type="schema",
        input_format="markdown",
        instruction=(
            "You are an expert content extractor. From the provided page content (markdown), extract ONLY the fields defined in the provided JSON Schema.\n"
            "- Map fields precisely: title, author (or null), date (YYYY-MM-DD or null), url, source.\n"
            "- Ignore navigation, ads, cookie banners, comments, unrelated links, and UI elements.\n"
            "- If a field is missing on the page, return null for that field.\n"
            "- Return a single JSON object that strictly conforms to the schema. No code fences, no extra text."
        ),
        llm_config=llm_conf,
    )
    return llm_strategy


def run_config():
    run_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy(),
        word_count_threshold=100,  # adjust for filtering short pages
        cache_mode=CacheMode.BYPASS,
    )
    return run_config


filter = LLMContentFilter(
    llm_config=llm_conf,
    instruction="""
        Task: From the provided webpage content, extract high-value educational material about Artificial Intelligence (AI) and Machine Learning (ML). Preserve structure and completeness. Exclude ads, navigation, comments, cookie notices, trackers, and unrelated sections.

        Output format: Produce TWO sections exactly in this order.

        SECTION 1 — Metadata (single JSON object in a fenced json code block):
        ```json
        {
          "title": "string",
          "author": "string|null",
          "published_date": "YYYY-MM-DD|null",
          "source_url": "string",
          "tags": ["string"]
        }
        ```

        Rules for metadata:
        - If unknown, use null (not "Unknown").
        - Use ISO date if available; otherwise null.
        - Provide 3–8 specific tags (e.g., "transformers", "reinforcement learning").

        SECTION 2 — Full Content (as Markdown in a fenced markdown code block):
        ```markdown
        <Full educational content only>
        ```

        Rules for content:
        - Keep original logical order, headings, lists, code blocks, and math. Do not summarize.
        - Include code examples and math as-is. Use fenced code with language hints when known.
        - Remove boilerplate (sign-up prompts, cookie notices, nav, footers). Do not include comments sections.
        - Do not include any prose outside the two fenced blocks.
        """,
    chunk_token_threshold=2096,
    verbose=True,
)
# END ##############################


# Vector DB Config ####################
client = QdrantClient(
    url=QDRANT_CLIENT_URL,
    api_key=QDRANT_API_KEY,
)


def collection_name_creator(collection_name):
    # Checking the collection name exists or not
    existing_collections = [
        col.name for col in client.get_collections().collections
    ]

    # Creating Collection if not exists
    if collection_name not in existing_collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
# END ################################
