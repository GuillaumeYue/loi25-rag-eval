"""The fixture imitates LégisQuébec's markup with made-up text; it contains no law text."""

from pathlib import Path

from fetch_corpus import parse_articles, write_markdown

FIXTURE = Path(__file__).parent / "fixtures" / "legisquebec-sample.html"


def test_parse_articles_from_sample_markup():
    articles = parse_articles(FIXTURE.read_text(encoding="utf-8"))
    numbers = [n for n, _ in articles]
    assert numbers == ["1", "3.7", "24"]

    art1 = dict(articles)["1"]
    lines = art1.splitlines()
    assert lines[0].startswith("1. Première phrase fictive")
    assert "1° premier élément;" in lines
    assert "2° second élément." in lines
    assert lines[-1].startswith("Deuxième alinéa fictif")
    # Amendment history and hidden spans are removed.
    assert "1993, c. 17" not in art1
    assert "caché" not in art1

    assert dict(articles)["3.7"].startswith("3.7. Article à numéro décimal")
    assert dict(articles)["24"] == "24. (Remplacé)."


def test_write_markdown_one_file_per_article(tmp_path: Path):
    articles = parse_articles(FIXTURE.read_text(encoding="utf-8"))
    n = write_markdown(articles, tmp_path)
    assert n == 3
    files = sorted(p.name for p in tmp_path.glob("*.md"))
    assert files == ["art-1.md", "art-24.md", "art-3.7.md"]
    body = (tmp_path / "art-3.7.md").read_text(encoding="utf-8")
    assert body.startswith("# Loi 25 (P-39.1), article 3.7\n")
    assert "3.7. Article à numéro décimal" in body
