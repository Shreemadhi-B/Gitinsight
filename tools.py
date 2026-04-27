# Plain Python tool functions the agent calls directly.

import os
from langchain_core.tools import tool
from loader import get_file_history as _get_file_history, fetch_commit as _fetch_commit, CLONE_BASE_DIR
from retriever import search_commits as _search_commits, format_search_results
from git import Repo


def _get_repo() -> Repo:
    """Gets the first available cloned repo."""
    if os.path.exists(CLONE_BASE_DIR):
        for name in os.listdir(CLONE_BASE_DIR):
            path = os.path.join(CLONE_BASE_DIR, name)
            if os.path.isdir(path):
                try:
                    return Repo(path)
                except Exception:
                    continue
    raise ValueError("No cloned repo found. Please analyze a repo first.")


@tool
def search_commits(query: str) -> str:
    """
    Search git commits by meaning or keywords.
    Use this to find commits related to a topic, feature, or bug.
    query: what to search for e.g. 'authentication bug' or 'database migration'
    """
    results = _search_commits(query=query, n_results=5)
    return format_search_results(results)


@tool
def fetch_commit(commit_hash: str) -> str:
    """
    Get full details of a specific commit by its hash.
    Use this when you need to inspect exactly what changed in a commit.
    commit_hash: the commit hash e.g. '2ac89889'
    """
    repo = _get_repo()
    result = _fetch_commit(repo=repo, commit_hash=commit_hash)
    if not result:
        return f"Commit {commit_hash} not found."

    lines = [
        f"Hash:    {result['hash']}",
        f"Author:  {result['author']} <{result['email']}>",
        f"Date:    {result['date']}",
        f"Message: {result['message']}",
        f"Files changed ({result['files_count']}):",
    ]
    for f in result.get("files_changed", []):
        lines.append(f"  - {f}")
    return "\n".join(lines)


@tool
def get_file_history(file_path: str) -> str:
    """
    Get the complete commit history for a specific file.
    Use this to see how a file has evolved over time.
    file_path: relative path e.g. 'src/flask/app.py'
    """
    repo = _get_repo()
    history = _get_file_history(repo=repo, file_path=file_path)
    if not history:
        return f"No commits found for file: {file_path}"

    lines = [f"Commit history for {file_path}:"]
    for c in history:
        lines.append(
            f"  [{c['hash']}] {c['date']} — {c['author']}: {c['message'][:80]}"
        )
    return "\n".join(lines)


ALL_TOOLS = [search_commits, fetch_commit, get_file_history]