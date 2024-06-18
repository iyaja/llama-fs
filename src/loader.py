import asyncio
import http
import http.server
import json
import os
import base64
from collections import defaultdict

import agentops
import colorama
import weave
import litellm
import ollama
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.schema import ImageDocument
from llama_index.core.node_parser import TokenTextSplitter
from termcolor import colored
from src.select_model import select_model


# @weave.op()
# @agentops.record_function("summarize")
async def get_dir_summaries(path: str, incognito=True):
    doc_dicts = load_documents(path)
    # metadata = process_metadata(doc_dicts)

    summaries = await get_summaries(doc_dicts, incognito=incognito)

    # Convert path to relative path
    for summary in summaries:
        summary["file_path"] = os.path.relpath(summary["file_path"], path)

    return summaries

    # [
    #     {
    #         file_path:
    #         file_name:
    #         file_size:
    #         content:
    #         summary:
    #         creation_date:
    #         last_modified_date:
    #     }
    # ]


# @weave.op()
# @agentops.record_function("load")
def load_documents(path: str):
    reader = SimpleDirectoryReader(
        input_dir=path,
        recursive=True,
        required_exts=[
            ".pdf",
            # ".docx",
            # ".py",
            ".txt",
            # ".md",
            ".png",
            ".jpg",
            ".jpeg",
            # ".ts",
        ],
    )
    splitter = TokenTextSplitter(chunk_size=6144)
    documents = []
    for docs in reader.iter_data():
        # By default, llama index split files into multiple "documents"
        if len(docs) > 1:
            # So we first join all the document contexts, then truncate by token count
            for d in docs:
                # Some files will not have text and need to be handled
                contents = splitter.split_text("\n".join(d.text))
                if len(contents) > 0:
                    text = contents[0]
                else:
                    text = ""
                documents.append(Document(text=text, metadata=docs[0].metadata))
        else:
            documents.append(docs[0])
    return documents


# @weave.op()
# @agentops.record_function("metadata")
def process_metadata(doc_dicts):
    file_seen = set()
    metadata_list = []
    for doc in doc_dicts:
        if doc["file_path"] not in file_seen:
            file_seen.add(doc["file_path"])
            metadata_list.append(doc)
    return metadata_list


async def summarize_document(doc, incognito = True):
    PROMPT = """
You will be provided with the contents of a file along with its metadata. Provide a summary of the contents. The purpose of the summary is to organize files based on their content. To this end provide a concise but informative summary. Make the summary as specific to the file as possible.

Write your response a JSON object with the following schema:

```json
{
    "file_path": "path to the file including name",
    "summary": "summary of the content"
}
```

only return the json, no chit chat
""".strip()


    chat_completion = litellm.completion(
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": json.dumps(doc)},
        ],
        model=select_model(incognito),
        temperature=0,
        max_retries=5,
    )

    summary = json.loads(chat_completion.choices[0].message.content)

    try:
        print(colored(summary["file_path"], "green"))  # Print the filename in green
        print(summary["summary"])  # Print the summary of the contents
        print("-" * 80 + "\n")  # Print a separator line with spacing for readability
    except KeyError as e:
        print(e)
        print(summary)

    return summary

def convert_image_to_base64(path: str, file_type: str) -> str:
    with open(path, 'rb') as image_bytes:
        base64_image = base64.b64encode(image_bytes.read()).decode("utf-8")
        return f"data:{file_type};base64,{base64_image}"

async def summarize_image_document(doc: ImageDocument):
    PROMPT = """
You will be provided with an image along with its metadata. Provide a summary of the image contents. The purpose of the summary is to organize files based on their content. To this end provide a concise but informative summary. Make the summary as specific to the file as possible.

Write your response a JSON object with the following schema:

```json
{
    "file_path": "path to the file including name",
    "summary": "summary of the content"
}
```
""".strip()

    chat_completion = litellm.completion(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Summarize the contents of this image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": convert_image_to_base64(doc.image_path, doc.extra_info.get('file_type'))
                        }
                    }
                ],
            },
        ],
        model=os.environ.get('IMAGE_MODEL') if os.environ.get('IMAGE_MODEL') is not None else "ollama/moondream",
    )

    summary = {
        "file_path": doc.image_path,
        "summary": chat_completion.choices[0].message.content,
    }

    print(colored(summary["file_path"], "green"))  # Print the filename in green
    print(summary["summary"])  # Print the summary of the contents
    print("-" * 80 + "\n")  # Print a separator line with spacing for readability
    return summary


async def dispatch_summarize_document(doc, incognito=True):
    if isinstance(doc, ImageDocument):
        return await summarize_image_document(doc)
    elif isinstance(doc, Document):
        return await summarize_document({"content": doc.text, **doc.metadata}, incognito=incognito)
    else:
        raise ValueError("Document type not supported")


async def get_summaries(documents, incognito=True):
    summaries = await asyncio.gather(
        *[dispatch_summarize_document(doc, incognito=incognito) for doc in documents]
    )
    return summaries


# @weave.op()
# @agentops.record_function("merge")
def merge_summary_documents(summaries, metadata_list):
    list_summaries = defaultdict(list)

    for item in summaries:
        list_summaries[item["file_path"]].append(item["summary"])

    file_summaries = {
        path: ". ".join(summaries) for path, summaries in list_summaries.items()
    }

    file_list = [
        {"summary": file_summaries[file["file_path"]], **file} for file in metadata_list
    ]

    return file_list


################################################################################################
# Non-async versions of the functions                                                        #
################################################################################################


def get_file_summary(path: str, incognito=True):
    reader = SimpleDirectoryReader(input_files=[path]).iter_data()

    docs = next(reader)
    splitter = TokenTextSplitter(chunk_size=6144)
    text = splitter.split_text("\n".join([d.text for d in docs]))[0]
    doc = Document(text=text, metadata=docs[0].metadata)
    summary = dispatch_summarize_document(doc, incognito=incognito)
    return summary
