from typing import Optional
import asyncio
from log import log
import datetime
import httpx
from pydantic import BaseModel, Field, ValidationError


class SteamProduct(BaseModel):
    name: str
    app_id: int


class Author(BaseModel):
    steam_id: int = Field(alias='steamid')
    num_games_owned: int
    num_reviews: int
    playtime_forever: int
    playtime_last_two_weeks: int
    playtime_at_review: int
    last_played: int


class SteamReview(BaseModel):
    recommendation_id: int = Field(alias="recommendationid")
    author: Author
    language: str
    review: str
    timestamp_created: datetime.datetime
    timestamp_updated: datetime.datetime
    voted_up: bool
    votes_up: int
    votes_funny: int
    weighted_vote_score: float
    comment_count: int
    steam_purchase: bool
    received_for_free: bool
    written_during_early_access: bool
    primarily_steam_deck: bool


class SteamQuerySummary(BaseModel):
    num_reviews: int
    review_score: Optional[float] = None
    review_score_desc: Optional[str] = None
    total_positive: Optional[int] = None
    total_negative: Optional[int] = None
    total_reviews: Optional[int] = None


class SteamReviews(BaseModel):
    success: int
    query_summary: SteamQuerySummary
    reviews: list[SteamReview]
    cursor: str


steam_review_base_url = "https://store.steampowered.com/appreviews/{app_id}"


async def fetch_steam_reviews(
    prod: SteamProduct,
    base_url: str,
    from_dt: datetime.datetime,
    request_per_second: float,
    only_english: bool = True
) -> list[SteamReview]:

    reviews: list[SteamReview] = []

    params = {
        'json': 1,
        'filter': 'recent',
        'num_per_page': 100,
        'language': 'all',
        'cursor': "*",
        'purchase_type': 'all'
    }

    if only_english:
        params['language'] = 'english'

    while True:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                base_url.format(app_id=prod.app_id),
                params=params
            )
            log.info(res.url)

        res.raise_for_status()

        try:
            batch = SteamReviews.model_validate(res.json())
        except ValidationError as e:
            log.error('Failed to parse steam reviews: ', e)
            log.info(res.json())
            break

        for review in batch.reviews:
            if review.timestamp_created >= from_dt:
                reviews.append(review)
            else:
                log.info('reached older reviews, stopping')
                log.info(f'found {len(reviews)} reviews')
                return reviews

        params['cursor'] = batch.cursor
        await asyncio.sleep(1/request_per_second)

    log.info(f'found {len(reviews)} reviews')
    return reviews
