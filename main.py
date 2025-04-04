from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from html_content import get_html_content
from llm_service import LLMService

app = FastAPI(title="LLM Chat Interface")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_service = LLMService()

class PromptRequest(BaseModel):
    prompt: str

@app.get("/", response_class=HTMLResponse)
async def get_html():
    return get_html_content()

@app.post("/ask", response_class=HTMLResponse)
async def process_prompt(prompt_request: PromptRequest):
    user_input = prompt_request.prompt
    response = llm_service.get_response(user_input)

    return get_html_content(user_input, response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
