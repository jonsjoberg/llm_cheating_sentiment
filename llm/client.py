from contextlib import nullcontext
import time
from typing import Callable
from defined_types import ReviewWithSentiment

import asyncio
from steam_product import SteamReview, SteamProduct
from abc import ABC, abstractmethod
import pandas as pd


def reviews_to_pandas(reviews: list[ReviewWithSentiment]) -> pd.DataFrame:

    reviews_as_dicts = [
        {
            'app_id': r.steam_product.app_id,
            'product_name': r.steam_product.name,
            'created_dt': r.steam_review.timestamp_created,
            'recommendation_id': r.steam_review.recommendation_id,
            'cheating_sentiment': r.cheating_sentiment
        } for r in reviews
    ]

    return pd.DataFrame(reviews_as_dicts)


class LLMClient(ABC):

    @abstractmethod
    async def cheating_ref_in_review(self, review: SteamReview, steam_product: SteamProduct) -> ReviewWithSentiment:
        pass

    @abstractmethod
    def get_model(self) -> str:
        pass

    @abstractmethod
    def close(self):
        pass

    @staticmethod
    def generate_prompt(review: SteamReview) -> str:
        return f"""Does this review of a game contains positive or negative sentiments of cheating, or is cheating not mentioned at all? 
        If the sentiment is positive reply with "positive", if it is negative reply with "negative", if it's not metioned at all reply with "not mentioned".
        REVIEW: {review.review}."""


class AsyncLimiter:
    def __init__(self, max_concurrency: int | None, max_requests_per_second: int | None):
        self.max_concurrency = max_concurrency
        self.max_requests_per_seconds = max_requests_per_second
        self.rate_limit_delay = None

        self.rate_limit_delay = None if max_requests_per_second is None else 1 / \
            max_requests_per_second

        # self.last_call_time = 0
        self.wait_until = 0
        self.semaphore_cm = asyncio.BoundedSemaphore(
            max_concurrency) if max_concurrency is not None else nullcontext()

    async def run(self, func: Callable, *args, **kwargs):
        async with self.semaphore_cm:
            if self.rate_limit_delay is not None:
                t = time.perf_counter()
                wait_time = self.wait_until - t
                self.wait_until = t + max(0, wait_time) + self.rate_limit_delay
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                # elapsed_time = time.perf_counter() - self.last_call_time

                # self.last_call_time = time.perf_counter()
            return await func(*args, **kwargs)


async def extract_cheating_sentiment(
    client: LLMClient,
    reviews: list[SteamReview],
    steam_product: SteamProduct,
    max_concurrent: int,
    max_request_per_seconds: int
) -> list[ReviewWithSentiment]:

    limiter = AsyncLimiter(
        max_concurrency=max_concurrent,
        max_requests_per_second=max_request_per_seconds
    )

    tasks = [
        limiter.run(
            client.cheating_ref_in_review,
            r,
            steam_product
        ) for r in reviews]
    results = await asyncio.gather(*tasks)

    return results
