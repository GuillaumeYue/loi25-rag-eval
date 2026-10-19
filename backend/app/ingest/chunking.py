"""Paragraph-aware chunking.

Paragraphs (blocks separated by blank lines) are packed into chunks of at most
`max_chars`. A paragraph longer than `max_chars` is split on sentence ends, then
hard-cut if a single sentence is still too long. Each chunk after the first
starts with the last `overlap` characters of the previous chunk so an answer
that straddles a boundary is still retrievable.
"""

from __future__ import annotations

import re

_SENTENCE_END = re.compile(r"(?<=[.!?;:])\s+")


def chunk_text(text: str, max_chars: int = 900, overlap: int = 150) -> list[str]:
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars")

    pieces = _split_long_paragraphs(_paragraphs(text), max_chars)
    chunks: list[str] = []
    current = ""

    for piece in pieces:
        candidate = piece if not current else f"{current}\n\n{piece}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        # Start the next chunk with the tail of the previous one.
        tail = chunks[-1][-overlap:].lstrip() if chunks and overlap else ""
        current = f"{tail}\n\n{piece}" if tail else piece
        if len(current) > max_chars:
            # Tail + piece does not fit; keep the piece alone (it fits on its own).
            current = piece

    if current:
        chunks.append(current)
    return chunks


def _paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _split_long_paragraphs(paragraphs: list[str], max_chars: int) -> list[str]:
    out: list[str] = []
    for p in paragraphs:
        if len(p) <= max_chars:
            out.append(p)
            continue
        current = ""
        for sentence in _SENTENCE_END.split(p):
            for part in _hard_cut(sentence, max_chars):
                candidate = part if not current else f"{current} {part}"
                if len(candidate) <= max_chars:
                    current = candidate
                else:
                    out.append(current)
                    current = part
        if current:
            out.append(current)
    return out


def _hard_cut(s: str, max_chars: int) -> list[str]:
    return [s[i : i + max_chars] for i in range(0, len(s), max_chars)] or [s]
