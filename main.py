"""
Implement a rate limiter that does not allow
a user to make more than 10 requests per second.
"""
import asyncio


async def send_request():
    await asyncio.sleep(0.2)
    return 200


async def run_test():
    response_code = await send_request()
    print(response_code)


if __name__ == "__main__":
    asyncio.run(run_test())
