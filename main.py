import config
import firebase
import steam_product
import asyncio
from config import LLM_MAX_REQUESTS_PER_SECOND, finals, STEAM_REQUEST_PER_SECOND, LLM_MAX_CONCURRENT, DEFAULT_LOOKBACK_WINDOW_HOURS
from datetime import datetime, timedelta, timezone
from llm import openrouter
from llm.client import extract_cheating_sentiment
from dotenv import load_dotenv
load_dotenv()


async def main():

    firestore_client = firebase.get_firestore_client()
    last_created_ts = await firebase.get_last_review_ts(firestore_client, finals.app_id)
    if last_created_ts is None:
        last_created_ts = (
            datetime.now(timezone.utc) -
            timedelta(hours=DEFAULT_LOOKBACK_WINDOW_HOURS)
        )

    llm_client = openrouter.OpenRouter(config.LLM_MODEL)

    product = finals

    reviews = await steam_product.fetch_steam_reviews(
        product,
        steam_product.steam_review_base_url,
        from_dt=last_created_ts,
        request_per_second=STEAM_REQUEST_PER_SECOND
    )

    reviews_with_sentiment = await extract_cheating_sentiment(
        client=llm_client,
        reviews=reviews,
        steam_product=product,
        max_concurrent=LLM_MAX_CONCURRENT,
        max_request_per_seconds=LLM_MAX_REQUESTS_PER_SECOND,
    )

    await firebase.insert_reviews(
        db=firestore_client,
        steam_product=product,
        reviews_with_sentiment=reviews_with_sentiment
    )


if __name__ == "__main__":
    asyncio.run(main())
