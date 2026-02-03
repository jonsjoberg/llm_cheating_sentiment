import asyncio
from log import log
import datetime
import httpx
from pydantic import ValidationError
from defined_types import SteamProduct, SteamReview, SteamReviews

steam_review_base_url = "https://store.steampowered.com/appreviews/{app_id}"


async def fetch_steam_reviews(
    prod: SteamProduct,
    base_url: str,
    from_dt: datetime.datetime,
    request_per_second: float,
    only_english: bool = True
) -> list[SteamReview]:

    log.info(
        f'fetching reviews for app_id {prod.app_id} from {from_dt.isoformat()}'
    )

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
