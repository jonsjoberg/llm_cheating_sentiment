
from pydantic import BaseModel
import asyncio
from enum import Enum
from steam_product import SteamReview, SteamProduct
from abc import ABC, abstractmethod
import pandas as pd


class CheatingSentiment(Enum):
    POSITIVE = 'positive'
    NOT_MENTIONED = 'not mentioned'
    NEGATIVE = 'negative'

    @classmethod
    def from_str(cls, s: str | None):
        if s is None:
            return None
        elif (s.lower() == 'positive'):
            return CheatingSentiment.POSITIVE
        elif s.lower() in ["not mentioned", "not_mentioned"]:
            return CheatingSentiment.NOT_MENTIONED
        elif s.lower() == 'negative':
            return CheatingSentiment.NEGATIVE

        return None


class ReviewWithSentiment(BaseModel):
    steam_product: SteamProduct
    steam_review: SteamReview
    cheating_sentiment: CheatingSentiment | None


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


async def extract_cheating_sentiment(
    client: LLMClient,
    reviews: list[SteamReview],
    steam_product: SteamProduct,
    max_concurrent: int
) -> list[ReviewWithSentiment]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def controlled_extract(review: SteamReview) -> ReviewWithSentiment:
        async with semaphore:
            return await client.cheating_ref_in_review(review, steam_product)

    tasks = [controlled_extract(r) for r in reviews]
    results = await asyncio.gather(*tasks)

    return results
