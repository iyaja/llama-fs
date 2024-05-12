import asyncio
import json
import os
import time

from groq import Groq
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from src.loader import get_doc_summaries

os.environ["GROQ_API_KEY"] = "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"


class Handler(FileSystemEventHandler):
    def __init__(self, base_path, callback, queue):
        self.base_path = base_path
        self.callback = callback
        self.queue = queue
        self.events = []
        print(f"Watching directory {base_path}")

    async def set_summaries(self):
        print(f"Getting summaries for {self.base_path}")
        self.summaries = await get_doc_summaries(self.base_path)
        print("Done.")

    def on_created(self, event: FileSystemEvent) -> None:
        src_path = os.path.relpath(event.src_path, self.base_path)
        print(f"Created {src_path}")
        # self.callback(event.src_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        src_path = os.path.relpath(event.src_path, self.base_path)
        print(f"Deleted {src_path}")
        # self.callback(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        src_path = os.path.relpath(event.src_path, self.base_path)
        dest_path = os.path.relpath(event.dest_path, self.base_path)
        print(f"Moved {src_path} > {dest_path}")
        self.events.append({"src_path": src_path, "dst_path": dest_path})
        file_tree = self.callback(
            summaries=self.summaries, fs_events=json.dumps({"files": self.events})
        )
        self.queue.put(file_tree)

    # def on_any_event(self, event):
    #     print(event)
    #     print(event.event_type, event.src_path, event.dest_path)
    #     if not event.is_directory:
    #         self.callback(event.src_path)


def create_file_tree(summaries, fs_events):

    FILE_PROMPT = """
You will be provided with list of source files and a summary of their contents. For each file, propose a new path and filename, using a directory structure that optimally organizes the files using known conventions and best practices.

If the file is already named well or matches a known convention, set the destination path to the same as the source path.

Your response must be a JSON object with the following schema:
```json
{
    "files": [
        {
            "src_path": "original file path",
            "dst_path": "new file path under proposed directory structure with proposed file name"
        }
    ]
}
```
""".strip()

    WATCH_PROMPT = f"""
Here are a few examples of good file naming conventions to emulate, based on the files provided:

```json
{fs_events}
```

Include the above items in your response exactly as is, along all other proposed changes.
""".strip()

    client = Groq()
    cmpl = client.chat.completions.create(
        messages=[
            {"content": FILE_PROMPT, "role": "system"},
            {"content": json.dumps(summaries), "role": "user"},
            {"content": WATCH_PROMPT, "role": "system"},
            {"content": json.dumps(summaries), "role": "user"},
        ],
        model="llama3-8b-8192",
        response_format={"type": "json_object"},
        temperature=0,
    )
    print("Model Reponse:")
    print(cmpl.choices[0].message.content)
    return json.loads(cmpl.choices[0].message.content)
