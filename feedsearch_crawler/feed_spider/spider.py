import base64
import re
import pathlib
from types import AsyncGeneratorType
from typing import Union, Any, List
from w3lib.url import url_query_cleaner

import bs4
from yarl import URL

from feedsearch_crawler.crawler import Crawler, Item, Request, Response

from feedsearch_crawler.feed_spider.dupefilter import NoQueryDupeFilter
from feedsearch_crawler.feed_spider.feed_info import FeedInfo
from feedsearch_crawler.feed_spider.feed_info_parser import FeedInfoParser
from feedsearch_crawler.feed_spider.site_meta import SiteMeta
from feedsearch_crawler.feed_spider.site_meta_parser import SiteMetaParser

# Regex to check that a feed-like string is a whole word to help rule out false positives.
feedlike_regex = re.compile("\\b(rss|feed|atom|json|xml|rdf|feeds)\\b", re.IGNORECASE)

# Regex to check URL string for invalid file types.
file_regex = re.compile(
    ".(jpe?g|png|gif|bmp|mp4|mp3|mkv|md|css|avi|pdf|js|woff?2|svg|ttf)/?$",
    re.IGNORECASE,
)

invalid_filetypes = [
    "jpeg",
    "jpg",
    "png",
    "gif",
    "bmp",
    "mp4",
    "mp3",
    "mkv",
    "md",
    "css",
    "avi",
    "pdf",
    "js",
    "woff",
    "woff2",
    "svg",
    "ttf",
]


