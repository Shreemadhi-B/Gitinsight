# Searches ChromaDB for commits semantically similar to a given query.

from ingest import get_chroma_client, get_collection


def search_commits(query: str, n_results: int = 5) -> list[dict]:
    """Finds commits most semantically similar to the query."""
    print(f"Searching commits for: '{query}'")

    client = get_chroma_client()
    collection = get_collection(client)

    if collection.count() == 0:
        print("ChromaDB is empty. Run ingest first.")
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    metadatas = results["metadatas"][0]
    documents = results["documents"][0]
    distances = results["distances"][0]

    search_results = []
    for i, metadata in enumerate(metadatas):
        search_results.append({
            **metadata,
            "document": documents[i],
            "similarity_score": round(1 - distances[i], 3),
        })

    print(f"Found {len(search_results)} results.")
    return search_results


def format_search_results(results: list[dict]) -> str:
    """Formats search results as readable text for the agent."""
    if not results:
        return "No relevant commits found."

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"Result {i} (similarity: {r['similarity_score']}):")
        lines.append(f"  Commit:  {r['hash']}")
        lines.append(f"  Author:  {r['author']}")
        lines.append(f"  Date:    {r['date']}")
        lines.append(f"  Message: {r['message']}")
        lines.append(f"  Files:   {r['files_changed']}")
        lines.append("")

    return "\n".join(lines)