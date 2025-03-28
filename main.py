import os

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from html_content import get_html_content
from llm_service import LLMService

app = FastAPI(title="LLM Chat Interface with Tools")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create static directory for uploaded files if it doesn't exist
os.makedirs("documents", exist_ok=True)

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


@app.post("/upload", response_class=HTMLResponse)
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join("documents", file.filename)
    content = await file.read()
    result = llm_service.upload_document(file_path, content)
    return get_html_content(f"Uploaded {file.filename}", result)


@app.post("/reset", response_class=HTMLResponse)
async def reset_conversation():
    llm_service.reset_memory()
    return get_html_content("Memory reset", "Conversation history has been cleared.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
