import os
from unittest import TestLoader
from webbrowser import Chrome
from github import Github
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from utility import *
from dotenv import load_dotenv

load_dotenv()


def create_vector_db(repo):
    # Fetch all .py files from the repository
    contents = repo.get_contents("")
    py_files = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        elif file_content.name.endswith(".py"):
            py_files.append(file_content)

    # Create a temporary directory to store the files
    temp_dir = "temp_repo_files"
    os.makedirs(temp_dir, exist_ok=True)

    # Save the content of each file
    for file in py_files:
        with open(os.path.join(temp_dir, file.name), "w") as f:
            f.write(file.decoded_content.decode())

    # Load the documents
    loader = TestLoader(os.path.join(temp_dir, py_files[0].name))
    documents = loader.load()

    # Split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    # Create the vector store
    embeddings = OpenAIEmbeddings()
    db = Chrome.from_documents(texts, embeddings)

    # Clean up temporary files
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)

    return db


def main():
    # Initialize GitHub API with token
    g = Github(os.getenv("GITHUB_TOKEN"))

    # Get the repo path and PR number from the environment variables
    repo_path = os.getenv("REPO_PATH")
    pull_request_number = int(os.getenv("PR_NUMBER"))

    # Get the repo object
    repo = g.get_repo(repo_path)

    # Create vector database for the repository
    vector_db = create_vector_db(repo)

    # Fetch README content (assuming README.md)
    readme_content = repo.get_contents("README.md")

    # Fetch pull request by number
    pull_request = repo.get_pull(pull_request_number)

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
    update_readme_and_create_pr(repo, updated_readme, readme_content.sha)


if __name__ == "__main__":
    main()
