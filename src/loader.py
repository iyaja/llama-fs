import json
import os
from collections import defaultdict
from llama_index.core import SimpleDirectoryReader
import ollama
from groq import Groq
import weave
import agentops
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Document
from llama_index.core.node_parser import TokenTextSplitter


# @weave.op()
# @agentops.record_function("summarize")
def get_doc_summaries(path: str):
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


# @weave.op()
# @agentops.record_function("load")
def load_documents(path: str):
    reader = SimpleDirectoryReader(input_dir=path, recursive=True)
    splitter = TokenTextSplitter(chunk_size=6144)
    documents = []
    for docs in reader.iter_data():
        # By default, llama index split files into multiple "documents"
        if len(docs) > 1:
            # So we first join all the document contexts, then truncate by token count
            text = splitter.split_text("\n".join([d.text for d in docs]))[0]
            documents.append(Document(text=text, metadata=docs[0].metadata))
    doc_dicts = [{"content": d.text, **d.metadata} for d in documents]
    return doc_dicts


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


# @weave.op()
# @agentops.record_function("query")
def query_summaries(doc_dicts):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    summaries = []
    print("Summarizing documents ...")
    for doc in doc_dicts:
        print("Processing {}".format(doc["file_path"]))
        PROMPT = """
You will be provided with the contents of a file along with its metadata. Provide a summary of the contents. The purpose of the summary is to organize files based on their content. To this end provide a concise but informative summary. Make the summary as specific to the file as possible.

Return a JSON list with the following schema:

```json
{
    "file_path": "path to the file including name",
    "summary": "summary of the content"
}
```
""".strip()

        max_retries = 5
        attempt = 0
        while attempt < max_retries:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": PROMPT},
                        {"role": "user", "content": json.dumps(doc)},
                    ],
                    model="llama3-8b-8192",
                    response_format={"type": "json_object"},
                    temperature=0,
                )
                break
            except Exception as e:
                print("Error status {}".format(e.status_code))
                attempt += 1

        summary = json.loads(chat_completion.choices[0].message.content)
        summaries.append(summary)

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
