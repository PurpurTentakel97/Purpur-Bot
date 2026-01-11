import pytest

from bot.core.helpers.env import get_env_var_or_default
from bot.core.helpers.env import get_env_var_or_rise
from bot.core.helpers.string import has_whitespace
from bot.core.helpers.string import identifier_for_db
from bot.core.helpers.string import name_for_db
from bot.core.helpers.string import strip_for_db


# env
def test_get_env_var_or_default_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_VAR", "  some value  ")
    assert get_env_var_or_default("TEST_VAR", "default") == "some value"


def test_get_env_var_or_default_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TEST_VAR", raising=False)
    assert get_env_var_or_default("TEST_VAR", "default") == "default"


def test_get_env_var_or_default_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_VAR", "   ")
    assert get_env_var_or_default("TEST_VAR", "default") == "default"


def test_get_env_var_or_rise_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_VAR", "  some value  ")
    assert get_env_var_or_rise("TEST_VAR") == "some value"


def test_get_env_var_or_rise_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TEST_VAR", raising=False)
    with pytest.raises(RuntimeError, match="Environment variable 'TEST_VAR' is not set"):
        get_env_var_or_rise("TEST_VAR")


def test_get_env_var_or_rise_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_VAR", "   ")
    with pytest.raises(RuntimeError, match="Environment variable 'TEST_VAR' is not set"):
        get_env_var_or_rise("TEST_VAR")


# string
def test_identifier_for_db() -> None:
    assert identifier_for_db("  TestName  ") == "testname"
    assert identifier_for_db("ANOTHER_TEST") == "another_test"
    assert identifier_for_db("  already_lowered  ") == "already_lowered"


def test_strip_for_db() -> None:
    assert strip_for_db("  some_id  ") == "some_id"
    assert strip_for_db("\tother_id\n") == "other_id"


def test_name_for_db() -> None:
    assert name_for_db("  john doe  ") == "John Doe"
    assert name_for_db("ALICE SMITH") == "Alice Smith"


def test_has_whitespace() -> None:
    assert has_whitespace("no_whitespace") is False
    assert has_whitespace("has whitespace") is True
    assert has_whitespace("has\twhitespace") is True
    assert has_whitespace("has\nwhitespace") is True
    assert has_whitespace("  ") is True
    assert has_whitespace("") is False
