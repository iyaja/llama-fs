# FileFlow Architecture

## System Overview

FileFlow is a client-server application with the following architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Desktop App                      │
│              (React Frontend - TypeScript)                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  MainScreen.tsx - User Interface                    │    │
│  │  - Batch/Watch mode selection                      │    │
│  │  - File path input                                  │    │
│  │  - Tree visualization                              │    │
│  │  - Accept/reject interface                         │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────┬─────────────────────────────────────────────────┘
             │ HTTP Requests (localhost:8000)
             │
┌────────────▼─────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                         │
│  ┌────────────────────────────────────────────────────┐      │
│  │  API Endpoints                                     │      │
│  │  - POST /batch - Process directory                 │      │
│  │  - POST /watch - Monitor changes                   │      │
│  │  - POST /commit - Apply changes                    │      │
│  └────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────┐      │
│  │  Core Modules                                      │      │
│  │  - loader.py - Document loading & summarization    │      │
│  │  - tree_generator.py - Structure proposals         │      │
│  │  - watch_utils.py - File monitoring                │      │
│  └────────────────────────────────────────────────────┘      │
└────────────┬──────────────────────────────────────────────────┘
             │
    ┌────────┴──────────┬────────────┬──────────────┐
    │                   │            │              │
    ▼                   ▼            ▼              ▼
┌────────┐    ┌──────────────┐  ┌────────┐   ┌─────────┐
│ Groq   │    │   Ollama     │  │ Files  │   │watchdog │
│ API    │    │ (Local LLM)  │  │System  │   │(Events) │
└────────┘    └──────────────┘  └────────┘   └─────────┘
```

## Backend Architecture

### Core Components

#### 1. **server.py** - HTTP API Server
Handles incoming requests from the frontend and orchestrates processing.

**Endpoints:**
- `GET /` - Health check
- `POST /batch` - Batch processing endpoint
- `POST /watch` - Watch mode streaming endpoint
- `POST /commit` - Apply file changes

**Key Features:**
- FastAPI async framework
- CORS middleware for cross-origin requests
- Queue-based streaming for watch mode
- AgentOps integration for monitoring

#### 2. **loader.py** - Document Processing
Loads files and generates AI-powered summaries.

**Key Functions:**
```
get_dir_summaries(path: str)
├─ load_documents(path) - Load all files
├─ get_summaries(documents) - Summarize in parallel
└─ Returns: List[{file_path, summary}]

summarize_document(doc, client)
├─ Calls Groq API with document content
└─ Returns: JSON {file_path, summary}

summarize_image_document(doc, client)
├─ Calls Ollama with Moondream model
└─ Returns: Image description
```

**Supported File Types:**
- `.pdf` - PDF documents
- `.txt` - Plain text files
- `.png`, `.jpg`, `.jpeg` - Images
- `.docx`, `.md`, `.py`, `.ts` - (additional formats available)

**Processing:**
- Token-based text splitting (6144 token chunks)
- Async parallel processing with asyncio
- Retry logic with exponential backoff

#### 3. **tree_generator.py** - File Organization
Generates optimal file structures using LLM reasoning.

**Key Function:**
```
create_file_tree(summaries: List, session)
├─ Analyzes file summaries
├─ Calls Groq with organization prompt
├─ LLM proposes src_path → dst_path mappings
└─ Returns: JSON structure with suggested moves
```

**Organization Strategy:**
- Follows naming conventions (dates, metadata)
- Considers file relationships
- Suggests logical hierarchies
- Preserves well-named files (zero temperature = deterministic)

#### 4. **watch_utils.py** - File System Monitoring
Monitors directory changes and learns user patterns.

**Key Class:**
```
Handler (extends FileSystemEventHandler)
├─ set_summaries() - Load initial file summaries
├─ update_summary(path) - Update single file
└─ Event Handlers:
   ├─ on_created(event)
   ├─ on_modified(event)
   ├─ on_moved(event)
   └─ on_deleted(event)
```

**Smart Features:**
- Summary caching to avoid re-processing
- Learns from user file moves
- Only updates changed files
- Includes recent moves as "good examples" in prompts

#### 5. **main.py** - CLI Tool
Command-line interface for batch processing.

**Features:**
- Click-based CLI
- `--auto-yes` flag for automated operation
- Tree visualization
- Directory creation and file staging

## Frontend Architecture

### React Component Structure

```
App.tsx
└── MainScreen.tsx (Main UI)
    ├── Input - Path selection
    ├── Buttons - Batch/Watch controls
    ├── FileLine components - Tree rendering
    ├── FileDetails.tsx - File information
    ├── TelescopeButton.tsx - Incognito mode
    └── Icons/ - SVG icon components
        ├── FileIcon
        ├── FolderIcon
        ├── ImageIcon
        ├── VideoIcon
        ├── MusicIcon
        └── UI Icons
