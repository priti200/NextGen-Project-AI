# MCP Server - Quick Start Guide

## Prerequisites

Before running the MCP server, ensure you have:
- Python 3.10 or higher
- At least one LLM API key (Gemini, OpenAI, or Claude)

## Installation

1. **Navigate to mcp-server directory:**
   ```bash
   cd mcp-server
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env and add your API keys
   # At minimum, set one of:
   # - GOOGLE_API_KEY (for Gemini)
   # - OPENAI_API_KEY (for GPT models)
   # - ANTHROPIC_API_KEY (for Claude)
   ```

## Running the Server

### Development Mode
```bash
cd src
python server.py
```

The server will start on `http://localhost:8080`

### Production Mode
```bash
cd src
uvicorn server:app --host 0.0.0.0 --port 8080 --workers 4
```

## Testing

### Check Health
```bash
curl http://localhost:8080/health
```

### Initialize a Session
```bash
curl -X POST http://localhost:8080/mcp/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_version": "1.0",
    "client_info": {"name": "test", "version": "1.0"}
  }'
```

### List Available Models
The health endpoint shows which models are available based on your API keys.

### Generate a Completion
```bash
curl -X POST http://localhost:8080/mcp/completion \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-pro",
    "messages": [
      {"role": "user", "content": "Hello! How are you?"}
    ]
  }'
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Supported Models

Depending on your API keys, the following models will be available:

### Google Gemini
- `gemini-pro` - Text generation
- `gemini-pro-vision` - Text + vision

### OpenAI
- `gpt-4` - Most capable
- `gpt-4-turbo` - Fast and capable
- `gpt-3.5-turbo` - Fast and efficient

### Anthropic Claude
- `claude-3-opus` - Most capable
- `claude-3-sonnet` - Balanced
- `claude-3-haiku` - Fast

## Next Steps

Check the main README.md for:
- Tool usage
- WebSocket streaming
- Backend integration
- Docker deployment
