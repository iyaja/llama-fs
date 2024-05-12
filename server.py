import json
import os
from collections import defaultdict

import colorama
import ollama
from asciitree import LeftAligned
from asciitree.drawing import BOX_LIGHT, BoxStyle
from fastapi import FastAPI, HTTPException
from groq import Groq
from llama_index.core import SimpleDirectoryReader
from pydantic import BaseModel
from termcolor import colored

from src.loader import get_doc_summaries
from src.tree_generator import create_file_tree
import pathlib
from pathlib import Path
from pydantic import BaseModel
from typing import Optional

os.environ["GROQ_API_KEY"] = "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"


class Request(BaseModel):
    path: str
    instruction: Optional[str] = None
    incognito: Optional[bool] = False


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/batch")
async def batch(request: Request):

    path = request.path
    if not os.path.exists(path):
        raise HTTPException(status_code=400, detail="Path does not exist in filesystem")

    summaries = await get_doc_summaries(path)
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
