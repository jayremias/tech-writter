import os
from dotenv import load_dotenv

load_dotenv(".env.dev")
print(os.getenv("OPENAI_API_KEY"))


from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from fastapi import FastAPI

from .generate import generate_response

app = FastAPI()


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite's default port
    ],
    allow_credentials=True,
    allow_methods=["*"],  # This allows all methods, including OPTIONS
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    repo_url: str
    pr_number: int


@app.post("/generate")
async def generate(request: GenerateRequest):
    response = generate_response(request.repo_url, request.pr_number)
    return {"response": response}
