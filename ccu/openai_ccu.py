import os
import asyncio
import sys
import time
from openai import OpenAI
from dotenv import load_dotenv

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

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

async def process_stream(stream, user_id):
    full_response = ""
    token_count = 0
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            print(f"User {user_id}: {content}", end="", flush=True)
            full_response += content
            token_count += len(content.split())  # Rough estimate of token count
        await asyncio.sleep(0)  # Yield control to allow other coroutines to run
    print(f"\n\nUser {user_id} Full response: {full_response}")
    return token_count

async def single_request(user_id):
    try:
        start_time = time.time()
        stream = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[
                {
                    "role": "user",
                    "content": f"xin chào",
                }
            ],
            model="gpt-4o-mini",
            stream=True
        )
        token_count = await process_stream(stream, user_id)
        end_time = time.time()
        elapsed_time = end_time - start_time
        return elapsed_time, token_count
    except Exception as e:
        print(f"Error for user {user_id}: {str(e)}")
        return 0, 0

async def main(ccu):
    start_time = time.time()
    tasks = [single_request(i) for i in range(ccu)]
    results = await asyncio.gather(*tasks)
    end_time = time.time()

    total_time = end_time - start_time
    total_tokens = sum(result[1] for result in results)
    avg_tokens_per_second = total_tokens / total_time if total_time > 0 else 0

    print(f"\n\nPerformance Report:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Total tokens generated: {total_tokens}")
    print(f"Average throughput: {avg_tokens_per_second:.2f} tokens/second")

if __name__ == "__main__":
    CCU = 1000  # Concurrent Users
    asyncio.run(main(CCU))