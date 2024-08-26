# README.md

This repository contains a backend service built with FastAPI. The service is designed to interact with GitHub repositories and pull requests.

## Features

- Fetch README content from a GitHub repository
- Fetch pull request details by number
- Get the diffs of the pull request
- Get the commit messages associated with the pull request
- Format data for OpenAI prompt
- Call OpenAI to generate the updated README content
- Create a pull request for the updated README

## New Changes

- Added a new file `backend/generate.py` which contains functions to fetch file content from a repository, get relevant files from a pull request, and generate a response based on the pull request details.
- Added a new file `backend/main.py` which sets up a FastAPI application and defines endpoints for generating responses based on pull request details, searching repositories, and listing pull requests.
- Updated `.gitignore` to ignore `.venv`, `__pycache__`, and `node_modules`.
- Added a new file `backend/requirements.txt` which lists all the Python dependencies required for the backend service.
- Updated `backend/utility.py` to include a function for formatting data for the OpenAI prompt and a function to call the OpenAI API.

## Setup

To set up the backend service, you need to install the Python dependencies listed in `backend/requirements.txt`. You can do this by running the following command:

```bash
cd backend
pip install -r backend/requirements.txt
```
To set up the frontend service, you need to install dependencies listed in `package.json`. You can do this by running the following command:

```bash
cd fronend
pnpm install
```

You also need to set up environment variables for the GitHub token (`GITHUB_TOKEN`) and the OpenAI API key (`OPENAI_API_KEY`).

## Usage

To start the application, navigate to the `root` directory and run the following commands:

```bash
pnpm install
pnpm run dev
```

## Contributing

If you want to contribute to this project, please create a new branch and submit a pull request with your changes. Your pull request will be reviewed and merged if it is approved.
