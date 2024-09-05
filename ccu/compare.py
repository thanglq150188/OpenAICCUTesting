import os
import time
import asyncio
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
import sys

load_dotenv(override=True)

def set_event_loop_policy():
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    elif sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    else:
        print(f"Unsupported platform: {sys.platform}")
        sys.exit(1)

set_event_loop_policy()

CONCURRENT_REQUESTS = 100
API_KEY = os.environ.get("OPENAI_API_KEY")

sync_client = OpenAI(api_key=API_KEY)
async_client = AsyncOpenAI(api_key=API_KEY)

def sync_request():
    response = sync_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello, how are you?"}]
    )
    return response.choices[0].message.content

async def async_request():
    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello, how are you?"}]
    )
    return response.choices[0].message.content

def run_sync_benchmark():
    start_time = time.time()
    for _ in range(CONCURRENT_REQUESTS):
        sync_request()
    end_time = time.time()
    return end_time - start_time

async def run_async_benchmark():
    start_time = time.time()
    tasks = [async_request() for _ in range(CONCURRENT_REQUESTS)]
    await asyncio.gather(*tasks)
    end_time = time.time()
    return end_time - start_time

if __name__ == "__main__":
    print(f"Running benchmarks with {CONCURRENT_REQUESTS} concurrent requests...")
    
    sync_time = run_sync_benchmark()
    print(f"Synchronous OpenAI time: {sync_time:.2f} seconds")
    
    async_time = asyncio.run(run_async_benchmark())
    print(f"Asynchronous AsyncOpenAI time: {async_time:.2f} seconds")
    
    speedup = (sync_time - async_time) / sync_time * 100
    print(f"AsyncOpenAI was {speedup:.2f}% faster")