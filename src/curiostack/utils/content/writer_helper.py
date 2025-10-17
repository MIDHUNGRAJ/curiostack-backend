import json
import os
import sqlite3
from ...config import get_db_path
from ...logger import get_logger


def get_titles(niche, debug=False):
    logger = get_logger(__name__, debug=False)
    """_summary_

    Args:
        niche (_str_): example: ai_ml, data science, cybersecurity

    Returns:
        _list_: returning list of titles
    """

    # Connect to database
    db_path = get_db_path(niche)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT title
                    FROM urls
                    WHERE processed = 1 AND content_written = 0
                """
            )
            rows = cursor.fetchall()
        return [row[0] for row in rows if row[0] is not None]
    except Exception as e:
        logger.exception(f"Failed to get titles: {niche}: {e}")
        return []


def content_save(top, final_data, niche, debug=False):
    """
    Save generated content to a JSON file and update the database
    to mark the corresponding title as written.

    Args:
        top (str): The topic (used as the title and filename).
        final_data (dict): The content data in JSON format.
        niche (str): Example: "ai_ml", "data_science", "cybersecurity".
        debug (bool): Whether to enable debug logging.
    """
    logger = get_logger(__name__, debug=debug)

    # Get paths
    db_path, script_dir = get_db_path(niche, script_dir=True)

    # Directory for output
    output_dir = os.path.join(script_dir, "..", "..", "data", "raw", niche)
    os.makedirs(output_dir, exist_ok=True)

    # Sanitize filename
    safe_top = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in top)
    filename = f"{safe_top}.json"
    output_path = os.path.join(output_dir, filename)

    try:
        # Write JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)

        # Update database
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE urls
                SET content_written = 1
                WHERE title = ?
                """,
                (top,),
            )
            conn.commit()

        logger.info(f"Content successfully saved for '{top}' → {output_path}")

    except Exception as e:
        logger.exception(f"Error saving content for '{top}' to {output_path}: {e}")


# # Example usage
# if __name__ == "__main__":
#     titles = get_titles(niche="ai_ml")
#     for t in titles:
#         print(t)
