import math

import pytest

from app.embeddings import get_embedder
from app.embeddings.stub import StubEmbedder


def test_stub_dimension_and_unit_norm():
    (v,) = StubEmbedder().embed(["Loi 25"])
    assert len(v) == 384
    assert math.isclose(math.sqrt(sum(x * x for x in v)), 1.0, rel_tol=1e-9)


def test_stub_is_deterministic_and_text_sensitive():
    e = StubEmbedder()
    a1, a2, b = e.embed(["article 8", "article 8", "article 9"])
    assert a1 == a2
    assert a1 != b


def test_factory_reads_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "stub")
    assert isinstance(get_embedder(), StubEmbedder)
    assert isinstance(get_embedder("stub"), StubEmbedder)


def test_factory_rejects_unknown_provider():
    with pytest.raises(ValueError):
        get_embedder("nope")
