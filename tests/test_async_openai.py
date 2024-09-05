import os
import asyncio
import sys
from openai import AsyncOpenAI
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

client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

async def main() -> None:
    stream = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "đợt này mới có game hắc thoại tây du ra với cốt truyện phóng tác từ tây du ký theo hơi hướng đen tối rất hay, bạn sẽ thử viết ra một cốt truyện phóng tác theo Tây Du, đen tối 1 chút, phóng tác hết mức có thể",
            }
        ],
        model="gpt-4o",
        temperature=0.0,
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()  # Add a newline at the end

if __name__ == "__main__":
    asyncio.run(main())