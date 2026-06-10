"""Run the Milestone 6 evaluation questions through retrieval and generation."""

from __future__ import annotations

import json

from generator import generate_response
from retriever import get_collection, index_documents, retrieve


QUESTIONS = [
    "What do students and reviewers say makes Bruin Plate a good option for healthy eating or dietary restrictions?",
    "How do UCLA meal plan types differ between Regular (R) and Premium (P), according to the Bruin 101 podcast?",
    "When are UCLA dining halls and quick-service/takeout locations usually busiest, according to The Stack's swipe analysis?",
    "What recent UCLA Dining problems did students report around schedule changes, strikes, mobile ordering, and food trucks?",
    "What do the sources say about The Study at Hedrick as a dining option?",
    "How much does a 14P meal plan cost in dollars per quarter?",
]


def compact_result(result: dict) -> dict:
    return {
        "distance": result.get("distance"),
        "title": result.get("title"),
        "filename": result.get("filename"),
        "chunk_index": result.get("chunk_index"),
    }


def main() -> None:
    if get_collection().count() == 0:
        print("No ChromaDB chunks found. Building the index before evaluation...")
        index_documents(reset=True)

    for index, question in enumerate(QUESTIONS, start=1):
        retrieved = retrieve(question)
        print(f"\n### Q{index}: {question}\n")
        print("Retrieved chunks:")
        print(json.dumps([compact_result(result) for result in retrieved], indent=2))
        print("\nSystem response:")
        print(generate_response(question, retrieved))


if __name__ == "__main__":
    main()
