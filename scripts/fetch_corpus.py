"""Download P-39.1 (Loi 25) from LégisQuébec and write one Markdown file per article.

Usage:
    python scripts/fetch_corpus.py                 # try to download, then parse
    python scripts/fetch_corpus.py --html FILE     # parse an HTML file saved by hand

Output: data/public/loi-25/art-<N>.md (git-ignored). One file per article so an
accuracy eval can check "expected article in top-k" by looking at the source path.

LégisQuébec sits behind a bot filter (CloudFront). Plain HTTP clients get a 403
or a 503 challenge page, while a browser loads the page fine. When the download
fails, save the page from a browser as data/raw/P-39.1.html and re-run with --html.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_HTML = REPO_ROOT / "data" / "raw" / "P-39.1.html"
OUT_DIR = REPO_ROOT / "data" / "public" / "loi-25"
URL = "https://www.legisquebec.gouv.qc.ca/fr/document/lc/P-39.1"
LAW_TITLE = "Loi sur la protection des renseignements personnels dans le secteur privé (P-39.1)"

# Elements that are navigation or metadata, not law text.
_NOISE_SELECTORS = (
    "div.HistoricalNote",
    "div.HistoryLink",
    ".Hidden",
    ".WidthFixForLabel",
)


def download(dest: Path) -> bool:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
        ),
        "Accept-Language": "fr-CA,fr;q=0.9",
    }
    try:
        resp = requests.get(URL, headers=headers, timeout=30)
    except requests.RequestException as exc:
        print(f"download failed: {exc}")
        return False
    if resp.status_code != 200 or 'id="se:1"' not in resp.text:
        print(f"download blocked (HTTP {resp.status_code}, no article markup in body)")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(resp.text, encoding="utf-8")
    print(f"saved {dest}")
    return True


def parse_articles(html: str) -> list[tuple[str, str]]:
    """Return (article_number, text) pairs in document order.

    LégisQuébec marks each article as <div class="section" id="se:N"> (N may be
    "21_1" for article 21.1). Inside, every paragraph, numbered item or
    sub-item is a <div> whose own inline <span>s hold the text, with nested
    <div>s for deeper items. Amendment history sits in div.HistoricalNote.
    """
    soup = BeautifulSoup(html, "html.parser")
    articles: list[tuple[str, str]] = []
    for div in soup.select('div.section[id^="se:"]'):
        if not isinstance(div, Tag):
            continue
        sec_id = str(div.get("id", ""))
        if "-ss:" in sec_id:
            continue
        number = sec_id.removeprefix("se:").replace("_", ".")
        for selector in _NOISE_SELECTORS:
            for noise in div.select(selector):
                noise.decompose()
        # The section div itself is a block too: repealed articles ("(Remplacé).")
        # keep their text directly in it, with no nested paragraph div.
        lines = [_inline_text(block) for block in [div, *div.find_all("div")]]
        text = "\n".join(ln for ln in lines if ln)
        articles.append((number, text))
    return articles


def _inline_text(block: Tag) -> str:
    """Text of a block's own content, ignoring nested <div> blocks (they get their own line)."""
    parts = [
        child if isinstance(child, str) else child.get_text("")
        for child in block.children
        if isinstance(child, str) or (isinstance(child, Tag) and child.name != "div")
    ]
    text = " ".join("".join(parts).split())
    # Labels come out glued to the text ("8.La personne", "1°des fins"): add a space.
    # The lookahead excludes digits and dots so "3.7." is never split into "3." + "7.".
    return re.sub(r"^(\d+(?:\.\d+)*[.°]|[a-z]\))(?=[^\s\d.])", r"\1 ", text)


def write_markdown(articles: list[tuple[str, str]], out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("art-*.md"):
        old.unlink()
    for number, text in articles:
        path = out_dir / f"art-{number}.md"
        body = f"# Loi 25 (P-39.1), article {number}\n\n{LAW_TITLE}\n\n{text}\n"
        path.write_text(body, encoding="utf-8")
    return len(articles)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--html", type=Path, help="parse this saved HTML instead of downloading")
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    args = parser.parse_args(argv)

    html_path = args.html or RAW_HTML
    if args.html is None and not html_path.exists() and not download(html_path):
        print(
            "\nManual fallback:\n"
            f"  1. Open {URL} in a browser.\n"
            f"  2. Save the page (HTML only) as {RAW_HTML}\n"
            "  3. Re-run: python scripts/fetch_corpus.py\n"
        )
        return 1
    articles = parse_articles(html_path.read_text(encoding="utf-8", errors="replace"))
    if not articles:
        print(f"no articles found in {html_path}; is it the full-text page?")
        return 1
    n = write_markdown(articles, args.out)
    print(f"wrote {n} articles to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
