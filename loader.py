# Handles cloning a GitHub repo and extracting commit history using GitPython.

import os
from datetime import datetime
from git import Repo
from git.exc import GitCommandError

CLONE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloned_repos")


def clone_repo(repo_url: str) -> tuple[Repo, str]:
    """Clones a GitHub repo locally if not already cloned."""
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    local_path = os.path.join(CLONE_BASE_DIR, repo_name)
    os.makedirs(CLONE_BASE_DIR, exist_ok=True)

    if os.path.exists(local_path):
        print(f"Repo already cloned at: {local_path}")
        return Repo(local_path), local_path

    print(f"Cloning repo from: {repo_url}")
    try:
        repo = Repo.clone_from(repo_url, local_path)
        print("Clone complete.")
        return repo, local_path
    except GitCommandError as e:
        print(f"Git error while cloning: {e}")
        raise


def extract_commits(repo: Repo, max_commits: int = 100) -> list[dict]:
    """Extracts commit metadata from the repo history."""
    print(f"Extracting commits (max: {max_commits})...")
    commits_data = []

    for i, commit in enumerate(list(repo.iter_commits())[:max_commits]):
        commits_data.append({
            "hash": commit.hexsha[:8],
            "full_hash": commit.hexsha,
            "author": commit.author.name,
            "email": commit.author.email,
            "date": datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d"),
            "message": commit.message.strip(),
            "files_changed": list(commit.stats.files.keys()),
            "files_count": len(commit.stats.files),
        })

        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{max_commits} commits...")

    print(f"Extracted {len(commits_data)} commits.")
    return commits_data


def get_file_history(repo: Repo, file_path: str) -> list[dict]:
    """Returns all commits that touched a specific file."""
    print(f"Getting history for: {file_path}")
    commits = list(repo.iter_commits(paths=file_path))

    if not commits:
        print(f"No commits found for: {file_path}")
        return []

    history = []
    for commit in commits:
        history.append({
            "hash": commit.hexsha[:8],
            "full_hash": commit.hexsha,
            "author": commit.author.name,
            "date": datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d"),
            "message": commit.message.strip(),
        })

    print(f"Found {len(history)} commits for {file_path}")
    return history


def fetch_commit(repo: Repo, commit_hash: str) -> dict:
    """Returns full details of a single commit by its hash."""
    print(f"Fetching commit: {commit_hash}")
    try:
        commit = repo.commit(commit_hash)
        return {
            "hash": commit.hexsha[:8],
            "full_hash": commit.hexsha,
            "author": commit.author.name,
            "email": commit.author.email,
            "date": datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d %H:%M"),
            "message": commit.message.strip(),
            "files_changed": list(commit.stats.files.keys()),
            "files_count": len(commit.stats.files),
            "stats": dict(commit.stats.files),
        }
    except Exception as e:
        print(f"Could not find commit {commit_hash}: {e}")
        return {}