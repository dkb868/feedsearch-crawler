import asyncio
import copy
import inspect
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Any
from typing import Union

import aiohttp
from yarl import URL

from feedsearch.crawler.duplicatefilter import DuplicateFilter
from feedsearch.crawler.item import Item
from feedsearch.crawler.lib import coerce_url
from feedsearch.crawler.request import Request
from feedsearch.crawler.response import Response

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    uvloop = None
    pass


class Crawler(ABC):
    dupefilter = DuplicateFilter()
    post_crawl_callback = None

    concurrency: int = 10
    max_request_size = 1024 * 1024 * 10

    stats: dict = {
        "requests_added": 0,
        "requests_successful": 0,
        "requests_failed": 0,
        "total_content_length": 0,
        "items_processed": 0,
        "urls_seen": 0,
    }

    def __init__(
        self,
        start_urls: List = None,
        max_tasks: int = 10,
        timeout: int = 10,
        user_agent: str = "",
        *args,
        **kwargs,
    ):
        self.max_tasks = max_tasks
        self.session = None
        self.request_queue = None
        self.items = set()
        self.start_urls = start_urls or []
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
        )
        self.headers = {"User-Agent": self.user_agent}
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.seen_lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(self.concurrency)

    async def _handle_request(self, request: Request):
        try:
            start = time.perf_counter()

            results, response = await request.fetch_callback()

            dur = int((time.perf_counter() - start) * 1000)
            self.logger.debug(
                "Fetched: url=%s dur=%dms status=%s prev=%s",
                response.url,
                dur,
                response.status_code,
                response.originator_url,
            )

            if response.ok:
                self.stats["requests_successful"] += 1
            else:
                self.stats["requests_failed"] += 1

            self.stats["total_content_length"] += response.content_length

            await self.dupefilter.url_seen(response.url, response.method)

            if results:
                await self._process_request_callback_result(results)

        except asyncio.CancelledError:
            self.logger.debug("Cancelled %s", request)
        except Exception as e:
            self.logger.exception("Exception during %s, %s", request, e)
        finally:
            return

    async def _process_request_callback_result(self, result: Any):
        try:
            if inspect.isasyncgen(result):
                async for value in result:
                    await self._process_request_callback_result(value)
            elif inspect.iscoroutine(result):
                await self._process_request_callback_result(await result)
            elif isinstance(result, Request):
                await self._process_request(result)
            elif isinstance(result, Item):
                await self.process_item(result)
                self.stats["items_processed"] += 1
        except Exception as e:
            self.logger.exception(e)

    async def process_item(self, item: Item) -> None:
        self.items.add(item)

    async def _process_request(self, request: Request) -> None:
        seen = await self.dupefilter.url_seen(request.url, request.method)
        if not seen:
            self.stats["requests_added"] += 1
            self.logger.debug("Queue Add: %s", request)
            self.request_queue.put_nowait(request)

    def follow(
        self, url: Union[str, URL], callback=None, response: Response = None, **kwargs
    ) -> Request:
        if isinstance(url, str):
            url = URL(url)

        history = []
        if response:
            url = response.url.join(url)
            history = copy.deepcopy(response.history)

        request = Request(
            url=url,
            request_session=self.session,
            history=history,
            callback=callback,
            xml_parser=self.parse_xml,
            max_size=self.max_request_size,
            **kwargs,
        )

        return request

    @abstractmethod
    async def parse_xml(self, response_text: str):
        raise NotImplementedError("Not Implemented")

    @abstractmethod
    async def parse(self, request: Request, response: Response):
        raise NotImplementedError("Not Implemented")

    async def _work(self):
        while True:
            request = await self.request_queue.get()

            try:
                await asyncio.shield(self._handle_request(request))
            except asyncio.CancelledError:
                self.logger.debug("Cancelled Request: %s", request)
            finally:
                self.request_queue.task_done()

    async def _run_callback(self, callback, *args, **kwargs):
        if not callback:
            return
        if inspect.iscoroutinefunction(callback):
            return await callback(*args, **kwargs)
        elif inspect.isfunction(callback):
            return callback(*args, **kwargs)
        else:
            self.logger.warning("Callback %s must be a coroutine or function", callback)

    def create_start_urls(self, url: Union[str, URL]):
        if isinstance(url, str):
            url = URL(url)

        if url.scheme not in ["http", "https"]:
            url = url.with_scheme("http")

        self.start_urls = [url]

    async def crawl(self, url: Union[URL, str] = ""):
        if url:
            self.create_start_urls(url)

        if not self.start_urls:
            raise ValueError("crawler.start_urls are required")

        start = time.perf_counter()
        self.request_queue = asyncio.Queue()
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)

        for url in self.start_urls:
            await self._process_request(self.follow(coerce_url(url), self.parse))

        workers = [asyncio.create_task(self._work()) for _ in range(self.max_tasks)]

        # When all work is done, exit.
        try:
            async with self.session:
                await asyncio.wait_for(self.request_queue.join(), timeout=self.timeout)
        except asyncio.TimeoutError:
            self.logger.debug("Timed out after %s seconds", self.timeout)
        finally:
            for w in workers:
                w.cancel()

        await self._run_callback(self.post_crawl_callback)

        await self.session.close()

        duration = int((time.perf_counter() - start) * 1000)
        self.stats["duration"] = duration
        self.stats["urls_seen"] = len(self.dupefilter.fingerprints)

        self.logger.info(
            "Crawl finished: urls=%s time=%dms",
            (self.stats["requests_failed"] + self.stats["requests_successful"]),
            duration,
        )
        self.logger.debug("Stats: %s", self.stats)