```

### Key Components

**MainScreen.tsx**
- Primary user interface
- Manages batch and watch modes
- Handles file tree visualization
- Manages user accept/reject decisions
- Communicates with backend API

**FileLine.tsx**
- Renders individual files/folders in tree
- Smart icon selection by file type
- Accept/reject buttons per file
- Proper indentation and styling

**FileDetails.tsx**
- Shows detailed information for selected file
- Displays file summary from AI analysis

**TelescopeButton.tsx**
- Toggles between cloud (Groq) and local (Ollama) processing
- "Incognito mode" for privacy

### State Management

```
watchMode: boolean           // Current operating mode
selectedFile: object         // Currently selected file
filePath: string            // Directory being processed
loading: boolean            // Processing state
newOldMap: array            // src → dst path mappings
preOrderedFiles: array      // Flattened file list
acceptedState: array        // User accept/reject decisions
```

## Data Flow

### Batch Mode Flow

```
1. User selects directory & clicks "Process"
   ↓
2. Frontend POST /batch request
   ├─ path: directory path
   ├─ instruction: optional user instructions
   └─ incognito: use local or cloud
   ↓
3. Backend /batch endpoint
   ├─ Calls loader.py:get_dir_summaries(path)
   ├─ For each file:
   │  ├─ Load document
   │  ├─ Generate AI summary
   │  └─ Add to summaries list
   ↓
4. tree_generator.py:create_file_tree()
   ├─ Sends summaries to Groq/Ollama
   ├─ LLM proposes optimal structure
   ├─ Returns: {src_path, dst_path, summary}[] array
   ↓
5. Frontend displays tree
   ├─ visualize with FileLine components
   ├─ User reviews suggestions
   ├─ Accepts/rejects individual changes
   ↓
6. User clicks "Confirm"
   ├─ Frontend sends /commit requests
   ├─ Backend moves files on disk
   ├─ Creates directory structure
   ↓
7. Files reorganized ✓
```

### Watch Mode Flow

```
1. User clicks "Watch" on directory
   ↓
2. Frontend POST /watch (streaming response)
   ↓
3. Backend /watch endpoint
   ├─ Creates watchdog Observer
   ├─ Initializes Handler for directory
   ├─ Loads initial summaries
   └─ Starts streaming responses
   ↓
4. User creates/modifies/moves files
   ↓
5. Handler detects filesystem events
   ├─ Updates file summaries
   ├─ Learns from user moves
   ├─ Queues response updates
   ↓
6. tree_generator.py:create_file_tree()
   ├─ Includes user's recent moves as examples
   ├─ LLM learns organization preferences
   ├─ Suggests similar organization
   ↓
7. Frontend streams updates in real-time
   ├─ Tree refreshes with new suggestions
   ├─ User can accept/reject changes
   ↓
8. Changes applied ✓
```

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Async HTTP framework
- **Groq SDK** - Cloud LLM API
- **Ollama** - Local LLM inference
- **llama-index** - Document processing
- **watchdog** - File system monitoring
- **AsyncIO** - Async processing
- **langchain** - LLM utilities

### Frontend
- **Electron 26+** - Desktop framework
- **React 18+** - UI library
- **TypeScript** - Type safety
- **React Router DOM** - Routing
- **NextUI** - Component library
- **Tailwind CSS** - Styling
- **Webpack** - Module bundler

### AI Models
- **Llama 3.1 70B** (Primary model)
  - Cloud: Via Groq API (<500ms inference)
  - Local: Via Ollama (privacy mode)
- **Moondream** - Image understanding (Ollama)

## Performance Optimizations

1. **Async Processing**
   - Parallel file summarization with asyncio.gather()
   - Non-blocking HTTP requests

2. **Intelligent Caching**
   - File summary caching in watch mode
   - Selective index updates based on filesystem diffs
   - Avoids re-processing unchanged files

3. **Fast Inference**
   - Groq API: <500ms most operations
   - Token-based text splitting to prevent timeouts

4. **Streaming Responses**
   - Watch mode uses HTTP streaming
   - Real-time updates without polling
   - Queue-based event aggregation

5. **Smart Index Rewriting**
   - Only updates necessary file tree sections
   - Reduces LLM processing overhead

## Configuration

See [CONFIGURATION.md](./CONFIGURATION.md) for environment setup and options.

## API Reference

See [API.md](./API.md) for detailed endpoint documentation.
