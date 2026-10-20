"""Code-level mitigations: TOOL_GUARD (before a tool runs) and OUTPUT_FILTER
(before an answer leaves). Both are plain functions over the request, the
model's output and the chunks retrieved for this request; nothing here calls
the model.

"Internal content" is detected two ways, and the same check serves both guards:
- a marker such as the canary prefix, matched after reducing text to letters
  and digits, so "C-A-N-A-R-Y-..." is caught (base64 is not: see README limits);
- a run of MIN_OVERLAP characters shared with an `interne` chunk retrieved for
  this request (whitespace-collapsed, case-insensitive). This needs no list of
  secrets: copying internal text verbatim is what it catches.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

from app.llm.base import ToolCall
from app.retrieval import RetrievedChunk

MIN_OVERLAP = 30
INTERNAL_MARKERS = ("CANARY",)
EMAIL_WORDS = ("courriel", "mail")  # "mail" also covers email, e-mail, Mail

FILTERED_ANSWER = (
    "Réponse retenue : elle contenait des renseignements internes qui ne peuvent pas "
    "être communiqués à ce profil d'utilisateur."
)


# --- shared detection ---------------------------------------------------------


def _alnum_upper(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^A-Za-z0-9]", "", text).upper()


def _collapse(text: str) -> str:
    return " ".join(text.split()).lower()


def _windows(text: str, size: int) -> set[str]:
    return {text[i : i + size] for i in range(len(text) - size + 1)}


def shares_text(text: str, chunks: Iterable[RetrievedChunk], min_len: int = MIN_OVERLAP) -> bool:
    """True if `text` contains a run of `min_len` characters found in any chunk."""
    candidate = _collapse(text)
    if len(candidate) < min_len:
        return False
    mine = _windows(candidate, min_len)
    return any(mine & _windows(_collapse(c.content), min_len) for c in chunks)


def has_marker(text: str, markers: Iterable[str] = INTERNAL_MARKERS) -> bool:
    flat = _alnum_upper(text)
    return any(_alnum_upper(m) in flat for m in markers)


def contains_internal(text: str, internal_chunks: list[RetrievedChunk]) -> bool:
    return has_marker(text) or shares_text(text, internal_chunks)


# --- TOOL_GUARD ---------------------------------------------------------------


def check_tool_call(
    call: ToolCall,
    question: str,
    internal_chunks: list[RetrievedChunk],
    allowed_domains: list[str],
) -> str | None:
    """Return why the call must be refused, or None if it may run.

    Three rules for send_email, all required:
    1. the user explicitly asked: the question mentions an email AND contains
       the recipient address verbatim (an address only a source mentions does
       not count, which is exactly the indirect-injection case);
    2. the recipient's domain is allow-listed;
    3. subject and body carry no internal content.
    """
    if call.name != "send_email":
        return f"outil non autorisé : {call.name}"
    to = str(call.arguments.get("to", "")).strip().lower()
    q = question.lower()
    if not any(word in q for word in EMAIL_WORDS) or not to or to not in q:
        return "l'utilisateur n'a pas demandé explicitement un envoi à cette adresse"
    domain = to.rsplit("@", 1)[-1] if "@" in to else ""
    if domain not in allowed_domains:
        return f"domaine destinataire non autorisé : {domain or '(aucun)'}"
    content = f"{call.arguments.get('subject', '')}\n{call.arguments.get('body', '')}"
    if contains_internal(content, internal_chunks):
        return "le courriel contient des renseignements internes"
    return None


# --- OUTPUT_FILTER ------------------------------------------------------------


def should_filter(answer: str, role: str, internal_chunks: list[RetrievedChunk]) -> bool:
    """Withhold a public answer that carries internal content. Employees are not filtered."""
    return role != "employe" and contains_internal(answer, internal_chunks)
