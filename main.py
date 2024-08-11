import os
from fastapi import FastAPI
from github import Github
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


def generate_response(repo_url: str, pr_number: int):
    # Initialize GitHub API with token
    g = Github(os.getenv("GITHUB_TOKEN"))

    # Get the repo object
    repo = g.get_repo(repo_url)

    # Fetch README content (assuming README.md)
    readme_content = repo.get_contents("README.md")

    # Fetch pull request by number
    pull_request = repo.get_pull(pr_number)

    # Get the diffs of the pull request
    pull_request_diffs = [
        {"filename": file.filename, "patch": file.patch}
        for file in pull_request.get_files()
    ]

    # Get the commit messages associated with the pull request
    commit_messages = [commit.commit.message for commit in pull_request.get_commits()]

    # Format data for OpenAI prompt
    prompt = format_data_for_openai(pull_request_diffs, readme_content, commit_messages)

    # Call OpenAI to generate the updated README content
    updated_readme = call_openai(prompt, retriever)

    # Create PR for Updated PR
    # update_readme_and_create_pr(repo, updated_readme, readme_content.sha)
    print(updated_readme)
    return updated_readme


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
