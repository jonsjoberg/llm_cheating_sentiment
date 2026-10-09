import asyncio
from datetime import datetime
import time

import pytest
from client import AsyncLimiter


@pytest.mark.asyncio
async def test_async_limiter_no_max_concurrency_no_rps():

    async_limiter = AsyncLimiter(
        max_concurrency=None, max_requests_per_second=None)
    active_tasks = 0
    n_tasks = 5
    completed_tasks = 0

    async def mock_task():
        nonlocal active_tasks, completed_tasks
        active_tasks += 1
        await asyncio.sleep(0.1)
        active_tasks -= 1
        completed_tasks += 1

    tasks = [async_limiter.run(mock_task) for _ in range(n_tasks)]
    await asyncio.gather(*tasks)

    assert active_tasks == 0
    assert completed_tasks == n_tasks


@pytest.mark.asyncio
async def test_async_limiter_max_concurrency_no_rps():

    concurrency = 2
    async_limiter = AsyncLimiter(
        max_concurrency=concurrency, max_requests_per_second=None
    )
    active_tasks = 0
    n_tasks = 5
    completed_tasks = 0
    max_observerd_concurrency = 0

    async def mock_task():
        nonlocal active_tasks, completed_tasks, max_observerd_concurrency
        active_tasks += 1
        max_observerd_concurrency = max(
            active_tasks, max_observerd_concurrency)
        await asyncio.sleep(0.1)
        active_tasks -= 1
        completed_tasks += 1

    tasks = [async_limiter.run(mock_task) for _ in range(n_tasks)]
    await asyncio.gather(*tasks)

    assert active_tasks == 0
    assert completed_tasks == n_tasks
    assert max_observerd_concurrency == concurrency


@pytest.mark.asyncio
async def test_async_limiter_no_max_concurrency_rps():

    max_rps = 1
    async_limiter = AsyncLimiter(
        max_concurrency=None, max_requests_per_second=max_rps
    )
    active_tasks = 0
    n_tasks = 3
    completed_tasks = 0

    start_time = time.perf_counter()

    async def mock_task():
        nonlocal active_tasks, completed_tasks
        active_tasks += 1
        print(f'task starting at {datetime.now().strftime('%H:%M:%S.%f')}')
        active_tasks -= 1
        completed_tasks += 1

    tasks = [async_limiter.run(mock_task) for _ in range(n_tasks)]
    await asyncio.gather(*tasks)

    elapsed_time = time.perf_counter() - start_time

    assert active_tasks == 0
    assert completed_tasks == n_tasks
    assert elapsed_time >= 2
    assert elapsed_time <= 2.5


@pytest.mark.asyncio
async def test_extract_cheating_sentiment_robustness():
    from client import LLMClient, extract_cheating_sentiment
    from defined_types import ReviewWithSentiment, CheatingSentiment
    from mocks import generate_mock_review, generate_mock_steam_product

    # Define a mock LLMClient that behaves differently for different recommendation IDs
    class MockLLMClient(LLMClient):
        async def cheating_ref_in_review(
            self, review, steam_product
        ) -> ReviewWithSentiment:
            if review.recommendation_id == 1:
                # Normal success path
                return ReviewWithSentiment(
                    steam_product=steam_product,
                    steam_review=review,
                    cheating_sentiment=CheatingSentiment.POSITIVE,
                )
            elif review.recommendation_id == 2:
                # Error path: raises an exception
                raise RuntimeError("Simulated connection error")
            elif review.recommendation_id == 3:
                # Timeout path: sleeps longer than the timeout parameter
                await asyncio.sleep(0.5)
                return ReviewWithSentiment(
                    steam_product=steam_product,
                    steam_review=review,
                    cheating_sentiment=CheatingSentiment.NEGATIVE,
                )
            # Default fallback
            return ReviewWithSentiment(
                steam_product=steam_product,
                steam_review=review,
                cheating_sentiment=CheatingSentiment.NOT_MENTIONED,
            )

        def get_model(self) -> str:
            return "mock"

        def close(self):
            pass

    client = MockLLMClient()
    steam_product = generate_mock_steam_product()

    r1 = generate_mock_review("First review")
    r1.recommendation_id = 1

    r2 = generate_mock_review("Second review")
    r2.recommendation_id = 2

    r3 = generate_mock_review("Third review")
    r3.recommendation_id = 3

    reviews = [r1, r2, r3]

    # Run extraction with a short timeout of 0.1 seconds to trigger timeout for r3
    results = await extract_cheating_sentiment(
        client=client,
        reviews=reviews,
        steam_product=steam_product,
        max_concurrent=3,
        max_request_per_seconds=10,
        timeout=0.1,
    )

    assert len(results) == 3

    # Review 1 should succeed
    assert results[0].steam_review.recommendation_id == 1
    assert results[0].cheating_sentiment == CheatingSentiment.POSITIVE

    # Review 2 raised an exception, should return None sentiment
    assert results[1].steam_review.recommendation_id == 2
    assert results[1].cheating_sentiment is None

    # Review 3 timed out, should return None sentiment
    assert results[2].steam_review.recommendation_id == 3
    assert results[2].cheating_sentiment is None
