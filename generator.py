"""Generate grounded UCLA dining answers from retrieved chunks."""

from __future__ import annotations

from typing import Any

from groq import Groq

from config import GROQ_API_KEY, LLM_MODEL

MAX_CONTEXT_CHUNKS = 5
MAX_CHUNK_CHARS = 1400
LOW_RELEVANCE_DISTANCE = 0.58

NO_CONTEXT_RESPONSE = (
    "I don't have enough information in the retrieved UCLA dining sources to answer that. "
    "Try rephrasing the question or asking about dining halls, meal plans, wait times, "
    "food trucks, mobile ordering, or student dining experiences covered by the corpus."
)


def _client() -> Groq:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to .env before running generation."
        )
    return Groq(api_key=GROQ_API_KEY)


def _source_label(chunk: dict[str, Any]) -> str:
    title = str(chunk.get("title") or chunk.get("filename") or "Unknown source")
    date = str(chunk.get("date") or "").strip()
    return f"{title} ({date})" if date else title


def _filter_chunks(retrieved_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep relevant chunks while avoiding a totally empty context on hard queries."""
    if not retrieved_chunks:
        return []

    filtered = [
        chunk
        for chunk in retrieved_chunks
        if float(chunk.get("distance", 1.0)) <= LOW_RELEVANCE_DISTANCE
    ]
    return (filtered or retrieved_chunks[:2])[:MAX_CONTEXT_CHUNKS]


def format_context(chunks: list[dict[str, Any]]) -> str:
    """Format retrieved chunks with stable citation numbers for the LLM prompt."""
    blocks = []
    for index, chunk in enumerate(chunks, start=1):
        text = str(chunk.get("text", "")).strip()
        if len(text) > MAX_CHUNK_CHARS:
            text = text[:MAX_CHUNK_CHARS].rsplit(" ", 1)[0].strip() + "..."

        source = _source_label(chunk)
        url = str(chunk.get("source_url") or "").strip()
        distance = chunk.get("distance", "unknown")

        blocks.append(
            f"[{index}] Source: {source}\n"
            f"URL: {url or 'No URL provided'}\n"
            f"Retrieval distance: {distance}\n"
            f"Text:\n{text}"
        )
    return "\n\n---\n\n".join(blocks)


def format_sources(chunks: list[dict[str, Any]]) -> str:
    """Build a programmatic source list matching the prompt's chunk numbers."""
    if not chunks:
        return ""

    lines = ["\n\nSources:"]
    for index, chunk in enumerate(chunks, start=1):
        label = _source_label(chunk)
        url = str(chunk.get("source_url") or "").strip()
        if url:
            lines.append(f"{index}. {label} - {url}")
        else:
            lines.append(f"{index}. {label}")
    return "\n".join(lines)


def generate_response(query: str, retrieved_chunks: list[dict[str, Any]]) -> str:
    """
    Generate a grounded answer from retrieved UCLA dining chunks.

    The answer should use only retrieved context, cite numbered chunks inline, and
    decline when the provided context does not contain the answer.
    """
    chunks = _filter_chunks(retrieved_chunks)
    if not chunks:
        return NO_CONTEXT_RESPONSE

    context = format_context(chunks)
    system_prompt = (
        "You answer questions for The Unofficial Guide to UCLA dining. "
        "Use only the retrieved context provided by the user. Do not use outside knowledge, "
        "current menus, current prices, or assumptions. If the context does not contain "
        "enough information to answer, say: \"I don't have enough information in the provided "
        "sources to answer that.\" Keep the answer concise but specific. Cite claims with "
        "the numbered source markers like [1] or [2]. If sources disagree or are time-bound, "
        "say so instead of blending them into one certainty."
    )
    user_prompt = f"""Retrieved context:
{context}

Question: {query}

Answer using only the retrieved context. Include inline citations such as [1]."""

    response = _client().chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=550,
    )

    answer = response.choices[0].message.content.strip()
    return f"{answer}{format_sources(chunks)}"
