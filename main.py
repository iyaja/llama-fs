import os
import json
import argparse
import pathlib
from groq import Groq
from llama_index.core import SimpleDirectoryReader
import colorama
import pathlib
from pathlib import Path
from termcolor import colored
from asciitree import LeftAligned
from asciitree.drawing import BoxStyle, BOX_LIGHT
from src.loader import get_dir_summaries
from src.tree_generator import create_file_tree
import asyncio
from dotenv import load_dotenv
import click
load_dotenv()
colorama.init()  # Initializes colorama to make it work on Windows as well


@click.command()
@click.argument("src_path", type=click.Path(exists=True))
@click.argument("dst_path", type=click.Path())
@click.option("--auto-yes", is_flag=True, help="Automatically say yes to all prompts")
def main(src_path, dst_path, auto_yes=False):

    summaries = asyncio.run(get_dir_summaries(src_path))

    # Get file tree
    files = create_file_tree(summaries)

    BASE_DIR = pathlib.Path(dst_path)
    BASE_DIR.mkdir(exist_ok=True)

    # Recursively create dictionary from file paths
    tree = {}
    for file in files:
        parts = Path(file["dst_path"]).parts
        current = tree
        for part in parts:
            current = current.setdefault(part, {})

    tree = {dst_path: tree}

    tr = LeftAligned(draw=BoxStyle(gfx=BOX_LIGHT, horiz_len=1))
    print(tr(tree))

    # Prepend base path to dst_path
    for file in files:
        file["dst_path"] = os.path.join(src_path, file["dst_path"])
        file["summary"] = summaries[files.index(file)]["summary"]

    if not auto_yes and not click.confirm(
        "Proceed with directory structure?", default=True
    ):
        click.echo("Operation cancelled.")
        return

    for file in files:
        file["path"] = pathlib.Path(file["dst_path"])
        # Create file in specified base directory
        (BASE_DIR / file["path"]).parent.mkdir(parents=True, exist_ok=True)
        with open(BASE_DIR / file["path"], "w") as f:
            f.write("")


if __name__ == "__main__":
    main()
