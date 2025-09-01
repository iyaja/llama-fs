import json
import os
import pathlib
import queue
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Optional
import time
import shutil  # Add this import at the beginning of your file

# Suppress only harmless warnings, keep important error logging
warnings.filterwarnings("ignore", message=".*Palette images with Transparency.*")
warnings.filterwarnings("ignore", message=".*Ignoring wrong pointing object.*")
# Don't suppress all PIL warnings - some might be important

import colorama
import ollama
import threading
from asciitree import LeftAligned
from asciitree.drawing import BOX_LIGHT, BoxStyle
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import SimpleDirectoryReader
from pydantic import BaseModel
from termcolor import colored
from watchdog.observers import Observer

from src.loader import get_dir_summaries
from src.tree_generator import create_file_tree
from src.watch_utils import Handler
from src.watch_utils import create_file_tree as create_watch_file_tree
from src.enhanced_loader import EnhancedFileLoader

from dotenv import load_dotenv
load_dotenv()


class Request(BaseModel):
    path: Optional[str] = None
    instruction: Optional[str] = None
    incognito: Optional[bool] = False


class CommitRequest(BaseModel):
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
    files = create_file_tree(summaries, None)

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

    return {"files": files, "tree": tree}


@app.post("/batch-execute")
async def batch_execute(request: Request):
    """Execute the suggested file moves from batch operation"""
    path = request.path
    if not os.path.exists(path):
        raise HTTPException(
            status_code=400, detail="Path does not exist in filesystem")

    summaries = await get_dir_summaries(path)
    # Get file tree
    files = create_file_tree(summaries, None)

    # Track execution results
    results = []
    errors = []

    # Execute file moves
    for file in files:
        src_path = os.path.join(path, file["src_path"])
        dst_path = os.path.join(path, file["dst_path"])

        try:
            # Skip if source and destination are the same
            if src_path == dst_path:
                results.append({
                    "file": file["src_path"],
                    "status": "skipped",
                    "reason": "Source and destination are the same"
                })
                continue

            # Ensure the destination directory exists
            dst_directory = os.path.dirname(dst_path)
            os.makedirs(dst_directory, exist_ok=True)

            # Move the file
            if os.path.isfile(src_path):
                shutil.move(src_path, dst_path)
                results.append({
                    "file": file["src_path"],
                    "status": "moved",
                    "from": file["src_path"],
                    "to": file["dst_path"]
                })
            else:
                errors.append({
                    "file": file["src_path"],
                    "status": "error",
                    "reason": "Source file does not exist"
                })

        except Exception as e:
            errors.append({
                "file": file["src_path"],
                "status": "error",
                "reason": str(e)
            })

    return {
        "message": f"Batch execution completed. {len(results)} files processed, {len(errors)} errors.",
        "results": results,
        "errors": errors,
        "total_files": len(files)
    }


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
    print('*'*80)
    print(request)
    print(request.base_path)
    print(request.src_path)
    print(request.dst_path)
    print('*'*80)

    src = os.path.join(request.base_path, request.src_path)
    dst = os.path.join(request.base_path, request.dst_path)

    if not os.path.exists(src):
        raise HTTPException(
            status_code=400, detail="Source path does not exist in filesystem"
        )

    # Ensure the destination directory exists
    dst_directory = os.path.dirname(dst)
    os.makedirs(dst_directory, exist_ok=True)

    try:
        # If src is a file and dst is a directory, move the file into dst with the original filename.
        if os.path.isfile(src) and os.path.isdir(dst):
            shutil.move(src, os.path.join(dst, os.path.basename(src)))
        else:
            shutil.move(src, dst)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while moving the resource: {e}"
        )

    return {"message": "Commit successful"}


