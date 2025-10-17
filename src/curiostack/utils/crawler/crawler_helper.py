import os
import sqlite3
import json
from ...config import get_db_path
from ...logger import get_logger

logger = get_logger(__name__, debug=False)


def niches_urls(niche):
    """_summary_

    Args:
        name (str): "ai_ml", "common", "cybersecurity", "datascience"
        niche (str): "technology", "business", "ai_ml" , etc..

    Returns:
        list : returns list of urls
    """
    logger.info(f"niches_urls called for {niche}")
    current_dir = os.path.dirname(os.path.abspath(__file__))

    output_path = os.path.join(current_dir, "..", "..", "niches", "urls.json")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, "r") as u:
            urls = json.load(u)
    except Exception as e:
        logger.exception(f"niches urls got error {e}")

    urls_ai_ml = urls[niche]
    return urls_ai_ml


def save_data(final_filtered_data, niche):
    """_summary_

    Args:
        final_filtered_data (_doc_): The web source data in JSON format
        niche (_str_): example: ai_ml, data science, cybersecurity
    """
    # Build database file path
    db_path = get_db_path(niche)

    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Make sure table exists (added title column)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        niche TEXT,
        processed INTEGER DEFAULT 0,
        content_written INTEGER DEFAULT 0
    );
    """)

    # Insert new URLs with titles (duplicates skipped automatically)
    for item in final_filtered_data:
        url = item.get("url")
        title = item.get("title")
        if url:
            cursor.execute("""
            INSERT OR IGNORE INTO urls (url, title, niche)
            VALUES (?, ?, ?)
            """, (url, title, niche))

    conn.commit()
    conn.close()

    print(f"Data successfully saved to: {db_path}")

