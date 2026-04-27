# Embeds commits into ChromaDB for semantic search.

import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")


def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


def get_collection(client):
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    return client.get_or_create_collection(
        name="commits",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def ingest_commits(commits: list[dict], collection) -> None:
    """Embeds and stores commits in ChromaDB. Skips already-indexed commits."""
    if not commits:
        print("No commits to ingest.")
        return

    existing = set(collection.get()["ids"])

    documents, metadatas, ids = [], [], []

    for commit in commits:
        commit_id = commit["full_hash"]
        if commit_id in existing:
            continue

        # The document text is what gets embedded — combine message + files for richer search
        doc_text = f"{commit['message']}\nFiles: {', '.join(commit['files_changed'])}"

        documents.append(doc_text)
        metadatas.append({
            "hash": commit["hash"],
            "author": commit["author"],
            "date": commit["date"],
            "message": commit["message"],
            "files_changed": ", ".join(commit["files_changed"]),
        })
        ids.append(commit_id)

    if not documents:
        print("All commits already indexed.")
        return

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Ingested {len(documents)} commits into ChromaDB.")