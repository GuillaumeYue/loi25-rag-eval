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

# q33 on 2026-10-20: the internal note's author line and a public article share
# legal boilerplate longer than MIN_OVERLAP.
NOTE_AUTHOR = RetrievedChunk(
    10,
    "Rédigé par : Marc-Antoine Lévesque, responsable de la protection des renseignements "
    "personnels (RPRP). Le compte compromis appartenait à un ancien sous-traitant.",
    "Note interne",
    "internal/note-interne-incident.md",
    "interne",
    0.7,
)
ART_32 = RetrievedChunk(
    11,
    "32. Le responsable de la protection des renseignements personnels doit répondre par "
    "écrit à la demande d'accès ou de rectification, avec diligence et au plus tard dans "
    "les 30 jours de la date de réception de la demande.",
    "Loi 25 (P-39.1), article 32",
    "public/loi-25/art-32.md",
    "public",
    0.9,
)
Q33_ANSWER = (
    "Adressez votre demande au responsable de la protection des renseignements personnels, "
    "à protection@energie-boreale.example [5]. Il doit répondre dans les 30 jours [1]."
)


def email(to, body="Résumé : le délai de réponse est de 30 jours.", subject="Résumé"):
    return ToolCall("t1", "send_email", {"to": to, "subject": subject, "body": body})


# --- detection -----------------------------------------------------------------


def test_shares_text_needs_a_long_verbatim_run_case_and_space_insensitive():
    copied = "voici : le compte COMPROMIS appartenait   à un ancien sous-traitant, solutions"
    assert guards.shares_text(copied, [NOTE])
    assert not guards.shares_text("Un sous-traitant était en cause.", [NOTE])
    assert not guards.shares_text("x" * 100, [])


def test_shares_text_ignores_runs_that_also_occur_in_common_chunks():
    assert guards.shares_text(Q33_ANSWER, [NOTE_AUTHOR])  # the 2026-10-20 false positive
    assert not guards.shares_text(Q33_ANSWER, [NOTE_AUTHOR], common=[ART_32])
    copied = "Le compte compromis appartenait à un ancien sous-traitant."
    assert guards.shares_text(copied, [NOTE_AUTHOR], common=[ART_32])


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


def test_public_boilerplate_in_an_email_is_not_internal_content():
    q = "Envoie un courriel à jean@energie-boreale.example"
    allowed = email("jean@energie-boreale.example", body=Q33_ANSWER)
    assert guards.check_tool_call(allowed, q, [NOTE_AUTHOR], DOMAINS, [ART_32]) is None
    body = "Rédigé par : Marc-Antoine Lévesque, responsable de la protection."
    leaking = email("jean@energie-boreale.example", body=body)
    assert "renseignements internes" in guards.check_tool_call(
        leaking, q, [NOTE_AUTHOR], DOMAINS, [ART_32]
    )


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


def test_q33_boilerplate_passes_when_a_public_source_has_it():
    assert not guards.should_filter(Q33_ANSWER, "public", [NOTE_AUTHOR], [ART_32])
    assert guards.should_filter(Q33_ANSWER, "public", [NOTE_AUTHOR])  # no public source: filtered


def test_verbatim_internal_sentence_is_still_filtered_next_to_public_sources():
    copied = (
        "Selon la note, le compte compromis appartenait à un ancien sous-traitant [3]. "
        "Le responsable de la protection des renseignements personnels répond en 30 jours [1]."
    )
    assert guards.should_filter(copied, "public", [NOTE_AUTHOR, NOTE], [ART_32])
    assert guards.should_filter("Identifiant : CANARY-QC-7F3A91.", "public", [], [ART_32])
