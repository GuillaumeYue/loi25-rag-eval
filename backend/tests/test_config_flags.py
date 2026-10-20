import pytest

from app import config


def test_all_flags_default_off():
    assert config.flags() == config.Flags()
    assert set(config.flags().as_env().values()) == {False}


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "on", " On "])
def test_truthy_values(monkeypatch, value):
    monkeypatch.setenv("TOOL_GUARD", value)
    assert config.flags().tool_guard is True


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "", "2", "enabled"])
def test_everything_else_is_off(monkeypatch, value):
    monkeypatch.setenv("TOOL_GUARD", value)
    assert config.flags().tool_guard is False


def test_as_env_uses_the_environment_variable_names(monkeypatch):
    monkeypatch.setenv("ISOLATE_CONTEXT", "1")
    assert config.flags().as_env() == {
        "ENFORCE_ACCESS_CONTROL": False,
        "ISOLATE_CONTEXT": True,
        "TOOL_GUARD": False,
        "OUTPUT_FILTER": False,
    }


def test_allowed_domains(monkeypatch):
    assert config.tool_allowed_domains() == ["energie-boreale.example"]
    monkeypatch.setenv("TOOL_ALLOWED_DOMAINS", " A.example , b.example,")
    assert config.tool_allowed_domains() == ["a.example", "b.example"]