@app.post("/smart-batch")
async def smart_batch(request: Request):
    """Smart batch processing using enhanced categorization"""
    path = request.path
    if not os.path.exists(path):
        raise HTTPException(
            status_code=400, detail="Path does not exist in filesystem")

    # Use enhanced loader for efficient categorization
    # Use conservative settings to prevent system overload
    enhanced_loader = EnhancedFileLoader(max_concurrent_tasks=3)
    result = await enhanced_loader.get_organized_files(path, use_llm_for_content=True)

    # Create tree structure for visualization
    tree = {}
    for file_info in result["move_plan"]:
        parts = Path(file_info["dst_path"]).parts
        current = tree
        for part in parts:
            current = current.setdefault(part, {})

    tree = {path: tree}

    tr = LeftAligned(draw=BoxStyle(gfx=BOX_LIGHT, horiz_len=1))
    print(tr(tree))

    return {
        "organized_structure": result["organized_structure"],
        "move_plan": result["move_plan"],
        "statistics": result["statistics"],
        "tree": tree,
        "total_files": result["total_files"]
    }


@app.post("/smart-batch-execute")
async def smart_batch_execute(request: Request):
    """Execute smart batch organization"""
    try:
        path = request.path
        if not os.path.exists(path):
            raise HTTPException(
                status_code=400, detail="Path does not exist in filesystem")

        print(f"🔍 Starting smart batch execution for: {path}")

        # Use enhanced loader for efficient categorization (without LLM by default)
        # Use conservative settings to prevent system overload
        enhanced_loader = EnhancedFileLoader(max_concurrent_tasks=3)
        result = await enhanced_loader.get_organized_files(path, use_llm_for_content=False)

        print(f"✅ Generated organization plan with {len(result['move_plan'])} files")
    except Exception as e:
        print(f"❌ Error in smart_batch_execute: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate organization plan: {str(e)}")

    # Track execution results
    results = []
    errors = []

    # Execute file moves with progress tracking
    print(f"📁 Executing file moves for {len(result['move_plan'])} files...")
    for i, file_info in enumerate(result["move_plan"], 1):
        src_path = os.path.join(path, file_info["src_path"])
        dst_path = os.path.join(path, file_info["dst_path"])

        print(f"[{i}/{len(result['move_plan'])}] Processing: {file_info['src_path']}")

        try:
            # Skip if this is flagged as an existing folder (already organized)
            if file_info.get("skip_move", False):
                results.append({
                    "file": file_info["src_path"],
                    "status": "skipped",
                    "reason": "File already in organized folder",
                    "category": file_info["category"],
                    "subcategory": file_info["subcategory"]
                })
                continue

            # Skip if source and destination are the same
            if src_path == dst_path:
                results.append({
                    "file": file_info["src_path"],
                    "status": "skipped",
                    "reason": "Source and destination are the same"
                })
                continue

            # Ensure the destination directory exists
            dst_directory = os.path.dirname(dst_path)
            os.makedirs(dst_directory, exist_ok=True)

            # Move the file
            if os.path.isfile(src_path):
                shutil.move(src_path, dst_path)
                results.append({
                    "file": file_info["src_path"],
                    "status": "moved",
                    "from": file_info["src_path"],
                    "to": file_info["dst_path"],
                    "category": file_info["category"],
                    "subcategory": file_info["subcategory"]
                })
            else:
                errors.append({
                    "file": file_info["src_path"],
                    "status": "error",
                    "reason": "Source file does not exist"
                })

        except Exception as e:
            error_msg = f"Failed to process {file_info['src_path']}: {str(e)}"
            print(f"❌ {error_msg}")
            errors.append({
                "file": file_info["src_path"],
                "status": "error",
                "reason": str(e)
            })

    return {
        "message": f"Smart batch execution completed. {len(results)} files processed, {len(errors)} errors.",
        "results": results,
        "errors": errors,
        "statistics": result["statistics"],
        "total_files": result["total_files"]
    }


@app.post("/quick-stats")
async def quick_stats(request: Request):
    """Get quick statistics about files without LLM analysis"""
    path = request.path
    if not os.path.exists(path):
        raise HTTPException(
            status_code=400, detail="Path does not exist in filesystem")

    enhanced_loader = EnhancedFileLoader()
    stats = enhanced_loader.get_quick_stats(path)

    return {
        "message": "Quick statistics generated",
        "statistics": stats
    }
