import asyncio
import logging
import json
from pprint import pprint
from feedsearch_crawler import search, FeedsearchSpider

urls = [
    # "http://arstechnica.com",
    "http://davidbeath.com",
    # "http://xkcd.com",
    # "http://jsonfeed.org",
    # "en.wikipedia.com",
    # "scientificamerican.com",
    # "newyorktimes.com",
    # "https://www.dancarlin.com",
    # "https://www.hanselminutes.com/",
    # "nytimes.com",
    # "https://www.jeremydaly.com/serverless-microservice-patterns-for-aws/",
    # "feedhandbook.com"
]


def get_pretty_print(json_object: object):
    return json.dumps(json_object, sort_keys=True, indent=2, separators=(",", ": "))


if __name__ == "__main__":
    logger = logging.getLogger("feedsearch_crawler")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    user_agent = "Mozilla/5.0 Feedsearch Bot"

    crawler = FeedsearchSpider(
        concurrency=10, timeout=100000, user_agent=user_agent, favicon_data_uri=False
    )
    crawler.start_urls = urls
    asyncio.run(crawler.crawl())

    serialized = [item.serialize() for item in crawler.items]

    # items = search(urls[0], concurrency=40, try_urls=False)
    # serialized = [item.serialize() for item in items]

    results = get_pretty_print(serialized)
    print(results)
    pprint([result["url"] for result in serialized])

    site_metas = [item.serialize() for item in crawler.site_metas]
    metas = get_pretty_print(site_metas)
    print(metas)
    # pprint(site_metas)

    pprint(crawler.favicons)
    pprint(crawler._dupefilter.fingerprints)
