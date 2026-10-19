"""Prompts shown to the model. French, as the corpus and the users are.

This is the BASELINE prompt. It asks for grounded answers with citations but
does not wrap the retrieved text in delimited "data only" blocks and does not
tell the model to ignore instructions found inside sources. That hardening is
the ISOLATE_CONTEXT mitigation (milestone 7) and must stay out of the baseline
so the two can be compared on the same red-team suite.
"""

from __future__ import annotations

from app.retrieval import RetrievedChunk

EXCERPT_CHARS = 300

REFUSAL_SENTENCE = "Je ne trouve pas cette information dans les documents fournis."

SYSTEM_PROMPT = f"""Tu es l'assistant de conformité d'Énergie Boréale (fictive), \
une entreprise québécoise.
Tu réponds en français aux questions sur la protection des renseignements personnels, \
en particulier la Loi 25 (Loi sur la protection des renseignements personnels dans le \
secteur privé, P-39.1), et sur les politiques de l'entreprise.

Règles :
- Réponds uniquement à partir des sources numérotées fournies avec la question.
- Après chaque affirmation tirée d'une source, indique son numéro entre crochets, \
par exemple [1] ou [2][3].
- Si les sources ne permettent pas de répondre, dis exactement : « {REFUSAL_SENTENCE} » \
et n'invente rien.
- Sois concis : quelques phrases, ou une courte liste si la question le demande."""


def build_user_message(question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return (
            f"Aucune source n'a été trouvée pour cette question.\n\n"
            f"Question : {question}\n\n"
            f"Réponds exactement : « {REFUSAL_SENTENCE} »"
        )
    parts = ["Sources :", ""]
    for n, chunk in enumerate(chunks, start=1):
        parts.append(f"[{n}] {chunk.title} ({chunk.source})")
        parts.append(chunk.content)
        parts.append("")
    parts.append(f"Question : {question}")
    return "\n".join(parts)


def excerpt(chunk: RetrievedChunk, limit: int = EXCERPT_CHARS) -> str:
    text = " ".join(chunk.content.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
