import json
import re
from datetime import datetime
from typing import List, Optional
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain.chains import RetrievalQA
from ..config import embeddings, client, llm, collection_name_creator
from ..utils import get_titles, content_save
from pydantic import BaseModel, Field, ValidationError
from ..logger import get_logger
import time


class ContentWriter:
    def __init__(self, niche, limit=None, debug=False):
        self.niche = niche
        self.limit = limit
        self.debug = debug
        self.logger = get_logger(__name__, debug=self.debug)

    def start(self):
        # Ensure collection exists before creating vector store
        collection_name_creator(collection_name=self.niche)

        # Vector Store
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=self.niche,
            embedding=embeddings,
            retrieval_mode=RetrievalMode.DENSE,
        )

        # RAG
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 6, "fetch_k": 32, "lambda_mult": 0.7},
            ),
        )
        titles = get_titles(niche=self.niche, debug=self.debug)

        # Questions or query
        # Validation schema for outputs (no aiVersion)
        class WrittenPost(BaseModel):
            title: str
            content: str
            excerpt: str
            url: Optional[str] = None
            author: Optional[str] = None
            date: Optional[str] = Field(default=None, description="YYYY-MM-DD or null")
            category: str
            tags: List[str]
            image: Optional[str] = None
            featured: bool

        def normalize_payload(payload: dict) -> dict:
            # Convert "Unknown"/"N/A"/empty strings to None for nullable fields
            for key in ["url", "author", "date", "image"]:
                if key in payload and isinstance(payload[key], str):
                    if payload[key].strip().lower() in {"unknown", "n/a", "", "null"}:
                        payload[key] = None

            # Ensure featured is boolean
            if isinstance(payload.get("featured"), str):
                payload["featured"] = payload["featured"].strip().lower() in {
                    "true",
                    "1",
                    "yes",
                }

            # Validate/normalize date to YYYY-MM-DD or None
            date_val = payload.get("date")
            if isinstance(date_val, str):
                try:
                    dt = datetime.fromisoformat(date_val.strip().replace("/", "-"))
                    payload["date"] = dt.strftime("%Y-%m-%d")
                except Exception:
                    payload["date"] = None

            # Ensure content has Key Takeaways section and no top-level title
            content_val = payload.get("content") or ""
            if isinstance(content_val, str):
                payload["content"] = re.sub(r"^#\s+.*\n+", "", content_val, count=1)
                if "## Key Takeaways" not in payload["content"]:
                    payload["content"] = (
                        payload["content"].rstrip() + "\n\n## Key Takeaways\n- "
                    )

            return payload

        if self.limit is not None:
            titles = titles[:self.limit]

        for top in titles:
            query = f"""
            You are a precise content writer. Using only retrieved context, produce a STRICT JSON object with fields below. Do not include code fences or any extra text.

            Schema:
            {{
            "title": "string",
            "content": "markdown string (no top-level # title; use ## for sections)",
            "excerpt": "1-2 sentence summary",
            "url": "string|null",
            "author": "string|null",
            "date": "YYYY-MM-DD|null",
            "category": "string",
            "tags": ["string"],
            "image": "string|null",
            "featured": false,
            }}

            Writing rules:
            - Do NOT repeat the title inside content.
            - Structure content with meaningful sections (##), lists, tables, and code blocks when relevant.
            - End content with a section: "## Key Takeaways" listing 4–8 bullets.
            - Keep all prose strictly inside the content field.

            Topic: {top}
            """

            answer = qa_chain.invoke({"query": query})
            raw_result = answer["result"]
            clean_result = re.sub(r"```(?:json)?|```", "", raw_result).strip()

            try:
                result = json.loads(clean_result)
            except json.JSONDecodeError:
                # Retry once with stricter instruction if parsing failed
                retry_query = (
                    "Return ONLY a valid JSON object per the schema. No prose, no code fences, no comments. "
                    + query
                )
                answer = qa_chain.invoke({"query": retry_query})
                raw_retry = answer.get("result", "")
                clean_retry = re.sub(r"```(?:json)?|```", "", raw_retry).strip()
                try:
                    result = json.loads(clean_retry)
                except json.JSONDecodeError:
                    self.logger.warning(
                        f"Skipping topic '{top}' due to invalid JSON after retry."
                    )
                    self.logger.debug(
                        f"First output: {raw_result}\nRetry output: {raw_retry}"
                    )
                    continue

            # Normalize and validate
            result = normalize_payload(result)
            try:
                validated = WrittenPost(**result)
                result = validated.model_dump()
            except ValidationError as ve:
                self.logger.warning(f"Validation failed for topic '{top}': {ve}")
                continue

            content_save(top=top, final_data=result, niche=self.niche, debug=self.debug)
            time.sleep(5)
