import json
import os
import pathlib
import queue
from collections import defaultdict
from pathlib import Path
from typing import Optional
import time

import colorama
import ollama
import threading
from asciitree import LeftAligned
from asciitree.drawing import BOX_LIGHT, BoxStyle
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from llama_index.core import SimpleDirectoryReader
from pydantic import BaseModel
from termcolor import colored
from watchdog.observers import Observer

from src.loader import get_dir_summaries
from src.tree_generator import create_file_tree
from src.watch_utils import Handler
from src.watch_utils import create_file_tree as create_watch_file_tree

os.environ["GROQ_API_KEY"] = "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"


class Request(BaseModel):
    path: str
    instruction: Optional[str] = None
    incognito: Optional[bool] = False


class CommitRequest(Request):
    base_path: str
    src_path: str  # Relative to base_path
    dst_path: str  # Relative to base_path


app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Or restrict to ['POST', 'GET', etc.]
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/batch")
async def batch(request: Request):

    path = request.path
    if not os.path.exists(path):
        raise HTTPException(
            status_code=400, detail="Path does not exist in filesystem")

    summaries = await get_dir_summaries(path)
    # Get file tree
    files = create_file_tree(summaries)

    # Recursively create dictionary from file paths
    tree = {}
    for file in files:
        parts = Path(file["dst_path"]).parts
        current = tree
        for part in parts:
            current = current.setdefault(part, {})

    tree = {path: tree}

    tr = LeftAligned(draw=BoxStyle(gfx=BOX_LIGHT, horiz_len=1))
    print(tr(tree))

    # Prepend base path to dst_path
    for file in files:
        # file["dst_path"] = os.path.join(path, file["dst_path"])
        file["summary"] = summaries[files.index(file)]["summary"]

    return files


@app.post("/watch")
async def watch(request: Request):
    path = request.path
    if not os.path.exists(path):
        raise HTTPException(
            status_code=400, detail="Path does not exist in filesystem")

    response_queue = queue.Queue()

    observer = Observer()
    event_handler = Handler(path, create_watch_file_tree, response_queue)
    await event_handler.set_summaries()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    # background_tasks.add_task(observer.start)

    def stream():
        while True:
            response = response_queue.get()
            yield json.dumps(response) + "\n"
            # yield json.dumps({"status": "watching"}) + "\n"
            # time.sleep(5)

    return StreamingResponse(stream())


@app.post("/commit")
async def commit(request: CommitRequest):
    if not os.path.exists(os.path.join(request.base_path, request.src_path)):
        raise HTTPException(
            status_code=400, detail="Source path does not exist in filesystem"
        )

    if not os.path.exists(os.path.join(request.base_path, request.dst_path)):
        os.makedirs(os.path.join(request.base_path, request.dst_path))

    os.rename(
        os.path.join(request.base_path, request.src_path),
        os.path.join(request.base_path, request.dst_path),
    )

    return
