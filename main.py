import os
import json
import argparse
import pathlib
from groq import Groq
from llama_index.core import SimpleDirectoryReader
import colorama
from termcolor import colored
from asciitree import LeftAligned
from asciitree.drawing import BoxStyle, BOX_LIGHT
from src.loader import get_doc_summaries

# import agentops
# import litellm

import click

colorama.init()  # Initializes colorama to make it work on Windows as well

# agentops.init(api_key="483ce794-f363-4983-8c66-3f669e12884b")


@click.command()
@click.argument("src_path", type=click.Path(exists=True))
@click.argument("dst_path", type=click.Path())
@click.option("--auto-yes", is_flag=True, help="Automatically say yes to all prompts")
def main(src_path, dst_path, auto_yes=False):
    os.environ["GROQ_API_KEY"] = (
        "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"
    )

    summaries = get_doc_summaries(src_path)

    for summary in summaries:
        print(colored(summary["file_name"], "green"))  # Print the filename in green
        print(summary["summary"])  # Print the summary of the contents
        print("-" * 80 + "\n")  # Print a separator line with spacing for readability

    # Create File Tree
    PROMPT = """
You will be provided with list of files and a summary of their contents. Read them carefully, then propose a directory structure that optimally organizes the files using known conventions and best practices.


Your response must be a JSON object with the following schema:
```json
    {
      "files": [
        {
          "filename": "name of the file",
          "path": "path under proposed directory structure"
        }
      ]
    }
```
""".strip()

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": json.dumps(summaries)},
        ],
        model="llama3-8b-8192",
        response_format={"type": "json_object"},  # Uncomment if needed
        temperature=0,
    )

    file_tree = json.loads(chat_completion.choices[0].message.content)["files"]

    BASE_DIR = pathlib.Path(dst_path)
    BASE_DIR.mkdir(exist_ok=True)

    # Recursively create dictionary from file paths
    tree = {}
    for file in file_tree:
        parts = pathlib.Path(file["path"]).parts
        current = tree
        for part in parts:
            current = current.setdefault(part, {})

    # for file in file_tree:
    #     parts = pathlib.Path(file["path"]).parts
    #     current = tree
    #     for part in parts:
    #         current = current.setdefault(part, {})

    print(tree)
    tr = LeftAligned(draw=BoxStyle(gfx=BOX_LIGHT, horiz_len=1))
    click.echo(tr(tree))

    if not auto_yes and not click.confirm(
        "Proceed with directory structure?", default=True
    ):
        click.echo("Operation cancelled.")
        return

    for file in file_tree:
        file["path"] = pathlib.Path(file["path"])
        # Create file in specified base directory
        (BASE_DIR / file["path"]).parent.mkdir(parents=True, exist_ok=True)
        with open(BASE_DIR / file["path"], "w") as f:
            f.write("")


if __name__ == "__main__":
    main()
