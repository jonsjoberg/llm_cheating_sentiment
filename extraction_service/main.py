import argparse
import asyncio
from datetime import date, datetime, timedelta, timezone

from dotenv import load_dotenv

import firebase
from config import (
    DEFAULT_LOOKBACK_WINDOW_HOURS,
    STEAM_REQUEST_PER_SECOND,
    apex,
    arc,
    bf6,
    cs2,
    finals,
    marvel,
    pubg,
    tarkov,
)
from defined_types import LLMServiceType, ReviewWithSentiment, SteamProduct
from llm import local_llama, openrouter
from llm.client import LLMClient, extract_cheating_sentiment
from log import log
from mocks import generate_mock_review, generate_mock_steam_product
from steam_product import fetch_steam_reviews, steam_review_base_url

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
    llm_max_concurrent: int,
    llm_max_requests_per_second: int,
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
        max_concurrent=llm_max_concurrent,
        max_request_per_seconds=llm_max_requests_per_second,
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
    parser.add_argument(
        "--test-review",
        type=str,
        help="Extracts the sentiment for the provided test review and prints it to stdout",
    )
    parser.add_argument(
        "--llm-service-type",
        type=str,
        choices=[s.value for s in LLMServiceType],
        required=True,
    )
    args = parser.parse_args()

    firestore_client = firebase.get_firestore_client()

    match args.llm_service_type:
        case LLMServiceType.LOCAL.value:
            llm_client = local_llama.LocalLlama()
            llm_max_concurrent = local_llama.LLM_MAX_CONCURRENT
            llm_max_requests_per_second = local_llama.LLM_MAX_REQUESTS_PER_SECOND
        case LLMServiceType.OPENROUTER.value:
            model = "google/gemma-3-27b-it"
            llm_client = openrouter.OpenRouter(model)
            llm_max_concurrent = openrouter.LLM_MAX_CONCURRENT
            llm_max_requests_per_second = openrouter.LLM_MAX_REQUESTS_PER_SECOND
        case _:
            log.error(f"unknown LLM Client Type: {args.model_service}")
            return

    if args.test_review is not None:
        review = generate_mock_review(args.test_review)
        reviews_with_sentiment = await extract_cheating_sentiment(
            llm_client,
            reviews=[review],
            steam_product=generate_mock_steam_product(),
            max_concurrent=llm_max_concurrent,
            max_request_per_seconds=llm_max_requests_per_second,
        )

        log.info(f"returned sentiment: {reviews_with_sentiment[0].cheating_sentiment}")
        return

    steam_apps = [finals, arc, bf6, cs2, pubg, marvel, tarkov, apex]
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
            llm_max_concurrent=llm_max_concurrent,
            llm_max_requests_per_second=llm_max_requests_per_second,
        )


if __name__ == "__main__":
    asyncio.run(main())
