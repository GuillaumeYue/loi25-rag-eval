from pathlib import Path

import pytest

from app.ingest.ingest import classification_for


def test_public_and_internal_paths(tmp_path: Path):
    assert classification_for(tmp_path / "public" / "faq.md", tmp_path) == "public"
    assert classification_for(tmp_path / "public" / "loi-25" / "art-1.md", tmp_path) == "public"
    assert classification_for(tmp_path / "internal" / "note.md", tmp_path) == "interne"


def test_other_paths_are_rejected(tmp_path: Path):
    with pytest.raises(ValueError):
        classification_for(tmp_path / "raw" / "P-39.1.html", tmp_path)
