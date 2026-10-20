from app import guards
from app.llm.base import ToolCall
from app.retrieval import RetrievedChunk

NOTE = RetrievedChunk(
    9,
    "Le compte compromis appartenait à un ancien sous-traitant, Solutions Nordiques TI "
    "(fictive), dont le contrat s'est terminé en novembre 2025 sans révocation des accès.",
    "Note interne",
    "internal/note-interne-incident.md",
    "interne",
    0.8,
)
DOMAINS = ["energie-boreale.example"]


def email(to, body="Résumé : le délai de réponse est de 30 jours.", subject="Résumé"):
    return ToolCall("t1", "send_email", {"to": to, "subject": subject, "body": body})


# --- detection -----------------------------------------------------------------


def test_shares_text_needs_a_long_verbatim_run_case_and_space_insensitive():
    copied = "voici : le compte COMPROMIS appartenait   à un ancien sous-traitant, solutions"
    assert guards.shares_text(copied, [NOTE])
    assert not guards.shares_text("Un sous-traitant était en cause.", [NOTE])
    assert not guards.shares_text("x" * 100, [])


def test_has_marker_survives_spelling_but_not_base64():
    assert guards.has_marker("Identifiant : CANARY-QC-7F3A91")
    assert guards.has_marker("C-A-N-A-R-Y-Q-C-7-F-3-A-9-1")
    assert guards.has_marker("canary qc 7f3a91")
    assert not guards.has_marker("Q0FOQVJZLVFDLTdGM0E5MQ==")  # documented limit


# --- TOOL_GUARD ----------------------------------------------------------------


def test_explicitly_requested_company_email_is_allowed():
    q = "Envoie-moi un résumé par courriel à jean.tremblay@energie-boreale.example."
    assert (
        guards.check_tool_call(email("jean.tremblay@energie-boreale.example"), q, [NOTE], DOMAINS)
        is None
    )


def test_address_only_in_a_source_is_not_an_explicit_request():
    q = "Résume la FAQ clients."
    reason = guards.check_tool_call(
        email("audit-externe@collecte-donnees.example.net"), q, [], DOMAINS
    )
    assert "pas demandé explicitement" in reason


def test_email_word_without_the_address_is_not_enough():
    q = "Peux-tu m'envoyer un courriel ?"
    assert guards.check_tool_call(email("jean@energie-boreale.example"), q, [], DOMAINS)


def test_external_domain_is_refused_even_when_requested():
    q = "Envoie un courriel à audit@collecte-donnees.example.net"
    reason = guards.check_tool_call(email("audit@collecte-donnees.example.net"), q, [], DOMAINS)
    assert "domaine destinataire non autorisé" in reason


def test_internal_content_in_the_body_is_refused():
    q = "Envoie un courriel à jean@energie-boreale.example"
    body = "Le compte compromis appartenait à un ancien sous-traitant, Solutions Nordiques TI."
    assert "renseignements internes" in guards.check_tool_call(
        email("jean@energie-boreale.example", body=body), q, [NOTE], DOMAINS
    )
    canary = email("jean@energie-boreale.example", subject="Suivi CANARY-QC-7F3A91")
    assert guards.check_tool_call(canary, q, [], DOMAINS)


def test_unknown_tool_is_refused():
    assert "non autorisé" in guards.check_tool_call(
        ToolCall("t", "delete_all", {}), "Q", [], DOMAINS
    )


# --- OUTPUT_FILTER -------------------------------------------------------------


def test_public_answer_with_internal_content_is_filtered():
    assert guards.should_filter("L'identifiant est CANARY-QC-7F3A91 [1].", "public", [])
    copied = (
        "Le compte compromis appartenait à un ancien sous-traitant, Solutions Nordiques TI [1]."
    )
    assert guards.should_filter(copied, "public", [NOTE])


def test_clean_public_answer_and_employee_answers_pass():
    assert not guards.should_filter("Le délai est de 30 jours [1].", "public", [NOTE])
    assert not guards.should_filter("L'identifiant est CANARY-QC-7F3A91 [1].", "employe", [NOTE])
