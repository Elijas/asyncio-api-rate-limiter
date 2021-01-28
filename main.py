"""
Implement a rate limiter that does not allow
a user to make more than 10 requests per second.
"""
import asyncio
import time
from datetime import timedelta, datetime


class TimeToLiveCounter:
    def __init__(self, *, ttl_seconds: float):
        self._ttl_seconds = ttl_seconds
        self._timestamps = []

    def increment(self):
        self._timestamps.append(datetime.now())

    @property
    def count(self):
        self._clear_old_timestamps()
        return len(self._timestamps)

    def _clear_old_timestamps(self):
        now = datetime.now()
        ttl = self._ttl_seconds
        self._timestamps = [
            timestamp
            for timestamp in self._timestamps
            if now < timestamp + timedelta(seconds=ttl)
        ]


class Server:
    def __init__(self, counter: TimeToLiveCounter):
        self._counter = counter

    @classmethod
    async def send_request(cls):
        # Simulated network delay
        await asyncio.sleep(0.2)

        # Simulated server-side processing
        ...
        return 200


async def run_test():
    server = Server(TimeToLiveCounter(ttl_seconds=1))
    response_code = await server.send_request()
    print(response_code)


def smoke_test_time_to_live_counter():
    counter = TimeToLiveCounter(ttl_seconds=0.03)
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


if __name__ == "__main__":
    smoke_test_time_to_live_counter()
