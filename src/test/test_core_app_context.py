import os
from pathlib import Path
from unittest.mock import patch

import pytest

from bot.core.app_context import AppContext
from bot.core.app_context import OptionalAppContextEntry
from bot.core.app_context import TwitchTokens
from bot.core.helpers.env import get_env_var_or_default


def test_optional_app_context_entry_value_or_rise() -> None:
    entry = OptionalAppContextEntry("value")
    assert entry.value_or_rise() == "value"


def test_optional_app_context_entry_value_or_rise_fail() -> None:
    entry: OptionalAppContextEntry[str] = OptionalAppContextEntry(None)
    with pytest.raises(RuntimeError, match="Value is not set"):
        entry.value_or_rise()


def test_optional_app_context_entry_value_or_default() -> None:
    entry: OptionalAppContextEntry[str] = OptionalAppContextEntry(None)
    assert entry.value_or_default("default") == "default"
    entry.set_value("value")
    assert entry.value_or_default("default") == "value"


def test_optional_app_context_entry_is_valid() -> None:
    entry: OptionalAppContextEntry[str] = OptionalAppContextEntry(None)
    assert not entry.is_valid()
    entry.set_value("value")
    assert entry.is_valid()


def test_get_env_var_or_default_success() -> None:
    with patch.dict(os.environ, {"TEST_VAR": "value"}):
        assert get_env_var_or_default("TEST_VAR", "default") == "value"


def test_get_env_var_or_default_fallback(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.dict(os.environ, {}, clear=True):
        assert get_env_var_or_default("TEST_VAR", "default") == "default"
        captured = capsys.readouterr()
        assert "Environment variable 'TEST_VAR' is not set, using default 'default'" in captured.out


def test_twitch_tokens_try_load_success() -> None:
    env = {
        "TWITCH_ACCESS_TOKEN": "access",
        "TWITCH_REFRESH_TOKEN": "refresh",
    }
    with patch.dict(os.environ, env):
        tokens = TwitchTokens.try_load_from_env()
        assert tokens is not None
        assert tokens.access_token == "access"
        assert tokens.refresh_token == "refresh"


def test_twitch_tokens_try_load_missing_access() -> None:
    env = {
        "TWITCH_REFRESH_TOKEN": "refresh",
    }
    with patch.dict(os.environ, env, clear=True):
        assert TwitchTokens.try_load_from_env() is None


def test_twitch_tokens_try_load_missing_refresh() -> None:
    env = {
        "TWITCH_ACCESS_TOKEN": "access",
    }
    with patch.dict(os.environ, env, clear=True):
        assert TwitchTokens.try_load_from_env() is None


def test_update_env_file_new_file(tmp_path: Path) -> None:
    from bot.core.types.environment_state import Environment

    env_file = tmp_path / ".env"
    updates = {"KEY1": "VAL1", "KEY2": "VAL2"}
    AppContext._update_env_file(env_file, updates, Environment.DEVELOPMENT)  # type: ignore[reportPrivateUsage]

    content = env_file.read_text(encoding="utf-8")
    assert "KEY1=VAL1\n" in content
    assert "KEY2=VAL2\n" in content


def test_update_env_file_update_existing(tmp_path: Path) -> None:
    from bot.core.types.environment_state import Environment

    env_file = tmp_path / ".env"
    env_file.write_text("KEY1=OLD1\n# Comment\nexport KEY2=OLD2\n", encoding="utf-8")

    updates = {"KEY1": "NEW1", "KEY2": "NEW2", "KEY3": "NEW3"}
    AppContext._update_env_file(env_file, updates, Environment.DEVELOPMENT)  # type: ignore[reportPrivateUsage]

    content = env_file.read_text(encoding="utf-8")
    assert "KEY1=NEW1\n" in content
    assert "# Comment\n" in content
    assert "export KEY2=NEW2\n" in content
    assert "KEY3=NEW3\n" in content
    # Ensure it didn't duplicate or mess up prefixes
    assert "KEY1=OLD1" not in content
    assert "KEY2=OLD2" not in content


def test_update_env_file_no_newline_at_end(tmp_path: Path) -> None:
    from bot.core.types.environment_state import Environment

    env_file = tmp_path / ".env"
    env_file.write_text("KEY1=VAL1", encoding="utf-8")

    updates = {"KEY2": "VAL2"}
    AppContext._update_env_file(env_file, updates, Environment.DEVELOPMENT)  # type: ignore[reportPrivateUsage]

    content = env_file.read_text(encoding="utf-8")
    assert content == "KEY1=VAL1\nKEY2=VAL2\n"


def test_update_env_file_complex(tmp_path: Path) -> None:
    from bot.core.types.environment_state import Environment

    env_file = tmp_path / ".env"
    initial_content = (
        "KEY1=VAL1\n"
        + "  KEY2=VAL2\n"
        + "export KEY3=VAL3\n"
        + "  export KEY4=VAL4\n"
        + "# Comment\n"
        + "KEY5=VAL5"  # No newline at end
    )
    env_file.write_text(initial_content, encoding="utf-8")

    updates = {
        "KEY1": "NEW1",
        "KEY2": "NEW2",
        "KEY3": "NEW3",
        "KEY4": "NEW4",
        "KEY6": "NEW6",
    }
    AppContext._update_env_file(env_file, updates, Environment.DEVELOPMENT)  # type: ignore[reportPrivateUsage]

    content = env_file.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    assert "KEY1=NEW1\n" in lines
    assert "  KEY2=NEW2\n" in lines
    assert "export KEY3=NEW3\n" in lines
    assert "  export KEY4=NEW4\n" in lines
    assert "# Comment\n" in lines
    assert "KEY5=VAL5\n" in lines  # Added newline
    assert "KEY6=NEW6\n" in lines


def test_optional_app_context_entry_value_unsafe() -> None:
    entry: OptionalAppContextEntry[str] = OptionalAppContextEntry(None)
    assert entry.value_unsafe() is None
    entry.set_value("value")
    assert entry.value_unsafe() == "value"


def test_app_context_update_twitch_tokens(tmp_path: Path) -> None:
    from bot.core.types.environment_state import Environment

    env_file = tmp_path / ".env"
    # Set the class variable to point to our temp file
    with patch.object(AppContext, "_ENV_FILE_PATH", env_file):
        ctx = AppContext(
            discord_token="d",
            discord_client_id="cid",
            discord_client_secret="cs",
            discord_redirect_uri="dr",
            twitch_client_id="c",
            twitch_credentials="cr",
            twitch_tokens=None,
            twitch_redirect_uri="r",
            environment_state=Environment.DEVELOPMENT,
            jwt_secret="j",
            twitch_subscription_callback_url=None,
            twitch_eventsub_secret="e",
            twitch_eventsub_port=8080,
            twitch_live_message_cooldown_in_seconds=120,
        )

        ctx.update_twitch_tokens("new_access", "new_refresh")

        assert ctx.twitch_tokens.is_valid()
        assert ctx.twitch_tokens.value_or_rise().access_token == "new_access"
        assert ctx.twitch_tokens.value_or_rise().refresh_token == "new_refresh"

        content = env_file.read_text(encoding="utf-8")
        assert "TWITCH_ACCESS_TOKEN=new_access\n" in content
        assert "TWITCH_REFRESH_TOKEN=new_refresh\n" in content
