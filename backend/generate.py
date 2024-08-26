import os

from github import Github
from .utility import call_openai, format_data_for_openai
from typing import List, Dict
import base64

from .utility import call_openai, format_data_for_openai


def get_file_content(repo, file_path: str) -> str:
    try:
        content = repo.get_contents(file_path)
        if isinstance(content, list):
            return "Directory: " + ", ".join([f.path for f in content])
        return base64.b64decode(content.content).decode("utf-8")
    except Exception as e:
        return f"Error fetching file content: {str(e)}"


def get_relevant_files(
    repo, pull_request_files: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    relevant_files = []
    for file in pull_request_files:
        content = get_file_content(repo, file["filename"])
        relevant_files.append({"filename": file["filename"], "content": content})
    return relevant_files


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
    relevant_files = get_relevant_files(repo, pull_request_diffs)

    # Get the commit messages associated with the pull request
    commit_messages = [commit.commit.message for commit in pull_request.get_commits()]

    # Format data for OpenAI prompt
    prompt = format_data_for_openai(
        pull_request_diffs, readme_content, commit_messages, relevant_files
    )

    # Call OpenAI to generate the updated README content
    updated_readme = call_openai(prompt)

    # Create PR for Updated PR
    # update_readme_and_create_pr(repo, updated_readme, readme_content.sha)
    print(updated_readme)
    return updated_readme
