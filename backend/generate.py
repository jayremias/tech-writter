import os
import base64
from typing import Dict, List
from github import Github
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from .utility import format_data_for_openai, call_openai, update_readme_and_create_pr
from dotenv import load_dotenv


load_dotenv()


def get_file_content(repo, file_path):
    try:
        content = repo.get_contents(file_path)
        if isinstance(content, list):
            return "Directory: " + ", ".join([f.path for f in content])
        return base64.b64decode(content.content).decode("utf-8")
    except Exception as e:
        return f"Error fetching file content: {str(e)}"


def create_vector_db(repo):
    # Fetch all files from the repository
    contents = repo.get_contents("")
    files = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            files.append(file_content)

    # Create a temporary directory to store the files
    temp_dir = "../temp_repo_files"
    os.makedirs(temp_dir, exist_ok=True)

    # Save the content of each file
    documents = []
    for file in files:
        file_path = os.path.join(temp_dir, file.path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        content = get_file_content(repo, file.path)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        if not content.startswith("Error fetching file content:"):
            loader = TextLoader(file_path)
            documents.extend(loader.load())

    # Split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    # Create the vector store
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(texts, embeddings)

    # Clean up temporary files
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(temp_dir)

    return db


def generate_response(repo_url: str, pr_number: int):
    # Initialize GitHub API with token
    g = Github(os.getenv("GITHUB_TOKEN"))

    # Get the repo object
    repo = g.get_repo(repo_url)

    # Create vector database for the repository
    vector_db = create_vector_db(repo)

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

    # Set up RAG
    retriever = vector_db.as_retriever()

    # Call OpenAI to generate the updated README content
    updated_readme = call_openai(prompt, retriever)

    # Create PR for Updated PR
    # update_readme_and_create_pr(repo, updated_readme, readme_content.sha)
    print(updated_readme)
    return updated_readme
