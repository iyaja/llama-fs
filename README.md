# FileFlow

## AI-Powered Intelligent File Organization

<img src="electron-react-app/assets/llama_fs.png" width="30%" />

> **Your files organized intelligently. Your way.**

FileFlow automatically organizes your files based on their content and conventions. Never waste time manually organizing files again.

---

## 🚀 Key Features

- **Smart Organization** - Uses AI to understand file content and suggest optimal organization
- **Two Operating Modes**:
  - **Batch Mode** - Process a directory, review suggestions, and apply changes
  - **Watch Mode** - Continuous daemon that learns from your edits and proactively organizes new files
- **Privacy First** - Process files locally with Ollama or use fast cloud inference with Groq
- **Blazingly Fast** - Most operations complete in <500ms with intelligent caching
- **Multiple File Types** - PDFs, documents, images, audio, and text files
- **Human-in-the-Loop** - Review and approve every suggestion before applying changes

---

## 🎯 The Problem

Open your `~/Downloads` directory. Or your Desktop. It's probably a mess.

> There are only two hard things in Computer Science: cache invalidation and **naming things**.

FileFlow solves the "naming things" problem by leveraging AI to understand your files and organize them intelligently.

---

## ⚡ How It Works

### Batch Mode
1. Select a directory
2. FileFlow analyzes all files and suggests an optimal structure
3. Review suggestions and apply changes

### Watch Mode
1. Select a directory to monitor
2. FileFlow continuously watches for changes
3. **Learns from your edits** - When you move 1-3 files into a folder, FileFlow automatically organizes the rest
4. Applies changes with your approval

**Example:** Create a folder for "2024 Tax Documents" and move a couple files into it. FileFlow will automatically move the rest of your tax-related files there!

---

## 🔒 Privacy & Performance

- **Incognito Mode** - Route all requests through Ollama for local processing (uses same Llama 3 model as cloud version)
- **Smart Caching** - Selective index rewriting based on filesystem changes
- **Fast Inference** - Cloud mode via Groq completes most operations in <500ms
- **Your Choice** - Toggle between cloud and local processing anytime

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, Groq API, Ollama
- **Frontend**: Electron, React 18, TypeScript, Tailwind CSS
- **AI**: Llama 3.1 70B (via Groq or Ollama)
- **Performance**: Smart caching, async processing, streaming responses

## 📋 Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ (for frontend)
- Groq API key (free at [console.groq.com](https://console.groq.com/keys))
- Optional: Ollama for local processing

#### Step 1: Clone the Repository
```bash
git clone https://github.com/iyaja/llama-fs.git
cd llama-fs
```

#### Step 2: Set Up Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Groq API key
# Get one free at: https://console.groq.com/keys
```

#### Step 3: Install Backend Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Install Frontend Dependencies
```bash
cd electron-react-app
npm install
cd ..
```

#### Step 5: (Optional) Set Up Local Processing
For privacy-first operation, install Ollama and download the Moondream model:
```bash
ollama pull moondream
```

---

## 🎮 Usage

### Running the Application

**Terminal 1 - Start Backend Server:**
```bash
fastapi dev server.py
# Runs on http://localhost:8000
```

**Terminal 2 - Start Frontend:**
```bash
cd electron-react-app
npm start
# Electron app opens with dev tools
```

### Batch Mode (Single Directory)
1. Select a directory path
2. Click "Process" to analyze files
3. Review suggested reorganization
4. Accept/reject individual changes
5. Click "Confirm" to apply changes

### Watch Mode (Continuous Monitoring)
1. Select a directory to monitor
2. Click "Watch" to start monitoring
3. FileFlow watches for new/changed files
4. As you manually organize files, FileFlow learns your patterns
5. Suggestions update in real-time

---

## 🔧 API Reference

### POST /batch
Process a directory and get file organization suggestions.

```bash
curl -X POST http://127.0.0.1:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/directory",
    "instruction": "organize my files",
    "incognito": false
  }'
```

**Parameters:**
- `path` - Directory to process
- `instruction` - (Optional) Special instructions for organization
- `incognito` - Use local Ollama (true) or cloud Groq (false)

### POST /watch
Start watching a directory for changes.

### POST /commit
Apply accepted file moves.

---

## 🏗️ Architecture

FileFlow consists of:
- **Backend** (Python/FastAPI) - File analysis, summarization, organization logic
- **Frontend** (Electron/React) - User interface for batch and watch modes
- **AI Models** - Llama 3.1 70B via Groq or Ollama

See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for detailed architecture information.

---

## 📚 Documentation

- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - System design and components
- [CONFIGURATION.md](./docs/CONFIGURATION.md) - Environment setup and options
- [API.md](./docs/API.md) - Detailed API documentation

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built with Llama 3.1 via [Groq](https://groq.com) and [Ollama](https://ollama.ai)
