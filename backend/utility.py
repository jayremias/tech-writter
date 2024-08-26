import os
import base64

from langchain_text_splitters import TokenTextSplitter

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


def format_data_for_openai(diffs, readme_content, commit_messages):
    prompt = (
        "You are an AI trained to update README files based on code changes. "
        "Please review the following information from a GitHub pull request:\n\n"
        "1. Code changes:\n"
        "{changes}\n\n"
        "2. Commit messages:\n"
        "{commit_messages}\n\n"
        "3. Current README file content:\n"
        "{readme_content}\n\n"
        "Based on the code changes, commit messages, and the current README, "
        "determine if the README needs to be updated. If so, provide an updated "
        "version of the README that:\n"
        "- Maintains its existing style and clarity\n"
        "- Reflects new features, changes in functionality, or important updates\n"
        "- Updates any outdated information\n"
        "- Adds or modifies sections as necessary to accurately represent the current state of the project\n\n"
        "If no update is needed, return the original README content.\n\n"
        "Updated README:\n"
    )

    changes = "\n".join(
        [f"File: {file['filename']}\nDiff: \n{file['patch']}\n" for file in diffs]
    )
    commit_messages = "\n".join(commit_messages)

    return prompt.format(
        changes=changes, commit_messages=commit_messages, readme_content=readme_content
    )


def truncate_text(text, max_tokens):
    splitter = TokenTextSplitter(chunk_size=max_tokens, chunk_overlap=0)
    chunks = splitter.split_text(text)
    return chunks[0] if chunks else ""


def call_openai(prompt, retriever):
    try:
        # client = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.1,
            max_tokens=2000,
        )

        # Create a custom prompt template for our task
        custom_prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are an AI trained to update README files based on code changes and repository context. "
                "Use the following pieces of context to help you understand the repository better:\n"
                "{context}\n\n"
                "Now, please address the following task:\n"
                "{question}\n"
                "If you need to refer to specific parts of the codebase or documentation that aren't "
                "directly mentioned in the context or question, you can ask for more information."
            ),
        )

        # Set up the RetrievalQA chain with reduced token limits
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": custom_prompt_template},
            return_source_documents=True,
        )

        # Truncate the prompt if it's too long
        max_prompt_tokens = 3000  # Adjust this value as needed
        truncated_prompt = truncate_text(prompt, max_prompt_tokens)

        # Run the chain
        result = qa_chain({"query": truncated_prompt})

        return result["result"]

    except Exception as e:
        print(f"Error making OpenAI API call: {e}")


def update_readme_and_create_pr(repo, updated_readme, readme_sha):
    """
    Submit Updated README content as a PR in a new branch
    """

    commit_message = "Proposed README update based on recent code changes"
    main_branch = repo.get_branch("main")
    new_branch_name = f"update-readme-{readme_sha[:10]}"
    new_branch = repo.create_git_ref(
        ref=f"refs/heads/{new_branch_name}", sha=main_branch.commit.sha
    )

    # Update the README file
    repo.update_file(
        path="README.md",
        message=commit_message,
        content=updated_readme,
        sha=readme_sha,
        branch=new_branch_name,
    )

    # Create a PR
    pr_title = "Update README based on recent changes"
    br_body = "This PR proposes an update to the README based on recent code changes. Please review and merge if appropriate."
    pull_request = repo.create_pull(
        title=pr_title, body=br_body, head=new_branch_name, base="main"
    )

    return pull_request
