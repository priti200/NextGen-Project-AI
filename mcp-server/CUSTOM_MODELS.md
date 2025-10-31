# Custom Model Integration Guide

The MCP server supports integration with any OpenAI-compatible API, allowing you to use:
- Local LLMs (Ollama, LM Studio, LocalAI)
- Self-hosted models (vLLM, Text Generation Inference)
- Custom fine-tuned models
- In-house model deployments

## Configuration

Custom models are configured via environment variables using a numbered pattern:

```env
CUSTOM_MODEL_<N>_NAME=model_name
CUSTOM_MODEL_<N>_BASE_URL=http://endpoint_url
CUSTOM_MODEL_<N>_API_KEY=api_key_if_needed
CUSTOM_MODEL_<N>_MAX_TOKENS=4096
CUSTOM_MODEL_<N>_SUPPORTS_TOOLS=true/false
CUSTOM_MODEL_<N>_SUPPORTS_VISION=true/false
```

## Examples

### 1. Ollama (Local LLMs)

Ollama provides easy access to open-source LLMs locally.

**Setup:**
```bash
# Install Ollama from https://ollama.ai
ollama pull llama2
ollama serve
```

**Configuration:**
```env
CUSTOM_MODEL_1_NAME=llama2
CUSTOM_MODEL_1_BASE_URL=http://localhost:11434/v1
CUSTOM_MODEL_1_API_KEY=dummy
CUSTOM_MODEL_1_MAX_TOKENS=4096
CUSTOM_MODEL_1_SUPPORTS_TOOLS=false
CUSTOM_MODEL_1_SUPPORTS_VISION=false
```

**Usage:**
```bash
curl -X POST http://localhost:8080/mcp/completion \
  -H "Content-Type: application/json" \
  -d '{
    "model": "custom-llama2",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 2. LM Studio

LM Studio provides a GUI for running local models with OpenAI-compatible API.

**Setup:**
1. Download LM Studio from https://lmstudio.ai
2. Load a model (e.g., Mistral 7B)
3. Start local server (default: http://localhost:1234)

**Configuration:**
```env
CUSTOM_MODEL_2_NAME=mistral-7b-instruct
CUSTOM_MODEL_2_BASE_URL=http://localhost:1234/v1
CUSTOM_MODEL_2_API_KEY=lm-studio
CUSTOM_MODEL_2_MAX_TOKENS=8192
CUSTOM_MODEL_2_SUPPORTS_TOOLS=false
CUSTOM_MODEL_2_SUPPORTS_VISION=false
```

### 3. LocalAI

LocalAI is a drop-in OpenAI replacement for running LLMs locally.

**Setup:**
```bash
docker run -p 8080:8080 -v $PWD/models:/models localai/localai:latest
```

**Configuration:**
```env
CUSTOM_MODEL_3_NAME=gpt-3.5-turbo
CUSTOM_MODEL_3_BASE_URL=http://localhost:8080/v1
CUSTOM_MODEL_3_API_KEY=dummy
CUSTOM_MODEL_3_MAX_TOKENS=4096
CUSTOM_MODEL_3_SUPPORTS_TOOLS=true
CUSTOM_MODEL_3_SUPPORTS_VISION=false
```

### 4. vLLM (Production Inference)

vLLM is a high-throughput inference server for production use.

**Setup:**
```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-chat-hf \
  --port 8000
