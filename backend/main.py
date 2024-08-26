import os
import httpx

from dotenv import load_dotenv

load_dotenv(".env.dev")

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


@app.get("/search-repos")
async def search_repos(q: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/search/repositories?q={q}",
            headers={"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"},
        )
        response.raise_for_status()
        data = response.json()
        return [repo["full_name"] for repo in data["items"][:5]]


@app.get("/list-prs")
async def list_prs(repo: str):
    owner, name = repo.split("/")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{name}/pulls",
            headers={"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"},
        )
        response.raise_for_status()
        data = response.json()
        return [str(pr["number"]) for pr in data[:5]]
