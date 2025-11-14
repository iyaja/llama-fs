# FileFlow Configuration

## Environment Variables

Create a `.env` file in the project root with the following variables:

### Required

**GROQ_API_KEY** (required for cloud mode)
```
GROQ_API_KEY=your_groq_api_key_here
```
- Get a free API key at: https://console.groq.com/keys
- Used for fast cloud inference with Llama 3.1 70B
- Groq provides generous free tier with rate limits

### Optional

**AGENTOPS_API_KEY** (optional monitoring)
```
AGENTOPS_API_KEY=your_agentops_api_key_here
```
- Get one at: https://app.agentops.ai/settings/projects
- Enables performance monitoring and session replay
- Shows latency, cost per session, and function traces
- Useful for debugging and optimization

## Setup Instructions

### 1. Copy Environment Template
```bash
cp .env.example .env
```

### 2. Get Groq API Key
1. Visit https://console.groq.com/keys
2. Sign up (free account)
3. Create an API key
4. Copy the key to your `.env` file

### 3. (Optional) Set Up AgentOps
1. Visit https://app.agentops.ai
2. Create an account
3. Go to Project Settings
4. Copy your API key to `.env`

### 4. (Optional) Set Up Ollama for Local Processing

For privacy-first operation, install Ollama and the Moondream image model:

```bash
# Install Ollama (https://ollama.ai)
# Then download Moondream:
ollama pull moondream

# You can also pull other models:
ollama pull llama2       # For local text processing
ollama pull mistral      # Alternative model
```

When using incognito mode in FileFlow, requests are routed to your local Ollama instance instead of Groq.

## Operational Modes

### Cloud Mode (Default)
- Uses Groq API for fast inference
- Requires: `GROQ_API_KEY`
- Speed: <500ms most operations
- Cost: Free tier available; paid plans for higher usage
- Privacy: Files sent to Groq servers

### Local Mode (Incognito)
- Uses local Ollama for all processing
- Requires: Ollama installed + `ollama pull moondream`
- Speed: Depends on hardware (typically 2-5 seconds)
- Cost: Free (hardware dependent)
- Privacy: All processing local, no external API calls

## File Type Support

### Text Documents
- `.pdf` - PDF files (via document loaders)
- `.txt` - Plain text
- `.docx` - Word documents
- `.md` - Markdown files
- `.py` - Python files
- `.ts` - TypeScript files

### Images
- `.png` - PNG images
- `.jpg` - JPEG images
- `.jpeg` - JPEG images
- `.gif` - GIF images (treated as static)

### Audio (Experimental)
- `.mp3` - MP3 audio
- `.wav` - WAV audio
- `.flac` - FLAC audio
- `.ogg` - OGG audio

## Advanced Configuration

### Customizing LLM Prompts

Edit prompts in:
- `src/tree_generator.py` - File organization prompts
- `src/loader.py` - Summarization prompts
- `src/watch_utils.py` - Watch mode learning prompts

### Adjusting Performance

**Token Chunk Size** (loader.py)
```python
CHUNK_SIZE = 6144  # Tokens per chunk
```
- Lower = faster but less context
- Higher = more context but slower

**Temperature** (tree_generator.py)
```python
temperature=0  # Deterministic output
```
- 0 = Always same result for same input
- Higher = More creative/variable

**File Monitoring** (watch_utils.py)
- Adjust debounce time for file events
- Configure summary update frequency

## Troubleshooting

### "GROQ_API_KEY not found"
- Ensure `.env` file exists in project root
- Check that GROQ_API_KEY is set correctly
- Reload/restart the application

### "Connection refused on localhost:8000"
- Ensure backend is running: `fastapi dev server.py`
- Check that no other service is using port 8000
- Check firewall settings

### "Ollama connection failed"
- Ensure Ollama is installed and running
- Verify Ollama is listening on localhost:11434 (default)
- Run: `ollama pull moondream` to download the model

### Slow Processing
- Check your internet connection (for cloud mode)
- Verify Groq/Ollama response times
- Check system resources (CPU/RAM)
- Reduce chunk size for faster processing

## Security Notes

1. **API Keys**
   - Never commit `.env` to version control
   - `.env` is already in `.gitignore`
   - Keep API keys confidential

2. **Local Processing**
   - Use incognito mode for sensitive files
   - Ollama runs locally without network transmission
   - Audit local Ollama setup for security

3. **File Access**
   - FileFlow has access to all files in monitored directories
   - Ensure proper file permissions
   - Review directories before processing

## Performance Tips

1. **Batch Mode**
   - Process smaller directories for faster results
   - Start with 10-20 files for testing

2. **Watch Mode**
   - Watch mode uses smart caching for performance
   - First scan is slowest (analyzes all files)
   - Subsequent operations are much faster

3. **Cloud Mode**
   - Groq is optimized for speed
   - Free tier is generous for typical usage
   - Consider paid plan for heavy usage

4. **Local Mode**
   - Download models in advance: `ollama pull moondream`
   - Increase system RAM for faster inference
   - GPU acceleration available with Ollama
