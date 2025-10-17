import os
import json
from datetime import datetime
from ..config import llm, UNSPLASH_ACCESS_KEY
import requests
import random

# Replace with your actual Unsplash Access Key
SEARCH_URL = "https://api.unsplash.com/search/photos"

# Main categories
MAIN_CATEGORIES = ["AI", "Technology", "Business", "Cybersecurity", "Data Science"]

main_categories = MAIN_CATEGORIES


def pre_pro(niche):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full, absolute path for the output file
    output_path = os.path.join(
        script_dir, "..", "..", "..", "data", "raw", niche
    )

    for filename in os.listdir(output_path):
        if filename.endswith(".json"):
            filepath = os.path.join(output_path, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                old_category = data.get("category", "")
                title = data.get("title", "")

                # Date only (YYYY-MM-DD) generated fresh for each file
                current_date = datetime.now().strftime("%Y-%m-%d")

                if not old_category or old_category.lower() not in [
                    c.lower() for c in main_categories
                ]:
                    prompt = f"""
                    You are a preprocessing model.
                    The given category is: "{old_category}".
                    The title is: "{title}".

                    Map this topic to the most relevant category from this list: {main_categories}.
                    Only respond with one category name from the list.
                    """
                    new_category = llm.invoke(prompt).content.strip()
                else:
                    new_category = old_category

                # Update JSON
                data["category"] = new_category

                if not data.get("date"):  # Covers None, "", missing key
                    data["date"] = current_date

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                print(f"Updated {filename}: {old_category} -> {new_category}")
                print(f"Updated {filename}: Date -> {data['date']}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")


def search_unsplash_images(query, per_page=10):
    params = {"query": query, "per_page": per_page, "client_id": UNSPLASH_ACCESS_KEY}
    response = requests.get(SEARCH_URL, params=params)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()


def update_img_url(niche):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full, absolute path for the output file
    output_path = os.path.join(
        script_dir, "..", "..", "..", "data", "raw", niche
    )

    for filename in os.listdir(output_path):
        if filename.endswith(".json"):
            filepath = os.path.join(output_path, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                category = data.get("category", "")
                print(category)

                if category == "AI":
                    results = search_unsplash_images(category)

                    photo_urls = []
                    if results and results.get("results"):
                        for photo in results["results"]:
                            photo_urls.append(photo["urls"]["regular"])

                    ai_ml_img = random.choice(photo_urls)
                    data["image"] = ai_ml_img

                if category == "Technology":
                    results = search_unsplash_images(category)

                    photo_urls = []
                    if results and results.get("results"):
                        for photo in results["results"]:
                            photo_urls.append(photo["urls"]["regular"])

                    tech_img = random.choice(photo_urls)
                    data["image"] = tech_img

                if category == "Business":
                    results = search_unsplash_images(category)

                    photo_urls = []
                    if results and results.get("results"):
                        for photo in results["results"]:
                            photo_urls.append(photo["urls"]["regular"])

                    bus_img = random.choice(photo_urls)
                    data["image"] = bus_img

                if category == "Cybersecurity":
                    results = search_unsplash_images(category)

                    photo_urls = []
                    if results and results.get("results"):
                        for photo in results["results"]:
                            photo_urls.append(photo["urls"]["regular"])

                    cyber_img = random.choice(photo_urls)
                    data["image"] = cyber_img

                if category == "Data Science":
                    results = search_unsplash_images(category)

                    photo_urls = []
                    if results and results.get("results"):
                        for photo in results["results"]:
                            photo_urls.append(photo["urls"]["regular"])

                    data_img = random.choice(photo_urls)
                    data["image"] = data_img

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)

            except Exception as e:
                print(f"Error processing {filename}: {e}")

