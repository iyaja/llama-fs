# LlamaFS

## Inspiration

Open your `~/Downloads` directory. Or your Desktop. It's probably a mess...

> There are only two hard things in Computer Science: cache invalidation and **naming things**.

## What it does

LlamaFS is a self-organizing file manager. It automatically renames and organizes your files based on their contents and well-known conventions (e.g., time). It supports many kinds of file, and even images (through Moondream) and audio (through Whisper).

LlamaFS runs in two "modes" - as a batch job (batch mode), and an interactive daemon (watch mode).

In batch mode, you 

In watch mode, LlamaFS starts a daemon that watches your directory. It intercepts all filesystem operations, updates i and uses your most recent edits in context to proactively learn and how, so you don't 
learns predict how you rename file. e.g. if you create a folder for 2023 tax documents, and start moving 1-3 file in it, LlamaFS will automatically creates, and move the right!

Uhh... Sending all my personal files to an API provider?! No thank you!

 it has a toggle for "incognito mode", allowing you route every request through Ollama instead of Groq. Since they use the same Llama 3 model, the perform identically.

## How we built it

We built LlamaFS on a Python backend, leveraging the Llama3 model through Groq for file content summarization and tree structuring. For local processing, we integrated Ollama running the same model to ensure privacy in incognito mode. The frontend is crafted with Electron, providing a sleek, user-friendly interface that allows users to interact with the suggested file structures before finalizing changes.

- **It's extremely fast!** (for LLM standards)! Most file ops are processed in <500ms in watch mode. This is because of our smart caching, that selectively rewrites sections of the index based on the minimum nessecary filesystem diff. And of course, Groq's super fast inference API. 😉

- **It's immediately useful** - It's very low friction to use, and a problem almost everyone has. We started using it ourselves on this project (very Meta)


## What's next for LlamaFS

- Find and remove old/unused files
- We have some really cool ideas for - filesystem diffs are hard...


## Installation

### Prerequisites

Before installing, ensure you have the following requirements:
- Python 3.10 or higher
- pip (Python package installer)

### Installing

To install the project, follow these steps:
Clone the repository:
   ```bash
   git clone https://github.com/iyaja/llama-fs.git
   ```

Navigate to the project directory:
    ```bash
    cd llama-fs
    ```

