"""
Implement a rate limiter that does not allow
a user to make more than 10 requests per second.
"""
import asyncio
import time
from datetime import timedelta, datetime


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
        return cls(request_limit_per_period, ExpiringCounter(period_seconds))

    def __init__(self, request_limit_per_period: int, request_limit_counter: ExpiringCounter):
        self._request_limit_per_period = request_limit_per_period
        self._request_limit_counter = request_limit_counter

    async def send_request(self, request_id):
        # Simulated network delay
        await asyncio.sleep(0.2)

        # Simulated server-side processing
        if self._request_limit_counter.count >= self._request_limit_per_period:
            return 429, request_id
        self._request_limit_counter.increment()
        return 200, request_id


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
        server.send_request(id_)
        for id_ in range(15)
    ]
    response_codes = asyncio.run(send_requests(requests_to_be_sent))
    assert len([k for k in response_codes if k[0] == 200]) == 10
    print("[SMOKE TEST PASS] run_smoke_test_server_rate_limiter")


if __name__ == "__main__":
    run_smoke_test_time_to_live_counter()
    run_smoke_test_server_rate_limiter()