class FeedsearchSpider(Crawler):
    duplicate_filter_class = NoQueryDupeFilter
    htmlparser = "html.parser"
    favicon_data_uri = True
    try_urls: Union[List[str], bool] = False
    full_crawl: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.site_meta_processor = SiteMetaParser(self)
        self.feed_info_parser = FeedInfoParser(self)
        self.site_metas = set()
        self.favicons = dict()
        self.post_crawl_callback = self.populate_feed_site_meta
        if "try_urls" in kwargs:
            self.try_urls = kwargs["try_urls"]
        if "favicon_data_uri" in kwargs:
            self.favicon_data_uri = kwargs["favicon_data_uri"]
        if "full_crawl" in kwargs:
            self.full_crawl = kwargs["full_crawl"]

    async def parse(self, request: Request, response: Response) -> AsyncGeneratorType:
        """
        Parse a Response for feeds or site metadata.

        :param request: Request
        :param response: Response
        :return: AsyncGenerator yielding Items, Requests, or iterative AsyncGenerators
        """

        # If the Response is not OK then there's no data to parse.
        if not response.ok:
            return

        # If the Response contains JSON then attempt to parse it as a JsonFeed.
        if response.json:
            if "version" and "jsonfeed" and "feed_url" in response.json:
                yield self.feed_info_parser.parse_item(request, response, type="json")
                return

        if not isinstance(response.text, str):
            self.logger.debug("No text in %s", response)
            return

        url_origin = response.url.origin()
        request_url_origin = request.url.origin()
        # If the returned url is an origin url, or the request url is an origin url (and there may have been a redirect)
        # then parse the site meta.
        if response.url == url_origin or request.url == request_url_origin:
            yield self.site_meta_processor.parse_item(request, response)

        # Restrict the RSS check to the first 500 characters, otherwise it's almost definitely not an actual feed.
        data = response.text.lower()[:500]

        if bool(data.count("<rss") + data.count("<rdf") + data.count("<feed")):
            yield self.feed_info_parser.parse_item(request, response, type="xml")
            return

        # Make sure the Response XML has been parsed if it exists.
        soup = await response.xml
        if not soup:
            return

        # Find all links in the Response.
        links = soup.find_all(self.tag_has_href)
        for link in links:
            href = link.get("href")
            url = self.parse_href_to_url(href)
            if not url:
                continue

            priority = 1 if self.is_feedlike_url(url, href) else 10

            # Follow all valid links if they are a valid "alternate" link (RSS Feed Discovery) or
            # if they look like they might point to valid feeds.
            if self.should_follow_url(url, link, response):
                yield await self.follow(href, self.parse, response, priority=priority)

    async def parse_xml(self, response_text: str) -> Any:
        """
        Parse Response text as XML.
        Used to allow implementations to provide their own XML parser.

        :param response_text: Response text as string.
        :return: None
        """
        return bs4.BeautifulSoup(response_text, self.htmlparser)

    async def process_item(self, item: Item) -> None:
        """
        Process parsed FeedInfo or SiteMeta items.

        :param item: Item object
        :return: None
        """
        if isinstance(item, FeedInfo):
            self.items.add(item)
        elif isinstance(item, SiteMeta):
            self.site_metas.add(item)

    # noinspection PyPep8
    async def populate_feed_site_meta(self) -> None:
        """
        Populate FeedInfo site information with data from the relevant SiteMeta item
        """
        for feed in self.items:
            # Check each SiteMeta for a url host match
            for meta in self.site_metas:
                # If the meta url host begins with www, then we remove it because the feed may be on
                # a different subdomain
                host = meta.url.host
                if not host:
                    self.logger.warning("No host in SiteMeta %s", meta)
                    return
                if host.startswith("www."):
                    host = host[4:]

                # If the meta url host is in the feed url host then we can assume that the feed belongs to that site
                if host in feed.url.host:
                    feed.site_url = meta.url
                    feed.site_name = meta.site_name
                    if not feed.favicon:
                        feed.favicon = meta.icon_url

            # Populate favicon data uri if available
            if feed.favicon:
                feed.favicon_data_uri = self.favicons.get(feed.favicon, "")

    async def create_data_uri(self, request: Request, response: Response) -> None:
        """
        Create a data uri from a favicon image.

        :param request: Request
        :param response: Response
        :return: None
        """
        if not response.ok or not isinstance(response.data, bytes):
            return

        try:
            encoded = base64.b64encode(response.data)
            uri = "data:image/png;base64," + encoded.decode(response.encoding)
            self.favicons[request.url] = uri
        except Exception as e:
            self.logger.warning("Failure encoding image: %s", e)

    def create_start_urls(self, url: Union[str, URL]) -> List[URL]:
        """
        Create URLs for the initial Requests.

        :param url: Original query URL
        :return: List of URLs to search
        """
        if isinstance(url, str):
            if "//" not in url:
                url = f"//{url}"
            url = URL(url)

        if url.scheme not in ["http", "https"]:
            url = url.with_scheme("http")

        origin = url.origin()

        urls = [url, origin]

        # Common paths for feeds.
        suffixes = {
            "index.xml",
            "atom.xml",
            "feeds",
            "feeds/default",
            "feed",
            "feed/default",
            "feeds/posts/default",
            "?feed=rss",
            "?feed=atom",
            "?feed=rss2",
            "?feed=rdf",
            "rss",
            "atom",
            "rdf",
            "index.rss",
            "index.rdf",
            "index.atom",
            "data/rss",
            "rss.xml",
            "index.json",
            "about",
            "about/feeds",
            "rss-feeds",
        }

        if self.try_urls:
            if isinstance(self.try_urls, list):
                urls.extend(origin.join(URL(suffix)) for suffix in self.try_urls)
            else:
                urls.extend(origin.join(URL(suffix)) for suffix in suffixes)

        return urls

    def should_follow_url(self, url: URL, link: bs4.Tag, response: Response) -> bool:
        """
        Check that the link should be followed if it may contain feed information.

        :param link: Link tag.
        :param response: Response
        :return: boolean
        """
        href: str = link.get("href")
        link_type: str = link.get("type")

        # No href value in link.
        if not href:
            return False

        try:
            url = URL(href)
        except UnicodeError as e:
            self.logger.error("Failed to encode href: %s : %s", href, str(e))
            return False

        is_one_jump: bool = self.is_one_jump_from_original_domain(url, response)

        # If the link may have a valid feed type then follow it regardless of the url text.
        if (
            link_type
            and any(
                map(link_type.lower().count, ["application/json", "rss", "atom", "rdf"])
            )
            and "json+oembed" not in link_type
            and is_one_jump
        ):
            return True
        # Else validate the actual URL string for possible feed values.

        else:
            follow = (
                is_one_jump
                and not self.has_invalid_contents(href)
                and self.is_valid_filetype(href)
                and not self.has_comments_in_querystring(url)
            )
            if self.full_crawl:
                return follow
            else:
                return follow and self.is_feedlike_url(url, href)

    @staticmethod
    def tag_has_href(tag: bs4.Tag) -> bool:
        """
        Find all tags that contain links.

        :param tag: XML tag
        :return: boolean
        """
        return tag.has_attr("href")

    @staticmethod
    def is_one_jump_from_original_domain(url: URL, response: Response) -> bool:
        """
        Check that the current URL is only one response away from the originally queried domain.

        We want to be able to follow potential feed links that point to a different domain than
        the originally queried domain, but not to follow any deeper than that.

        Sub-domains of the original domain are ok.

        i.e: the following are ok
            "test.com" -> "feedhost.com"
            "test.com/feeds" -> "example.com/feed.xml"
            "test.com" -> "feeds.test.com"

        not ok:
            "test.com" -> "feedhost.com" (we stop here) -> "feedhost.com/feeds"

        :param url: URL object or string
        :param response: Response object
        :return: boolean
        """

        if not url.is_absolute():
            url = url.join(response.url)

        # This is the first Response in the chain
        if len(response.history) == 1:
            return True

        # URL is same domain
        if url.host == response.history[0].host:
            return True

        # URL is sub-domain
        if response.history[0].host in url.host:
            return True

        # URL domain and current Response domain are different from original domain
        if (
            response.history[-1].host != response.history[0].host
            and url.host != response.history[0].host
        ):
            return False

        return True

    @staticmethod
    def is_valid_filetype(url: str) -> bool:
        """
        Check if url string has an invalid filetype extension.

        :param url: URL string
        :return: boolean
        """
        # if file_regex.search(url.strip()):
        #     return False
        # return True
        suffix = pathlib.Path(url).suffix.strip(".").lower()
        if suffix in invalid_filetypes:
            return False
        return True

    @staticmethod
    def has_comments_in_querystring(url: URL) -> bool:
        """
        Check if URL querystring contains comment keys.

        :param url: URL object
        :return: boolean
        """
        return any(key in url.query for key in ["comment", "comments", "post"])

    @staticmethod
    def is_feedlike_url(url: URL, url_string: str) -> bool:
        """
        Check if url looks like it may point to something resembling a feed.

        :param url: URL object
        :param url_string: URL string
        :return: boolean
        """
        # Check url string without query parameters
        if feedlike_regex.search(url_query_cleaner(url_string)):
            return True
        # Check querystring keys
        for key in url.query:
            if feedlike_regex.search(key):
                return True
        return False

    @staticmethod
    def has_invalid_contents(string: str) -> bool:
        """
        Ignore any string containing the following strings.

        :param string: String to check
        :return: boolean
        """
        return any(
            map(
                string.lower().count,
                ["wp-includes", "wp-content", "wp-json", "xmlrpc", "wp-admin", "/amp/"],
            )
        )
