# LLM Chat Interface

A simple web interface for interacting with local LLM models via Ollama and FastAPI.

## Features

- Clean, minimalist web interface
- Conversation memory between interactions
- Integration with Ollama for local LLM inference
- FastAPI backend for performance and ease of use

## Requirements

- Python 3.8+
- Ollama installed with the llama3.2 model
- Required Python packages: fastapi, uvicorn, langchain, ollama, pydantic

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/valeriawin/ai-gent.git
   cd ai-gent
   ```

2. Create virtual environment and install the required packages:
   ```
   python -m venv ai-agent-env
   source ai-agent-env/bin/activate
   pip install fastapi uvicorn langchain langchain_community ollama pydantic
   ```

3. Make sure Ollama is running with the llama3.2 model installed:
   ```
   ollama pull llama3.2
   ```

## Usage

1. Start the application:
   ```
   python main.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

3. Type your question in the input field and click "Send"

## Project Structure

- `main.py` - FastAPI application and routes
- `llm_service.py` - LLM integration and conversation management
- `html_content.py` - HTML template generation

## Customization

To use a different model, modify the model name in `llm_service.py`:

```python
def __init__(self, model_name="llama3.2"):  # Change "llama3.2" to your preferred model
```

## License

MIT
