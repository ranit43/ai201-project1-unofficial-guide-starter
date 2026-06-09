"""Embed UCLA dining chunks in ChromaDB and retrieve relevant evidence.

Milestone 4 keeps generation out of the loop on purpose: this module indexes
the chunks produced by ingest.py, then lets us inspect semantic-search results
directly before adding an LLM in Milestone 5.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

from config import CHROMA_COLLECTION, CHROMA_PATH, DOCS_PATH, EMBEDDING_MODEL, N_RESULTS


def _model_cache_exists(model_name: str) -> bool:
    model_names = [model_name]
    if "/" not in model_name:
        model_names.append(f"sentence-transformers/{model_name}")

    cache_root = Path.home() / ".cache" / "huggingface" / "hub"
    return any(
        (cache_root / f"models--{name.replace('/', '--')}").exists()
        for name in model_names
    )


if _model_cache_exists(EMBEDDING_MODEL):
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import chromadb
from chromadb.utils import embedding_functions

from ingest import build_chunks

METADATA_KEYS = (
    "chunk_id",
    "chunk_index",
    "title",
    "source_url",
    "publication",
    "date",
    "type",
    "filename",
    "source_path",
    "char_count",
)

EVAL_SMOKE_QUERIES = [
    "What do students and reviewers say makes Bruin Plate a good option for healthy eating or dietary restrictions?",
    "How do UCLA meal plan types differ between Regular and Premium?",
    "When are UCLA dining halls and quick-service takeout locations usually busiest?",
]


def _embedding_function():
    """Create the shared sentence-transformers embedding function."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )


_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_embedding_function(),
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the active ChromaDB collection."""
    return _collection


def reset_collection():
    """Delete and recreate the configured collection for a clean re-index."""
    global _collection

    try:
        _client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass

    _collection = _client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


def _metadata_for_chroma(chunk: dict[str, Any]) -> dict[str, str | int | float | bool]:
    """Keep only scalar metadata values ChromaDB can store."""
    metadata: dict[str, str | int | float | bool] = {}
    for key in METADATA_KEYS:
        value = chunk.get(key)
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            metadata[key] = value
        else:
            metadata[key] = str(value)
    return metadata


def embed_and_store(chunks: list[dict[str, Any]], reset: bool = False) -> int:
    """Embed chunks and upsert them into ChromaDB with source metadata."""
    if reset:
        reset_collection()

    if not chunks:
        print("No chunks to store.")
        return get_collection().count()

    get_collection().upsert(
        documents=[str(chunk["text"]) for chunk in chunks],
        metadatas=[_metadata_for_chroma(chunk) for chunk in chunks],
        ids=[str(chunk["chunk_id"]) for chunk in chunks],
    )

    count = get_collection().count()
    print(f"Stored {count} total chunk(s) in {CHROMA_COLLECTION}.")
    return count


def index_documents(docs_path: str | Path = DOCS_PATH, reset: bool = True) -> int:
    """Build chunks from source documents and store them in the vector database."""
    chunks = build_chunks(Path(docs_path))
    return embed_and_store(chunks, reset=reset)


def retrieve(query: str, n_results: int = N_RESULTS) -> list[dict[str, Any]]:
    """Return the top matching chunks for a plain-language query."""
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    limit = min(n_results, count)
    results = collection.query(
        query_texts=[query],
        n_results=limit,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for doc, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append(
            {
                "text": doc,
                "distance": round(float(distance), 4),
                "chunk_id": metadata.get("chunk_id", ""),
                "chunk_index": metadata.get("chunk_index", -1),
                "title": metadata.get("title", "Unknown source"),
                "source_url": metadata.get("source_url", ""),
                "publication": metadata.get("publication", ""),
                "date": metadata.get("date", ""),
                "filename": metadata.get("filename", ""),
                "source_path": metadata.get("source_path", ""),
                "char_count": metadata.get("char_count", len(doc)),
            }
        )

    return output


def print_results(query: str, results: list[dict[str, Any]]) -> None:
    """Print retrieval results in a format useful for Milestone 4 inspection."""
    print("\n" + "=" * 88)
    print(f"Query: {query}")
    print("=" * 88)

    if not results:
        print("No results. Build the index first with: python retriever.py --rebuild-index")
        return

    for rank, result in enumerate(results, start=1):
        source_bits = [result["title"]]
        if result.get("date"):
            source_bits.append(str(result["date"]))
        if result.get("filename"):
            source_bits.append(str(result["filename"]))

        print(f"\n[{rank}] distance={result['distance']} | {' | '.join(source_bits)}")
        if result.get("source_url"):
            print(result["source_url"])
        print("-" * 88)
        print(result["text"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index UCLA dining chunks and inspect semantic retrieval results."
    )
    parser.add_argument(
        "--rebuild-index",
        action="store_true",
        help="Rebuild the ChromaDB collection from the current document chunks.",
    )
    parser.add_argument(
        "--append-index",
        action="store_true",
        help="Upsert chunks without deleting the existing collection first.",
    )
    parser.add_argument(
        "--docs-path",
        type=Path,
        default=Path(DOCS_PATH),
        help="Directory containing UCLA dining .txt source files.",
    )
    parser.add_argument("--query", help="Question to run through semantic retrieval.")
    parser.add_argument(
        "--top-k",
        type=int,
        default=N_RESULTS,
        help="Number of retrieved chunks to print.",
    )
    parser.add_argument(
        "--eval-smoke",
        action="store_true",
        help="Run three planning.md evaluation queries and print retrieved chunks.",
    )
    args = parser.parse_args()

    if args.rebuild_index or args.append_index:
        index_documents(args.docs_path, reset=args.rebuild_index)

    if args.query:
        print_results(args.query, retrieve(args.query, n_results=args.top_k))

    if args.eval_smoke:
        if get_collection().count() == 0:
            index_documents(args.docs_path, reset=True)
        for query in EVAL_SMOKE_QUERIES:
            print_results(query, retrieve(query, n_results=args.top_k))

    if not (args.rebuild_index or args.append_index or args.query or args.eval_smoke):
        parser.print_help()


if __name__ == "__main__":
    main()
