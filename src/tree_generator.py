from groq import Groq
import json
import os

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


def create_file_tree(summaries: list):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": FILE_PROMPT},
            {"role": "user", "content": json.dumps(summaries)},
        ],
        model="llama3-8b-8192",
        response_format={"type": "json_object"},  # Uncomment if needed
        temperature=0,
    )

    file_tree = json.loads(chat_completion.choices[0].message.content)["files"]
    return file_tree
