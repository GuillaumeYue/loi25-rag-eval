from pathlib import Path

import pytest

from app.ingest.loaders import load_file, title_for

FIXTURES = Path(__file__).parent / "fixtures"


def test_markdown_is_loaded_verbatim(tmp_path: Path):
    p = tmp_path / "doc.md"
    p.write_text("# Titre\n\nTexte <!-- commentaire caché -->\n", encoding="utf-8")
    text = load_file(p)
    # Raw markdown keeps HTML comments: that is what the injection trap relies on.
    assert "commentaire caché" in text
    assert title_for(p, text) == "Titre"


def test_txt_title_falls_back_to_filename(tmp_path: Path):
    p = tmp_path / "note-sans-titre.txt"
    p.write_text("Juste du texte.", encoding="utf-8")
    assert title_for(p, load_file(p)) == "note-sans-titre"


def test_html_strips_tags_and_scripts(tmp_path: Path):
    p = tmp_path / "page.html"
    p.write_text(
        "<html><head><style>p{}</style><script>alert(1)</script></head>"
        "<body><h1>Politique</h1><p>Premier paragraphe.</p><p>Deuxième.</p></body></html>",
        encoding="utf-8",
    )
    text = load_file(p)
    assert "alert" not in text and "p{}" not in text
    assert "Premier paragraphe." in text and "Deuxième." in text
    assert "<p>" not in text


def test_pdf_text_is_extracted():
    text = load_file(FIXTURES / "minimal.pdf")
    assert "Bonjour PDF" in text


def test_unsupported_suffix_raises(tmp_path: Path):
    p = tmp_path / "data.xlsx"
    p.write_bytes(b"")
    with pytest.raises(ValueError):
        load_file(p)
