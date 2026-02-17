import argparse
from defined_types import SteamProduct, ReviewWithSentiment


import firebase
from steam_product import fetch_steam_reviews, steam_review_base_url
import asyncio
from config import (
    LLM_MAX_REQUESTS_PER_SECOND,
    finals,
    STEAM_REQUEST_PER_SECOND,
    LLM_MAX_CONCURRENT,
    DEFAULT_LOOKBACK_WINDOW_HOURS,
    arc,
    bf6,
    cs2,
    pubg,
    marvel,
    tarkov,
    apex,
    cod,
)
from datetime import datetime, timedelta, timezone, date

from llm import local_llama
from llm.client import extract_cheating_sentiment, LLMClient
from dotenv import load_dotenv

load_dotenv()


def get_dates(reviews_with_sentiments: list[ReviewWithSentiment]) -> set[date]:

    dates = set(
        [r.steam_review.timestamp_created.date() for r in reviews_with_sentiments]
    )
    return dates


async def extract_for_steam_product(
    db: firebase.AsyncClient,
    steam_product: SteamProduct,
    llm_client: LLMClient,
):

    last_created_ts = await firebase.get_last_review_ts(db, steam_product.app_id)
    if last_created_ts is None:
        last_created_ts = datetime.now(timezone.utc) - timedelta(
            hours=DEFAULT_LOOKBACK_WINDOW_HOURS
        )

    reviews = await fetch_steam_reviews(
        steam_product,
        steam_review_base_url,
        from_dt=last_created_ts,
        request_per_second=STEAM_REQUEST_PER_SECOND,
    )

    reviews_with_sentiment = await extract_cheating_sentiment(
        client=llm_client,
        reviews=reviews,
        steam_product=steam_product,
        max_concurrent=LLM_MAX_CONCURRENT,
        max_request_per_seconds=LLM_MAX_REQUESTS_PER_SECOND,
    )

    await firebase.insert_reviews(
        db=db,
        steam_product=steam_product,
        reviews_with_sentiment=reviews_with_sentiment,
    )

    updated_dates = get_dates(reviews_with_sentiment)

    await firebase.summarize_reviews(db, steam_product, updated_dates)


async def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--summarize-only", action="store_true")
    args = parser.parse_args()

    firestore_client = firebase.get_firestore_client()

    llm_client = local_llama.LocalLlama()

    steam_apps = [finals, arc, bf6, cs2, pubg, marvel, tarkov, apex, cod]
    if args.summarize_only:
        for app in steam_apps:
            today = datetime.now().date()
            last_10_days = [today - timedelta(days=i) for i in range(10)]
            await firebase.summarize_reviews(firestore_client, app, set(last_10_days))
        return

    for app in steam_apps:
        await extract_for_steam_product(
            db=firestore_client,
            steam_product=app,
            llm_client=llm_client,
        )


if __name__ == "__main__":
    asyncio.run(main())
