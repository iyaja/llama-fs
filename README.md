# LlamaFS

<img src="electron-react-app/assets/llama_fs.png" width="30%" />

## Inspiration

[Watch the explainer video](https://x.com/AlexReibman/status/1789895425828204553)

Open your `~/Downloads` directory. Or your Desktop. It's probably a mess...

> There are only two hard things in Computer Science: cache invalidation and **naming things**.

## What it does

LlamaFS is a self-organizing file manager. It automatically renames and organizes your files based on their content and well-known conventions (e.g., time). It supports many kinds of files, including images (through Moondream) and audio (through Whisper).

LlamaFS runs in two "modes" - as a batch job (batch mode), and an interactive daemon (watch mode).

In batch mode, you can send a directory to LlamaFS, and it will return a suggested file structure and organize your files.

In watch mode, LlamaFS starts a daemon that watches your directory. It intercepts all filesystem operations and uses your most recent edits to proactively learn how you rename file. For example, if you create a folder for your 2023 tax documents, and start moving 1-3 files in it, LlamaFS will automatically create and move the files for you!

## How we built it

We built LlamaFS on a Python backend, leveraging the Llama3 model through Ollama for local file content summarization and tree structuring. The frontend is crafted with Electron, providing a sleek, user-friendly interface that allows users to interact with the suggested file structures before finalizing changes.

- **It's extremely fast!** (by LLM standards)! Most file operations are processed in <500ms in watch mode. This is because of our smart caching that selectively rewrites sections of the index based on the minimum necessary filesystem diff. And of course, Ollama's fast local inference. 😉

- **It's immediately useful** - It's very low friction to use and addresses a problem almost everyone has. We started using it ourselves on this project (very Meta).

- **Privacy-focused** - All processing happens locally using Ollama, so your files never leave your machine.

## What's next for LlamaFS

- Find and remove old/unused files
- We have some really cool ideas for - filesystem diffs are hard...

## Installation

### Prerequisites

Before installing, ensure you have the following requirements:
- Python 3.10 or higher
- pip (Python package installer)
- Ollama (for local LLM inference)

### Installing

To install the project, follow these steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/iyaja/llama-fs.git
   ```

2. Navigate to the project directory:
    ```bash
    cd llama-fs
    ```

3. Install requirements
   ```bash
   pip install -r requirements.txt
   ```

4. Install and pull the required Ollama models:
    ```bash
    # For text processing
    ollama pull llama3.1:8b

    # For image processing (required for image files)
    ollama pull moondream
    ```

## Usage

To serve the application locally using FastAPI, run the following command
   ```bash
   fastapi dev server.py
   ```

This will run the server by default on port 8000. The API provides several endpoints:

### Smart Categorization (Recommended) ⭐

#### 1. Quick Statistics
Get instant statistics about files without LLM analysis:
   ```bash
   curl -X POST http://127.0.0.1:8000/quick-stats \
    -H "Content-Type: application/json" \
    -d '{"path": "/Users/<username>/Downloads/", "instruction": "string", "incognito": false}'
   ```

#### 2. Smart Preview Organization
Efficient categorization using file extensions and patterns, with optional LLM enhancement:
   ```bash
   curl -X POST http://127.0.0.1:8000/smart-batch \
    -H "Content-Type: application/json" \
    -d '{"path": "/Users/<username>/Downloads/", "instruction": "string", "incognito": false}'
   ```

#### 3. Smart Execute Organization
Automatically organize files using smart categorization:
   ```bash
   curl -X POST http://127.0.0.1:8000/smart-batch-execute \
    -H "Content-Type: application/json" \
    -d '{"path": "/Users/<username>/Downloads/", "instruction": "string", "incognito": false}'
   ```

### Legacy Endpoints

#### 4. Preview File Organization (Batch Mode)
This endpoint analyzes files and suggests organization without moving them:
   ```bash
   curl -X POST http://127.0.0.1:8000/batch \
    -H "Content-Type: application/json" \
    -d '{"path": "/Users/<username>/Downloads/", "instruction": "string", "incognito": false}'
   ```

#### 5. Execute File Organization (Batch Mode)
This endpoint analyzes files and automatically moves them to the suggested locations:
   ```bash
   curl -X POST http://127.0.0.1:8000/batch-execute \
    -H "Content-Type: application/json" \
    -d '{"path": "/Users/<username>/Downloads/", "instruction": "string", "incognito": false}'
   ```

#### 6. Watch Mode (Real-time)
This endpoint watches a directory for changes and suggests organization in real-time:
   ```bash
   curl -X POST http://127.0.0.1:8000/watch \
    -H "Content-Type: application/json" \
    -d '{"path": "/Users/<username>/Downloads/", "instruction": "string", "incognito": false}'
   ```

#### 7. Individual File Move
This endpoint moves a single file to a new location:
   ```bash
   curl -X POST http://127.0.0.1:8000/commit \
    -H "Content-Type: application/json" \
    -d '{"base_path": "/Users/<username>/Downloads/", "src_path": "old_file.pdf", "dst_path": "organized/new_file.pdf"}'
   ```

## Smart Categorization System

The smart categorization system organizes files efficiently using:

### **First-Level Categories**
- **documents** - PDFs, Word docs, text files
- **spreadsheets** - Excel, CSV files
- **presentations** - PowerPoint files
- **images** - Photos, graphics, screenshots
- **videos** - Video files and recordings
- **audio** - Music and audio files
- **3d-printing** - STL, GCODE files
- **installers** - Setup and installation files
- **executables** - Programs and scripts
- **archives** - Compressed files
- **code** - Source code files
- **data** - Configuration and data files

### **Second-Level Subcategories**
- **documents**: manuals, reports, legal, general
- **images**: screenshots, photos, logos, general
- **3d-printing**: gcode, models, general
- **installers**: installers, uninstallers, general
- **code**: scripts, config, source

### **Smart Features**
- **Locationally exempt files** - Development files (`.py`, `.ts`, `.js`, `.bat`, etc.) and system files stay in place
- **Existing folder detection** - Files already in organized folders are not moved "leftwards" in the directory tree
- **Extension-based categorization** for instant organization
- **Filename pattern matching** (e.g., "Setup.exe" → installers)
- **MIME type detection** for unknown extensions
- **LLM content analysis** for enhanced categorization
- **Hierarchical organization** with categories and subcategories
