"""Load and chunk the UCLA dining document corpus for the RAG pipeline.

Milestone 3 focuses on producing clean, metadata-rich chunks before any
embedding work happens. This module intentionally has no third-party
dependencies so it can be inspected and reused by later milestones.
"""

from __future__ import annotations

import argparse
import html
import random
import re
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent
# TODO: take it as an argument instead of hardcoding it
DOCS_PATH = PROJECT_ROOT / "documents" / "ucla-dining-hall" / "ucla-cld"

TARGET_CHARS = 900
# ? Anticipated Challenge #5
MAX_CHARS = 1024
OVERLAP_CHARS = 180
MIN_CHARS = 120

HEADER_SEPARATOR = "\n---"


def parse_header(raw_text: str) -> tuple[dict[str, str], str]:
    """Split a source file into metadata headers and body text."""
    if HEADER_SEPARATOR not in raw_text:
        return {}, raw_text

    header_text, body = raw_text.split(HEADER_SEPARATOR, 1)
    body = body.lstrip("- \n")

    metadata: dict[str, str] = {}
    for line in header_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized_key = key.strip().lower()
        if normalized_key and value.strip():
            metadata[normalized_key] = value.strip()

    return metadata, body


def clean_text(text: str) -> str:
    """Remove light extraction artifacts while preserving paragraph structure."""
    text = html.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_documents(docs_path: Path = DOCS_PATH) -> list[dict[str, str]]:
    """Load UCLA dining .txt documents with attribution metadata."""
    documents = []

    for filepath in sorted(docs_path.glob("*.txt")):
        raw_text = filepath.read_text(encoding="utf-8")
        header, body = parse_header(raw_text)
        text = clean_text(body)

        if not text:
            continue

        title = header.get("title") or filepath.stem.replace("_", " ").title()
        source_url = header.get("source_url", "")
        publication = header.get("publication", "")
        date = header.get("date") or header.get("date_collected", "")
        source_type = header.get("type", "")

        documents.append(
            {
                "title": title,
                "source_url": source_url,
                "publication": publication,
                "date": date,
                "type": source_type,
                "filename": filepath.name,
                "source_path": str(filepath.relative_to(PROJECT_ROOT)),
                "text": text,
            }
        )

    print(f"Loaded {len(documents)} UCLA dining document(s) from {docs_path}")
    return documents


def split_sentences(text: str) -> list[str]:
    """Split text on sentence boundaries, with a simple fallback for long lines."""
    sentences = re.split(r"(?<=[.!?])\s+(?=[\"'A-Z0-9])", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def split_long_text(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """Break an oversized paragraph into sentence-aware pieces."""
    speaker_match = re.match(r"^([A-Z]{1,4}:)\s+(.*)$", text, flags=re.DOTALL)
    speaker_label = ""
    working_text = text
    if speaker_match:
        speaker_label = speaker_match.group(1)
        working_text = speaker_match.group(2).strip()

    pieces = []
    current = ""

    for sentence in split_sentences(working_text):
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            pieces.append(current)
        current = sentence

        while len(current) > max_chars:
            split_at = current.rfind(" ", 0, max_chars)
            if split_at < max_chars // 2:
                split_at = max_chars
            pieces.append(current[:split_at].strip())
            current = current[split_at:].strip()

    if current:
        pieces.append(current)

    if speaker_label:
        return [
            f"{speaker_label} {piece}" if not piece.startswith(speaker_label) else piece
            for piece in pieces
        ]
    return pieces


def text_units(text: str) -> list[str]:
    """Return paragraph-sized units, splitting oversized paragraphs by sentence."""
    units = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= MAX_CHARS:
            units.append(paragraph)
        else:
            units.extend(split_long_text(paragraph))
    return units


def chunk_units(
    units: Iterable[str],
    target_chars: int = TARGET_CHARS,
    max_chars: int = MAX_CHARS,
    overlap_chars: int = OVERLAP_CHARS,
    min_chars: int = MIN_CHARS,
) -> list[str]:
    """Merge text units into chunks with whole-unit overlap."""
    chunks = []
    current: list[str] = []

    for unit in units:
        candidate = "\n\n".join([*current, unit]).strip()
        if current and len(candidate) > target_chars:
            chunk_text = "\n\n".join(current).strip()
            if len(chunk_text) >= min_chars:
                chunks.append(chunk_text)
            current = overlap_tail(current, overlap_chars)
            if len("\n\n".join([*current, unit]).strip()) > max_chars:
                current = []
            current.append(unit)
        else:
            current.append(unit)

    final_chunk = "\n\n".join(current).strip()
    if len(final_chunk) >= min_chars:
        chunks.append(final_chunk)

    return chunks


def overlap_tail(units: list[str], overlap_chars: int) -> list[str]:
    """Keep enough complete trailing units to preserve local context."""
    tail: list[str] = []
    total = 0
    for unit in reversed(units):
        tail.insert(0, unit)
        total += len(unit)
        if total >= overlap_chars:
            break
    return tail


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "document"


def chunk_document(document: dict[str, str]) -> list[dict[str, object]]:
    """Chunk one loaded document and attach source metadata to every chunk."""
    chunks = []
    base_id = slugify(Path(document["filename"]).stem)

    for index, chunk_text in enumerate(chunk_units(text_units(document["text"]))):
        chunks.append(
            {
                "text": chunk_text,
                "chunk_id": f"{base_id}_{index:03d}",
                "chunk_index": index,
                "title": document["title"],
                "source_url": document["source_url"],
                "publication": document["publication"],
                "date": document["date"],
                "type": document["type"],
                "filename": document["filename"],
                "source_path": document["source_path"],
                "char_count": len(chunk_text),
            }
        )

    return chunks


def build_chunks(docs_path: Path = DOCS_PATH) -> list[dict[str, object]]:
    """Load all documents and return all metadata-rich chunks."""
    chunks = []
    for document in load_documents(docs_path):
        chunks.extend(chunk_document(document))
    return chunks


def print_chunk_preview(chunks: list[dict[str, object]], count: int = 5) -> None:
    """Print representative chunks for manual Milestone 3 inspection."""
    if not chunks:
        print("No chunks produced.")
        return

    print(f"\nProduced {len(chunks)} total chunk(s).")
    print(
        "Chunk size summary: "
        f"min={min(c['char_count'] for c in chunks)}, "
        f"max={max(c['char_count'] for c in chunks)}, "
        f"avg={sum(int(c['char_count']) for c in chunks) // len(chunks)} chars"
    )

    sample_count = min(count, len(chunks))
    for chunk in random.sample(chunks, sample_count):
        print("\n" + "=" * 80)
        print(
            f"{chunk['chunk_id']} | {chunk['title']} | "
            f"{chunk['date']} | {chunk['char_count']} chars"
        )
        if chunk["source_url"]:
            print(chunk["source_url"])
        print("-" * 80)
        print(chunk["text"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load and chunk the UCLA dining corpus for inspection."
    )
    parser.add_argument(
        "--docs-path",
        type=Path,
        default=DOCS_PATH,
        help="Directory containing UCLA dining .txt source files.",
    )
    parser.add_argument(
        "--preview-count",
        type=int,
        default=5,
        help="Number of random chunks to print for inspection.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Random seed for reproducible preview chunks.",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    chunks = build_chunks(args.docs_path)
    print_chunk_preview(chunks, args.preview_count)


if __name__ == "__main__":
    main()
