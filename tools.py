import json
import random
from pathlib import Path
from openai import OpenAI
import chromadb
import streamlit as st


def search_docs(query: str) -> str:
    """Search the docs collection for passages related to the query."""
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)

    script_dir = Path(__file__).parent
    chroma_path = script_dir / "chroma_db"

    # Embed the query
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    query_embedding = response.data[0].embedding

    # Query Chroma
    chroma_client = chromadb.PersistentClient(path=str(chroma_path))
    collection = chroma_client.get_or_create_collection(name="docs")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    if not results["documents"] or not results["documents"][0]:
        return "No strong match in the documents."

    # Check if closest distance is above 1.4
    closest_distance = results["distances"][0][0]
    if closest_distance > 1.4:
        return "No strong match in the documents."

    # Format results
    passages = []
    for i, doc in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        source = metadata.get("source", "Unknown")
        page = metadata.get("page", "?")
        passages.append(f"[{source} p.{page}]\n{doc}\n")

    return "\n".join(passages)


def save_weak_spot(topic: str, note: str) -> str:
    """Save a weak spot to the revision list."""
    script_dir = Path(__file__).parent
    weak_spots_path = script_dir / "weak_spots.json"

    # Load existing weak spots
    if weak_spots_path.exists():
        with open(weak_spots_path, "r") as f:
            weak_spots = json.load(f)
    else:
        weak_spots = []

    # Add new weak spot
    weak_spots.append({"topic": topic, "note": note})

    # Save back to file
    with open(weak_spots_path, "w") as f:
        json.dump(weak_spots, f, indent=2)

    return f"Added '{topic}' to your revision list."


def list_weak_spots() -> str:
    """Return the list of weak spots."""
    script_dir = Path(__file__).parent
    weak_spots_path = script_dir / "weak_spots.json"

    if not weak_spots_path.exists():
        return "No weak spots yet. Keep practicing!"

    with open(weak_spots_path, "r") as f:
        weak_spots = json.load(f)

    if not weak_spots:
        return "No weak spots yet. Keep practicing!"

    result = "Your revision list:\n"
    for i, spot in enumerate(weak_spots, 1):
        result += f"{i}. {spot['topic']}: {spot['note']}\n"

    return result


def pick_quiz_topic() -> str:
    """Pick one weak spot at random to quiz the user on."""
    script_dir = Path(__file__).parent
    weak_spots_path = script_dir / "weak_spots.json"

    if not weak_spots_path.exists():
        return "No weak spots yet, so there is nothing to quiz on."

    with open(weak_spots_path, "r") as f:
        weak_spots = json.load(f)

    if not weak_spots:
        return "No weak spots yet, so there is nothing to quiz on."

    spot = random.choice(weak_spots)
    return f"Quiz topic: {spot['topic']}\nNote: {spot['note']}"


if __name__ == "__main__":
    print("=== Testing search_docs ===")
    result = search_docs("What is RAG?")
    print(result)
    print()

    print("=== Testing save_weak_spot ===")
    result = save_weak_spot("Chunking strategy", "Remember to use sliding window overlap")
    print(result)
    print()

    print("=== Testing list_weak_spots ===")
    result = list_weak_spots()
    print(result)
    print()

    print("=== Testing pick_quiz_topic ===")
    result = pick_quiz_topic()
    print(result)
