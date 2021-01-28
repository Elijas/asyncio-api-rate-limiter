"""
Implement a rate limiter that does not allow
a user to make more than 10 requests per second.
"""
import asyncio
import time
from collections import defaultdict
from datetime import timedelta, datetime
from pprint import pp


class ExpiringCounter:
    def __init__(self, seconds: float):
        self._seconds = seconds
        self._timestamps = []

    def increment(self):
        self._timestamps.append(datetime.now())

    @property
    def count(self):
        self._clear_old_timestamps()
        return len(self._timestamps)

    def _clear_old_timestamps(self):
        now = datetime.now()
        self._timestamps = [
            timestamp
            for timestamp in self._timestamps
            if now < timestamp + timedelta(seconds=self._seconds)
        ]


class Server:
    @classmethod
    def init_from_config(cls, request_limit_per_period: int, period_seconds: float):
        return cls(request_limit_per_period, defaultdict(lambda: ExpiringCounter(period_seconds)))

    def __init__(self, request_limit_per_period: int, request_limit_multitenant_counter):
        self._request_limit_per_period = request_limit_per_period
        self._request_limit_multitenant_counter = request_limit_multitenant_counter

    async def send_request(self, user_id, request_id):
        # Simulated network delay
        await asyncio.sleep(0.2)

        # Simulated server-side processing
        counter = self._request_limit_multitenant_counter[user_id]
        if counter.count >= self._request_limit_per_period:
            return 429, user_id, request_id
        counter.increment()
        return 200, user_id, request_id


def run_smoke_test_time_to_live_counter():
    counter = ExpiringCounter(seconds=0.03)
    assert counter.count == 0
    counter.increment()
    counter.increment()
    assert counter.count == 2
    time.sleep(0.02)
    assert counter.count == 2
    counter.increment()
    assert counter.count == 3
    time.sleep(0.02)
    assert counter.count == 1
    time.sleep(0.02)
    assert counter.count == 0
    print("[SMOKE TEST PASS] smoke_test_time_to_live_counter")


async def send_requests(reqs):
    return await asyncio.gather(*reqs)


def run_smoke_test_server_rate_limiter():
    server = Server.init_from_config(request_limit_per_period=10, period_seconds=1)
    requests_to_be_sent = [
        server.send_request(user_id, user_request_id)
        for user_id in ('bob', 'alice')
        for user_request_id in range(15)
    ]
    responses = asyncio.run(send_requests(requests_to_be_sent))
    pp(responses)
    assert len([k for k in responses if k[0] == 200]) == 2 * 10
    print("[SMOKE TEST PASS] run_smoke_test_server_rate_limiter")


if __name__ == "__main__":
    run_smoke_test_time_to_live_counter()
    run_smoke_test_server_rate_limiter()

""" 
OUTPUT:

[SMOKE TEST PASS] smoke_test_time_to_live_counter
[(200, 'bob', 0),
 (200, 'bob', 1),
 (200, 'bob', 2),
 (200, 'bob', 3),
 (200, 'bob', 4),
 (200, 'bob', 5),
 (200, 'bob', 6),
 (200, 'bob', 7),
 (200, 'bob', 8),
 (200, 'bob', 9),
 (429, 'bob', 10),
 (429, 'bob', 11),
 (429, 'bob', 12),
 (429, 'bob', 13),
 (429, 'bob', 14),
 (200, 'alice', 0),
 (200, 'alice', 1),
 (200, 'alice', 2),
 (200, 'alice', 3),
 (200, 'alice', 4),
 (200, 'alice', 5),
 (200, 'alice', 6),
 (200, 'alice', 7),
 (200, 'alice', 8),
 (200, 'alice', 9),
 (429, 'alice', 10),
 (429, 'alice', 11),
 (429, 'alice', 12),
 (429, 'alice', 13),
 (429, 'alice', 14)]
[SMOKE TEST PASS] run_smoke_test_server_rate_limiter

Process finished with exit code 0
"""
