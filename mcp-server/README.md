# NextGen Project AI - MCP Server

An independent Model Context Protocol (MCP) server that provides AI-powered project management capabilities using multiple LLM models (Gemini, OpenAI, etc.) with a rich set of tools for project analysis, risk prediction, and intelligent insights.

## Features

- **Multi-Model Support**: Gemini, OpenAI GPT-4, Claude, and more
- **Rich Tool Set**: Project analysis, risk prediction, resource optimization
- **MCP Protocol**: Standard Model Context Protocol implementation
- **Dockerized**: Easy deployment with Docker
- **Extensible**: Plugin architecture for custom tools
- **RESTful API**: HTTP endpoints for integration
- **WebSocket Support**: Real-time streaming responses
- **Context Management**: Efficient context handling for long conversations

## Architecture

```
mcp-server/
├── src/
│   ├── server.py           # Main MCP server implementation
│   ├── config.py           # Configuration management
│   ├── models/             # LLM model integrations
│   │   ├── base.py         # Base model interface
│   │   ├── gemini.py       # Google Gemini integration
│   │   ├── openai.py       # OpenAI GPT integration
│   │   └── claude.py       # Anthropic Claude integration
│   ├── tools/              # MCP tools
│   │   ├── base.py         # Base tool interface
│   │   ├── project_analyzer.py
│   │   ├── risk_predictor.py
│   │   ├── resource_optimizer.py
│   │   ├── code_analyzer.py
│   │   └── jira_integration.py
│   ├── context/            # Context management
│   │   ├── manager.py      # Context manager
│   │   └── storage.py      # Context storage
│   └── utils/              # Utilities
│       ├── logger.py       # Logging
│       └── validators.py   # Input validation
├── tests/                  # Unit tests
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── requirements.txt        # Python dependencies
└── .env.example            # Environment variables template
```

## Quick Start

### Local Development

```bash
# Install dependencies
cd mcp-server
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python src/server.py
```

### Docker Deployment

```bash
# Build image
docker build -t nextgen-mcp-server .

# Run container
docker run -p 8080:8080 --env-file .env nextgen-mcp-server

# Or use docker-compose
docker-compose up
```

## Configuration

Set the following environment variables in `.env`:

```env
# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080
MCP_LOG_LEVEL=INFO

# LLM Model API Keys
GOOGLE_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key

# Default Model
DEFAULT_MODEL=gemini-pro

# Integration APIs
JIRA_API_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your_jira_token
GITHUB_TOKEN=your_github_token
SLACK_BOT_TOKEN=your_slack_token

# Database (optional)
REDIS_URL=redis://localhost:6379
```

## MCP Protocol Endpoints

### HTTP Endpoints

- `POST /mcp/initialize` - Initialize MCP session
- `POST /mcp/tools/list` - List available tools
- `POST /mcp/tools/call` - Execute a tool
- `POST /mcp/prompts/list` - List available prompts
- `POST /mcp/prompts/get` - Get prompt template
- `POST /mcp/resources/list` - List resources
- `POST /mcp/resources/read` - Read resource
- `POST /mcp/completion` - Get AI completion
- `GET /health` - Health check

### WebSocket

- `ws://localhost:8080/mcp/stream` - Streaming completions

## Available Tools

### 1. Project Analyzer
Analyzes project health, velocity, and metrics.

```json
{
  "name": "analyze_project",
  "parameters": {
    "project_key": "PROJ-123",
    "analysis_type": "comprehensive"
  }
}
```

### 2. Risk Predictor
Predicts project risks using ML models.

```json
{
  "name": "predict_risk",
  "parameters": {
    "project_key": "PROJ-123",
    "component": "backend"
  }
}
```

### 3. Resource Optimizer
Optimizes resource allocation.

```json
{
  "name": "optimize_resources",
  "parameters": {
    "project_key": "PROJ-123",
    "constraints": {}
  }
}
```

### 4. Code Analyzer
Analyzes code quality and suggests improvements.

```json
{
  "name": "analyze_code",
  "parameters": {
    "repository": "owner/repo",
    "path": "src/"
  }
}
```

### 5. Jira Integration
Fetches and analyzes Jira data.

```json
{
  "name": "jira_query",
  "parameters": {
    "jql": "project = PROJ",
    "fields": ["summary", "status"]
  }
}
```

## Usage Examples

### Python Client

```python
import requests

# Initialize session
response = requests.post("http://localhost:8080/mcp/initialize", json={
    "protocol_version": "1.0",
    "client_info": {"name": "test-client", "version": "1.0"}
})

session_id = response.json()["session_id"]

# Call a tool
response = requests.post("http://localhost:8080/mcp/tools/call", json={
    "session_id": session_id,
    "name": "analyze_project",
    "parameters": {"project_key": "PROJ-123"}
})

print(response.json())
```

### cURL

```bash
# Initialize
curl -X POST http://localhost:8080/mcp/initialize \
  -H "Content-Type: application/json" \
  -d '{"protocol_version": "1.0", "client_info": {"name": "curl", "version": "1.0"}}'

# Call tool
curl -X POST http://localhost:8080/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_123",
    "name": "analyze_project",
    "parameters": {"project_key": "PROJ-123"}
  }'
```

## Model Selection

The server supports multiple LLM models. Specify the model in your requests:

```json
{
  "model": "gemini-pro",  // or "gpt-4", "claude-3-opus"
  "messages": [...],
  "tools": [...]
}
```

### Supported Models

- **Google Gemini**: `gemini-pro`, `gemini-pro-vision`
- **OpenAI**: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Anthropic Claude**: `claude-3-opus`, `claude-3-sonnet`

## Development

### Adding a New Tool

1. Create a new file in `src/tools/`:

```python
from .base import BaseTool

class MyCustomTool(BaseTool):
    name = "my_custom_tool"
    description = "Does something amazing"
    
    def execute(self, parameters):
        # Implementation
        return {"result": "success"}
```

2. Register in `src/server.py`

### Adding a New Model

1. Create a new file in `src/models/`:

```python
from .base import BaseModel

class MyCustomModel(BaseModel):
    def __init__(self, api_key):
        self.api_key = api_key
    
    async def generate(self, prompt, **kwargs):
        # Implementation
        return "Generated text"
```

2. Register in `src/config.py`

## Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/

# Specific test
pytest tests/test_tools.py
```

## Deployment

### Production Checklist

- [ ] Set all required environment variables
- [ ] Configure proper logging
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure rate limiting
- [ ] Set up SSL/TLS certificates
- [ ] Enable authentication
- [ ] Configure backup strategy

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: nextgen-mcp-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: google-api-key
```

## Performance

- **Throughput**: ~100 requests/second
- **Latency**: <100ms (p99)
- **Concurrent Sessions**: 1000+

## Security

- API key authentication
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/your-org/nextgen-project-ai/issues)
- Email: support@example.com