```

**Configuration:**
```env
CUSTOM_MODEL_4_NAME=llama-2-7b-chat
CUSTOM_MODEL_4_BASE_URL=http://localhost:8000/v1
CUSTOM_MODEL_4_API_KEY=dummy
CUSTOM_MODEL_4_MAX_TOKENS=4096
CUSTOM_MODEL_4_SUPPORTS_TOOLS=false
CUSTOM_MODEL_4_SUPPORTS_VISION=false
```

### 5. Self-Hosted Fine-Tuned Model

Host your own fine-tuned model with any OpenAI-compatible server.

**Configuration:**
```env
CUSTOM_MODEL_5_NAME=my-company-model
CUSTOM_MODEL_5_BASE_URL=https://models.mycompany.com/v1
CUSTOM_MODEL_5_API_KEY=your_secret_api_key_here
CUSTOM_MODEL_5_MAX_TOKENS=8192
CUSTOM_MODEL_5_SUPPORTS_TOOLS=true
CUSTOM_MODEL_5_SUPPORTS_VISION=true
```

### 6. Hugging Face Text Generation Inference

**Setup:**
```bash
docker run -p 8080:80 -v $PWD/data:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id mistralai/Mistral-7B-Instruct-v0.2
```

**Configuration:**
```env
CUSTOM_MODEL_6_NAME=mistral-7b
CUSTOM_MODEL_6_BASE_URL=http://localhost:8080/v1
CUSTOM_MODEL_6_API_KEY=dummy
CUSTOM_MODEL_6_MAX_TOKENS=4096
```

## Multiple Custom Models

You can configure multiple custom models simultaneously:

```env
# Model 1: Ollama Llama2
CUSTOM_MODEL_1_NAME=llama2
CUSTOM_MODEL_1_BASE_URL=http://localhost:11434/v1

# Model 2: LM Studio Mistral
CUSTOM_MODEL_2_NAME=mistral-7b
CUSTOM_MODEL_2_BASE_URL=http://localhost:1234/v1

# Model 3: Production vLLM
CUSTOM_MODEL_3_NAME=production-gpt
CUSTOM_MODEL_3_BASE_URL=https://prod-server:8000/v1
CUSTOM_MODEL_3_API_KEY=prod_key_123
```

All models will be available with the `custom-` prefix:
- `custom-llama2`
- `custom-mistral-7b`
- `custom-production-gpt`

## Capabilities

### Function/Tool Calling

Set `SUPPORTS_TOOLS=true` if your model supports function calling:

```env
CUSTOM_MODEL_1_SUPPORTS_TOOLS=true
```

Then you can use it with tools:
```json
{
  "model": "custom-your-model",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get weather info",
        "parameters": {...}
      }
    }
  ]
}
```

### Vision/Image Support

Set `SUPPORTS_VISION=true` if your model can process images:

```env
CUSTOM_MODEL_1_SUPPORTS_VISION=true
```

## Troubleshooting

### Connection Refused
- Ensure the model server is running
- Check the base URL is correct
- Verify firewall/network settings

### Timeout Errors
- Custom models use 5-minute timeout for generation
- Increase timeout if needed for large responses

### Authentication Errors
- Use `dummy` or `none` for API key if not required
- Verify API key is correct for secured endpoints

### Model Not Found
- Check the model name matches what the server expects
- Some servers auto-detect model names

## Testing

Test your custom model:

```bash
# Initialize session
SESSION=$(curl -s -X POST http://localhost:8080/mcp/initialize \
  -H "Content-Type: application/json" \
  -d '{"protocol_version":"1.0","client_info":{"name":"test"}}' \
  | jq -r '.session_id')

# Test completion
curl -X POST http://localhost:8080/mcp/completion \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION\",
    \"model\": \"custom-llama2\",
    \"messages\": [{\"role\":\"user\",\"content\":\"Say hello!\"}]
  }"
```

## Best Practices

1. **Use descriptive model names**: `custom-finance-model` instead of `custom-model1`
2. **Set accurate token limits**: Prevents truncation issues
3. **Enable capabilities correctly**: Only set tools/vision to true if supported
4. **Use local models for development**: Ollama/LM Studio are great for testing
5. **Secure production endpoints**: Use HTTPS and strong API keys
6. **Monitor performance**: Custom models may be slower than cloud APIs

## Supported Local Model Runners

| Tool | Base URL | Auth | Notes |
|------|----------|------|-------|
| Ollama | http://localhost:11434/v1 | None | Easy setup, Mac/Linux/Windows |
| LM Studio | http://localhost:1234/v1 | None | GUI, cross-platform |
| LocalAI | http://localhost:8080/v1 | None | Docker, multi-model |
| vLLM | http://localhost:8000/v1 | Optional | High performance |
| Text Gen UI | http://localhost:5000/v1 | None | Web UI, many models |
| FastChat | http://localhost:8000/v1 | Optional | OpenAI compatible |

All these tools provide OpenAI-compatible APIs that work with this MCP server!
