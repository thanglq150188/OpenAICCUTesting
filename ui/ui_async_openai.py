import os
import asyncio
import sys
import time
import tkinter as tk
from tkinter import ttk
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

class StreamingGUI:
    def __init__(self, master, ccu):
        self.master = master
        self.master.title("OpenAI Streaming Responses")
        self.master.geometry("800x600")

        # Create main frame
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=1)

        # Create canvas
        self.canvas = tk.Canvas(main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create another frame inside the canvas
        self.inner_frame = tk.Frame(self.canvas)

        # Add that frame to a window in the canvas
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.text_widgets = []

        for i in range(ccu):
            frame = tk.Frame(self.inner_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            label = tk.Label(frame, text=f"User {i}:", anchor="w")
            label.pack(fill=tk.X)
            
            text_widget = tk.Text(frame, wrap=tk.WORD, height=4)
            text_widget.pack(fill=tk.X)
            self.text_widgets.append(text_widget)

        # Create start button
        self.start_button = tk.Button(self.master, text="Start Streaming", command=self.start_streaming)
        self.start_button.pack(side=tk.BOTTOM, pady=10)

        self.status_bar = tk.Label(self.master, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_text(self, user_id, content):
        self.text_widgets[user_id].insert(tk.END, content)
        self.text_widgets[user_id].see(tk.END)
        self.master.update_idletasks()

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.master.update_idletasks()

    def start_streaming(self):
        self.start_button.config(state=tk.DISABLED)
        self.update_status("Streaming in progress...")
        asyncio.run(main(len(self.text_widgets), self))
        self.start_button.config(state=tk.NORMAL)

async def process_stream(stream, user_id, gui):
    full_response = ""
    token_count = 0
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            gui.update_text(user_id, content)
            full_response += content
            token_count += len(content.split())
    # gui.update_text(user_id, f"\n\nFull response: {full_response}\n")
    return token_count

async def single_request(user_id, gui):
    try:
        start_time = time.time()
        stream = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"xin chào, hãy nói 1 câu gì dở hơi đi",
                }
            ],
            temperature=0.7,
            model="gpt-4o-mini",
            stream=True
        )
        token_count = await process_stream(stream, user_id, gui)
        end_time = time.time()
        elapsed_time = end_time - start_time
        return elapsed_time, token_count
    except Exception as e:
        gui.update_text(user_id, f"Error: {str(e)}\n")
        return 0, 0

async def main(ccu, gui):
    start_time = time.time()
    tasks = [single_request(i, gui) for i in range(ccu)]
    results = await asyncio.gather(*tasks)
    end_time = time.time()

    total_time = end_time - start_time
    total_tokens = sum(result[1] for result in results)
    avg_tokens_per_second = total_tokens / total_time if total_time > 0 else 0

    performance_report = (
        f"Performance Report: Total time: {total_time:.2f}s, "
        f"Total tokens: {total_tokens}, "
        f"Avg throughput: {avg_tokens_per_second:.2f} tokens/s"
    )
    # gui.update_status(performance_report)

if __name__ == "__main__":
    CCU = 10  # Concurrent Users
    root = tk.Tk()
    gui = StreamingGUI(root, CCU)
    root.mainloop()