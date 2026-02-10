from collections import defaultdict
import math
from steam_product import SteamProduct
from datetime import datetime, timezone, date, time
import firebase_admin.firestore_async
from config import FIREBASE_JSON
from log import log
from firebase_admin import credentials, initialize_app
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.query import Query
from llm.client import ReviewWithSentiment
from defined_types import CheatingSentiment
from google.cloud.firestore_v1.base_query import FieldFilter, And


def get_firestore_client() -> AsyncClient:
    cred = credentials.Certificate(FIREBASE_JSON)
    initialize_app(cred)

    return firebase_admin.firestore_async.client()


async def get_last_review_ts(db: AsyncClient, app_id: int) -> datetime | None:
    reviews_ref = db.collection(f"apps/{str(app_id)}/reviews")
    if len(await reviews_ref.limit(1).get()) == 0:
        log.info(f"no reviews found for app_id {app_id}")
        return None

    last_review = (
        await reviews_ref.order_by("timestamp_created", direction=Query.DESCENDING)
        .limit(1)
        .select(["timestamp_created"])
        .get()
    )
    log.info(last_review)
    last_timestamp_created = (
        last_review[0].get("timestamp_created").replace(tzinfo=timezone.utc)
    )
    log.info(
        f"last timestamp created for app_id: {app_id} was {last_timestamp_created.isoformat()}"
    )
    return last_timestamp_created


async def steam_product_exists(db: AsyncClient, app_id: int) -> bool:
    ref = db.document(f"apps/{app_id}")
    doc = await ref.get()
    return doc.exists


async def insert_steam_product(db: AsyncClient, steam_product: SteamProduct):
    log.info(f"inserting steam_product: {steam_product.app_id}")
    await db.document(f"apps/{steam_product.app_id}").set(steam_product.to_dict())


async def ensure_steam_product(db: AsyncClient, steam_product: SteamProduct):
    if not await steam_product_exists(db, steam_product.app_id):
        log.info(f"failed ot find steam_product: {steam_product.app_id}")
        await insert_steam_product(db, steam_product)


async def summarize_reviews(
    db: AsyncClient, steam_product: SteamProduct, dts: set[date]
):

    reviews_reference = db.collection(f"apps/{steam_product.app_id}/reviews")

    for dt in dts:
        start_of_day = datetime.combine(dt, time.min)
        end_of_day = datetime.combine(dt, time.max)

        dt_filter = And(
            [
                FieldFilter("timestamp_created", ">=", start_of_day),
                FieldFilter("timestamp_created", "<=", end_of_day),
            ]
        )

        reviews = await reviews_reference.where(filter=dt_filter).get()
        sentiments = {sentiment.value: 0 for sentiment in CheatingSentiment}
        for review in reviews:
            sentiment = review.get("sentiment")
            sentiments[sentiment] += 1

        await insert_summarized_reviews(db, steam_product, sentiments, dt)


async def insert_summarized_reviews(
    db: AsyncClient,
    steam_product: SteamProduct,
    sentiment_counted: dict[CheatingSentiment, int],
    dt: date,
):
    log.info(
        f"inserting summarized reviews for app {steam_product.app_id} and {dt.isoformat()}"
    )
    await db.document(
        f"apps/{steam_product.app_id}/summarized_reviews/{dt.isoformat()}"
    ).set(sentiment_counted)


async def insert_reviews(
    db: AsyncClient,
    steam_product: SteamProduct,
    reviews_with_sentiment: list[ReviewWithSentiment],
):
    await ensure_steam_product(db, steam_product)

    if len(reviews_with_sentiment) == 0:
        log.info("no reviews to insert, early out")
        return

    batch_size = 500
    n_batches = math.floor(len(reviews_with_sentiment) / batch_size) + 1
    log.info(f"{n_batches} to insert")
    for b in range(n_batches):
        batch = db.batch()
        start_idx = b * batch_size
        end_idx = min((b + 1) * batch_size, len(reviews_with_sentiment))

        log.info(f"creating batch: {b}, start_idx: {start_idx}, end_idx: {end_idx}")

        current_reviews = reviews_with_sentiment[start_idx:end_idx]
        for r in current_reviews:
            if r.cheating_sentiment is None:
                continue

            ref = db.document(
                f"apps/{steam_product.app_id}/reviews/{r.steam_review.recommendation_id}"
            )
            batch.set(ref, r.to_firestore_review().to_dict())
        log.info("commiting batch")
        await batch.commit()
