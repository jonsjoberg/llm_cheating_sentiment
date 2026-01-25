import steam_product
import asyncio
from config import finals, STEAM_REQUEST_PER_SECOND, LLM_MAX_CONCURRENT
from datetime import datetime, timezone
from llm import openrouter
from llm.client import extract_cheating_sentiment, LLMClient, ReviewWithSentiment
from dotenv import load_dotenv
load_dotenv()


async def get_reviews_and_sentiment(
    product: steam_product.SteamProduct,
    from_dt: datetime,
    llm_client: LLMClient
) -> list[ReviewWithSentiment]:

    reviews = await steam_product.fetch_steam_reviews(
        product,
        steam_product.steam_review_base_url,
        from_dt=from_dt,
        request_per_second=STEAM_REQUEST_PER_SECOND
    )

    reviews_with_sentiment = await extract_cheating_sentiment(
        client=llm_client,
        reviews=reviews,
        steam_product=product,
        max_concurrent=LLM_MAX_CONCURRENT
    )

    return reviews_with_sentiment


async def main():

    llm_client = openrouter.OpenRouter(openrouter.DEVSTRAL_FREE)

    from_dt = datetime.strptime(
        '2026-01-20', "%Y-%m-%d").replace(tzinfo=timezone.utc)

    product = finals

    reviews_with_sentiment = await get_reviews_and_sentiment(
        product, from_dt, llm_client
    )

    for review in reviews_with_sentiment:
        print(f"{review.steam_product.name} - {review.steam_review.recommendation_id} - {review.cheating_sentiment}")


if __name__ == "__main__":
    asyncio.run(main())
