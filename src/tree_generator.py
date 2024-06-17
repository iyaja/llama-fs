import litellm
import json
import os

from src.select_model import select_model

FILE_PROMPT = """
You will be provided with list of source files and a summary of their contents. For each file, propose a new path and filename, using a directory structure that optimally organizes the files using known conventions and best practices.
Follow good naming conventions. Here are a few guidelines
- Think about your files : What related files are you working with?
- Identify metadata (for example, date, sample, experiment) : What information is needed to easily locate a specific file?
- Abbreviate or encode metadata
- Use versioning : Are you maintaining different versions of the same file?
- Think about how you will search for your files : What comes first?
- Deliberately separate metadata elements : Avoid spaces or special characters in your file names
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


def create_file_tree(summaries: list, incognito=True):
    chat_completion = litellm.completion(
        messages=[
            {"role": "system", "content": FILE_PROMPT},
            {"role": "user", "content": json.dumps(summaries)},
        ],
        model=select_model(incognito),
        response_format={"type": "json_object"},
        temperature=0,
    )

    file_tree = json.loads(chat_completion.choices[0].message.content)["files"]
    return file_tree
