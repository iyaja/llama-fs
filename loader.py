import json
import os
from collections import defaultdict
from llama_index.core import SimpleDirectoryReader
import ollama
from groq import Groq


def get_doc_summaries(path: str) -> List[Dict[str, str, str, str, str, str]]:
    doc_dicts = load_documents(path)
    metadata = process_metadata(doc_dicts)
    
    summaries = query_summaries(doc_dicts)
    
    file_summaries = merge_summary_documents(summaries, metadata)
    
    return file_summaries

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


def load_documents(path: str):
    # reader = SimpleDirectoryReader(input_dir=path, recursive=True)
    reader = SimpleDirectoryReader(input_dir=path)
    documents = reader.load_data()
    doc_dicts = [{"content": d.text, **d.metadata} for d in documents]
    return doc_dicts


def process_metadata(doc_dicts):
    file_seen = set()
    metadata_list = []
    for doc in doc_dicts:
        if doc["file_path"] not in file_seen:
            file_seen.add(doc["file_path"])
            metadata_list.append(doc)
    return metadata_list


def query_summaries(doc_dicts):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    
    PROMPT = f"""
    The following is a list of file contents, along with their metadata. For each file, provide a summary of the contents.
    The purpose of the summary is to organize files based on their content. To this end provide a concise but informative summary.
    Try to make the summary as specific to the file as possible.

    {doc_dicts}

    Return a JSON list with the following schema:

    ```json
    {{
    "files": [
        {{
        "file_path": "path to the file including name",
        "summary": "summary of the content"
        }}
    ]
    }}
    ```
    """.strip()
    

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Always return JSON. Do not include any other text or formatting characters.",
            },
            {
                "role": "user",
                "content": PROMPT,
            },
        ],
        model="llama3-70b-8192",
        response_format={"type": "json_object"},
    )

    summaries = json.loads(chat_completion.choices[0].message.content)["files"]

    return summaries


def merge_summary_documents(summaries, metadata_list):
    list_summaries = defaultdict(list)

    for item in summaries:
        list_summaries[item["file_path"]].append(item["summary"])

    file_summaries = {path: '. '.join(summaries) for path, summaries in list_summaries.items()}

    file_list = [{"summary": file_summaries[file["file_path"]], **file} for file in metadata_list]
    
    return file_list