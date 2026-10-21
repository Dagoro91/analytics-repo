"""Build the schema context for the LLM from the dbt documentation (models/gold/schema.yml)."""
from pathlib import Path

import yaml

SCHEMA_FILE = Path("models/gold/schema.yml")
CHROMA_PATH = "data/chroma"
COLLECTION = "gold_docs"


def load_docs() -> list[dict]:
    """One document per gold table, with descriptions."""
    spec = yaml.safe_load(SCHEMA_FILE.read_text())
    docs = []
    for model in spec["models"]:
        columns = "\n".join(
            f"  - {c['name']}: {c.get('description', '').strip()}" for c in model.get("columns", [])
        )
        text = (
            f"Table gold.{model['name']}: {' '.join(model['description'].split())}\n"
            f"Columns:\n{columns}"
        )
        docs.append({"id": model["name"], "text": text, "columns": [c["name"] for c in model.get("columns", [])]})
    return docs


def baseline_context() -> str:
    """No documentation: only table and column names."""
    return "\n".join(f"gold.{d['id']}({', '.join(d['columns'])})" for d in load_docs())


def build_index() -> None:
    """Index the documented schema in ChromaDB (local, free)."""
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION)
    docs = load_docs()
    collection.add(ids=[d["id"] for d in docs], documents=[d["text"] for d in docs])
    print(f"Indexed {len(docs)} gold tables in ChromaDB at {CHROMA_PATH}")


def rag_context(question: str, top_k: int = 2) -> str:
    """Retrieve the most relevant documented tables for the question."""
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION)
    result = collection.query(query_texts=[question], n_results=top_k)
    return "\n\n".join(result["documents"][0])


if __name__ == "__main__":
    build_index()
