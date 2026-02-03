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
