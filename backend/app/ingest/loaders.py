"""Turn a file on disk into plain text plus a title.

Supported: .md, .txt (as is), .html (tags, scripts and styles removed), .pdf (pypdf).
Markdown is kept raw on purpose: HTML comments and other markup the user would
not see in a rendered page are exactly what an indirect-injection trap relies on.
"""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup

SUPPORTED_SUFFIXES = {".md", ".txt", ".html", ".htm", ".pdf"}


def load_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return path.read_text(encoding="utf-8")
    if suffix in {".html", ".htm"}:
        return _html_to_text(path.read_text(encoding="utf-8", errors="replace"))
    if suffix == ".pdf":
        return _pdf_to_text(path)
    raise ValueError(f"unsupported file type: {path.name}")


def title_for(path: Path, text: str) -> str:
    """First Markdown heading if there is one, otherwise the file stem."""
    for line in text.splitlines():
        m = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if m:
            return m.group(1)
    return path.stem


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text("\n")
    return _squeeze_blank_lines(text)


def _pdf_to_text(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return _squeeze_blank_lines("\n\n".join(pages))


def _squeeze_blank_lines(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines()]
    out: list[str] = []
    for ln in lines:
        if ln == "" and out and out[-1] == "":
            continue
        out.append(ln)
    return "\n".join(out).strip()
