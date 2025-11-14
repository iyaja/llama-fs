# FileFlow API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### GET /
Health check endpoint.

**Response:** `200 OK`
```json
{
  "status": "ok"
}
```

---

### POST /batch

Process a directory and get file organization suggestions.

**Request:**
```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/directory",
    "instruction": "organize files by type and date",
    "incognito": false
  }'
```

**Parameters:**
- `path` (string, required) - Directory path to process
- `instruction` (string, optional) - Special instructions for organization
- `incognito` (boolean, optional, default: false) - Use local Ollama (true) or cloud Groq (false)

**Response:** `200 OK`
```json
{
  "files": [
    {
      "src_path": "Documents/report.pdf",
      "dst_path": "2024/Reports/report.pdf",
      "summary": "Q4 2024 financial report analyzing quarterly performance"
    },
    {
      "src_path": "Documents/image.jpg",
      "dst_path": "Photos/2024/image.jpg",
      "summary": "Photo taken on January 5, 2024"
    }
  ]
}
```

**Response Fields:**
- `files` - Array of file organization suggestions
  - `src_path` - Current file location
  - `dst_path` - Suggested new location
  - `summary` - AI-generated description of file content

**Error Responses:**

`400 Bad Request`
```json
{
  "error": "Directory not found or invalid path"
}
```

`422 Unprocessable Entity`
```json
{
  "error": "Path is required"
}
```

---

### POST /watch

Start watching a directory for changes (streaming response).

**Request:**
```bash
curl -X POST http://localhost:8000/watch \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/directory",
    "incognito": false
  }'
```

**Parameters:**
- `path` (string, required) - Directory to monitor
- `incognito` (boolean, optional, default: false) - Use local Ollama or cloud Groq

**Response:** `200 OK` (Streaming)

The response is a stream of newline-delimited JSON objects:

```
{"event": "initialized", "files": [...]}
{"event": "file_created", "path": "newfile.txt", "summary": "..."}
{"event": "file_modified", "path": "existing.txt", "summary": "..."}
{"event": "reorganization_suggested", "files": [...]}
```

**Event Types:**

1. **initialized**
   - First event after watch mode starts
   - Contains initial file list and summaries

2. **file_created**
   - File was added to directory
   - Includes summary of new file

3. **file_modified**
   - File was changed
   - Includes updated summary

4. **file_moved**
   - File was moved/renamed
   - FileFlow learns this pattern

5. **reorganization_suggested**
   - FileFlow suggests changes based on patterns
   - Contains full file reorganization proposal

**Streaming Response Example:**
```json
{
  "event": "initialized",
  "files": [
    {"src_path": "file1.pdf", "dst_path": "Documents/file1.pdf", "summary": "..."}
  ]
}
```

---

### POST /commit

Apply file reorganization changes (move files on disk).

**Request:**
```bash
curl -X POST http://localhost:8000/commit \
  -H "Content-Type: application/json" \
  -d '{
    "src_path": "Documents/report.pdf",
    "dst_path": "2024/Reports/report.pdf"
  }'
```

**Parameters:**
- `src_path` (string, required) - Current file location
- `dst_path` (string, required) - New file location

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "File moved successfully"
}
```

**Error Responses:**

`400 Bad Request`
```json
{
  "error": "Source file not found"
}
```

`409 Conflict`
```json
{
  "error": "Destination file already exists"
}
```

---

## Usage Examples

### Example 1: Batch Processing

```bash
# Process Downloads folder
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/Users/username/Downloads",
    "instruction": "organize by file type and date"
  }' | jq .

# Response:
# {
#   "files": [
#     {
#       "src_path": "report.pdf",
#       "dst_path": "Documents/2024/report.pdf",
#       "summary": "Annual financial report for 2024"
#     },
#     ...
#   ]
# }

# Apply first suggestion:
curl -X POST http://localhost:8000/commit \
  -H "Content-Type: application/json" \
  -d '{
    "src_path": "report.pdf",
    "dst_path": "Documents/2024/report.pdf"
  }'
```

### Example 2: Watch Mode with Streaming

```bash
# Start watching directory
curl -X POST http://localhost:8000/watch \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/Users/username/Documents"
  }' \
  | jq .

# Keep connection open to receive events
# Ctrl+C to stop watching
```

### Example 3: Local/Incognito Mode

```bash
# Process sensitive files locally
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/Users/username/PrivateFiles",
    "incognito": true
  }' | jq .

# Note: Requires Ollama installed and running
```

---

## Error Handling

All error responses follow this format:

```json
{
  "error": "Error description",
  "details": "Additional context (optional)"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - File or directory not found
- `409 Conflict` - File already exists at destination
- `422 Unprocessable Entity` - Invalid JSON or missing required fields
- `500 Internal Server Error` - Server error

---

## Rate Limiting

Current implementation has no explicit rate limiting.

**Recommendations:**
- Groq API: Free tier has usage limits (check [console.groq.com](https://console.groq.com))
- Ollama: Local only, no external rate limits

---

## Performance Notes

### Batch Mode Timing
- **Small directory** (< 10 files): 1-3 seconds
- **Medium directory** (10-50 files): 5-15 seconds
- **Large directory** (50+ files): 20+ seconds

### Watch Mode Timing
- **Initial scan**: Same as batch mode
- **File change detection**: < 500ms
- **Reorganization suggestion**: 2-5 seconds after file move

### Factors Affecting Performance

1. **File Size** - Larger files take longer to summarize
2. **File Type** - Images slower than text
3. **Network** - Groq API latency
4. **System Resources** - CPU/RAM for local processing
5. **Queue** - Multiple simultaneous requests

---

## Authentication

No authentication currently required. FileFlow is designed for local use.

**Security Notes:**
- API only listens on localhost by default
- Suitable for single-user desktop application
- Not recommended for multi-user or remote access without auth

---

## CORS

Frontend (Electron) is configured to make requests to `localhost:8000`.

CORS headers are configured to allow requests from `http://localhost:3000` and `http://localhost:8000`.

---

## Future Enhancements

Planned API improvements:
- Batch commit (multiple files at once)
- Undo/rollback operations
- Custom organization rules
- Webhook support for external integrations
- WebSocket for bidirectional communication in watch mode
