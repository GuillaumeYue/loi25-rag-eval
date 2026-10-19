from app.prompting import REFUSAL_SENTENCE, SYSTEM_PROMPT, build_user_message, excerpt
from app.retrieval import RetrievedChunk


def chunk(n: int, content: str = "Contenu", classification: str = "public") -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=n,
        content=content,
        title=f"Titre {n}",
        source=f"public/doc-{n}.md",
        classification=classification,
        score=0.9,
    )


def test_sources_are_numbered_from_one_and_question_is_last():
    msg = build_user_message("Quel délai ?", [chunk(1, "Alpha"), chunk(2, "Beta")])
    assert "[1] Titre 1 (public/doc-1.md)\nAlpha" in msg
    assert "[2] Titre 2 (public/doc-2.md)\nBeta" in msg
    assert msg.index("[1]") < msg.index("[2]") < msg.index("Question : Quel délai ?")
    assert msg.rstrip().endswith("Question : Quel délai ?")


def test_no_sources_asks_for_the_refusal_sentence():
    msg = build_user_message("Météo ?", [])
    assert REFUSAL_SENTENCE in msg
    assert "[1]" not in msg


def test_system_prompt_mentions_citations_and_refusal():
    assert "[1]" in SYSTEM_PROMPT
    assert REFUSAL_SENTENCE in SYSTEM_PROMPT


def test_excerpt_is_truncated_and_single_line():
    long = "mot " * 200 + "\n\nautre ligne"
    e = excerpt(chunk(1, long))
    assert len(e) <= 300
    assert "\n" not in e
    assert e.endswith("…")
    assert excerpt(chunk(1, "court")) == "court"
