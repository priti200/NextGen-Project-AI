# Open-Source & Custom Model Support

## ✅ Added Features

The MCP server now supports **any OpenAI-compatible API endpoint**, including:

### 🏠 Local Models
- **Ollama** - Easy local LLM runner (llama2, mistral, codellama, etc.)
- **LM Studio** - GUI for running local models
- **LocalAI** - Docker-based OpenAI replacement
- **Text Generation WebUI** - Popular local model interface

### ⚡ Production Servers
- **vLLM** - High-throughput inference server
- **Text Generation Inference (TGI)** - Hugging Face's production server
- **FastChat** - Scalable serving for LLMs

### 🔧 Custom Deployments
- Self-hosted fine-tuned models
- In-house model APIs
- Custom endpoints with authentication

## 📝 Configuration

Add custom models via environment variables:

```env
# Pattern: CUSTOM_MODEL_<N>_<PROPERTY>

# Example 1: Ollama (local)
CUSTOM_MODEL_1_NAME=llama2
CUSTOM_MODEL_1_BASE_URL=http://localhost:11434/v1
CUSTOM_MODEL_1_API_KEY=dummy
CUSTOM_MODEL_1_MAX_TOKENS=4096
CUSTOM_MODEL_1_SUPPORTS_TOOLS=false
CUSTOM_MODEL_1_SUPPORTS_VISION=false

# Example 2: Production API
CUSTOM_MODEL_2_NAME=my-company-gpt
CUSTOM_MODEL_2_BASE_URL=https://models.company.com/v1
CUSTOM_MODEL_2_API_KEY=secret_key_here
CUSTOM_MODEL_2_MAX_TOKENS=8192
CUSTOM_MODEL_2_SUPPORTS_TOOLS=true
CUSTOM_MODEL_2_SUPPORTS_VISION=false
```

## 🚀 Usage

Custom models are prefixed with `custom-`:

```json
{
  "model": "custom-llama2",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ]
}
```

## 📚 New Files

1. **`src/models/custom.py`** - Custom model implementations
   - `CustomModel` - Generic OpenAI-compatible wrapper
   - `OllamaModel` - Ollama-specific adapter
   - `LMStudioModel` - LM Studio adapter
   - `LocalAIModel` - LocalAI adapter

2. **`CUSTOM_MODELS.md`** - Complete configuration guide
   - Setup instructions for each platform
   - Multiple examples
   - Troubleshooting tips
   - Best practices

## 🔧 Technical Details

### Features
- ✅ Async/streaming support
- ✅ Function calling (if model supports)
- ✅ Vision inputs (if model supports)
- ✅ Custom timeouts (5 min for local models)
- ✅ Token usage tracking
- ✅ Multiple models simultaneously

### Automatic Detection
The factory automatically detects model type:
- URLs with "ollama" → OllamaModel
- Port 1234 → LMStudioModel  
- Others → CustomModel

### Model Registration
Custom models register with `custom-` prefix:
- Config: `CUSTOM_MODEL_1_NAME=llama2`
- Registered as: `custom-llama2`
- Prevents conflicts with official models

## 🧪 Testing

```bash
# Start Ollama
ollama pull llama2
ollama serve

# Configure
export CUSTOM_MODEL_1_NAME=llama2
export CUSTOM_MODEL_1_BASE_URL=http://localhost:11434/v1

# Start MCP server
cd mcp-server/src
python server.py

# Test
curl -X POST http://localhost:8080/mcp/completion \
  -H "Content-Type: application/json" \
  -d '{
    "model": "custom-llama2",
    "messages": [{"role":"user","content":"Hi!"}]
  }'
```

## 📋 Benefits

1. **Cost Savings** - Use free local models for development/testing
2. **Privacy** - Keep data on-premise with self-hosted models
3. **Flexibility** - Integrate any custom fine-tuned model
4. **Control** - Full control over model versions and updates
5. **Speed** - Low latency with local deployment
6. **Compliance** - Meet data residency requirements

## 🎯 Use Cases

- **Development**: Test with local Ollama before using paid APIs
- **Production**: Self-hosted models for data privacy
- **Research**: Custom fine-tuned models for specific domains
- **Hybrid**: Mix cloud and local models based on requirements
- **Cost Optimization**: Route simple queries to local models

## 📖 Documentation

See **CUSTOM_MODELS.md** for:
- Detailed setup for each platform
- Configuration examples
- Troubleshooting guide
- Best practices
- Supported model runners comparison

The MCP server now provides maximum flexibility for any model deployment scenario! 🎉
