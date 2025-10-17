import asyncio
from .scraping import Crawler, ContentExtractor
from .preprocessing import ContentWriter, pre_pro, update_img_url

# from .logger import get_logger
import time

# logger = get_logger(__name__, debug=True)


# def run():
#     ai_ml_crawler = Crawler(niche="ai_ml")
#     logger.info("Starting Curiostack Crawler")
#     try:
#         asyncio.run(ai_ml_crawler.start())
#     except Exception as e:
#         logger.exception(f"An error occured entho myre {e}")

# ai_ml_crawler = Crawler(niche="ai_ml", debug=True)

# ai_ml_extract = ContentExtractor(niche="ai_ml", limit=3, debug=True)

# ai_ml_writer = ContentWriter(niche="ai_ml", limit=3, debug=True)

# cybersecurity_crawler = Crawler(niche="cybersecurity", debug=True)

# cybersecurity_extract = ContentExtractor(niche="cybersecurity", limit=10, debug=True)

# cybersecurity_writer = ContentWriter(niche="cybersecurity", limit=10, debug=True)

# asyncio.run(ai_ml_crawler.start())
# time.sleep(3)
# asyncio.run(ai_ml_extract.start())
# time.sleep(3)
# ai_ml_writer.start()
# time.sleep(3)
# pre_pro(niche="ai_ml")
# update_img_url(niche="ai_ml")

# asyncio.run(cybersecurity_crawler.start())

# time.sleep(3)

# asyncio.run(cybersecurity_extract.start())

# time.sleep(3)

# cybersecurity_writer.start()

# time.sleep(2)

# pre_pro(niche="cybersecurity")
# update_img_url(niche="cybersecurity")


niches = ["ai_ml", "cybersecurity", "common_technology", "data_science"]

for niche in niches:

    crawler = Crawler(niche=niche, debug=True)
    extracter = ContentExtractor(niche=niche, limit=10)
    writer = ContentWriter(niche=niche, limit=10, debug=True)

    asyncio.run(crawler.start())
    time.sleep(3)
    asyncio.run(extracter.start())
    time.sleep(3)
    writer.start()
    time.sleep(3)
    pre_pro(niche=niche)
    update_img_url(niche=niche)
    print("COMPLETED 🚨")

