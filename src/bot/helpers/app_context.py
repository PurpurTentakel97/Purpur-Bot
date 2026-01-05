import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import ClassVar
from typing import Final
from typing import NamedTuple
from typing import Optional
from typing import Self
from typing import final

from dotenv import load_dotenv

from bot.helpers.log import LogLevel
from bot.helpers.log import log_default
from bot.types.environment_state import Environment


def _get_env_var_or_default[T](key: str, default: T) -> T | str:
    value = os.getenv(key)
    if value is None or not value.strip():
        log_default(LogLevel.INFO, f"Environment variable '{key}' is not set, using default '{default}'")
        return default

    return value.strip()


def _get_env_var_or_rise(key: str) -> str:
    value = os.getenv(key)
    if value is None or not value.strip():
        raise RuntimeError(f"Environment variable '{key}' is not set")
    return value.strip()


@final
class TwitchTokens(NamedTuple):
    access_token: str
    refresh_token: str

    @classmethod
    def try_load(cls) -> Optional[Self]:
        access_token = _get_env_var_or_default("TWITCH_ACCESS_TOKEN", None)
        refresh_token = _get_env_var_or_default("TWITCH_REFRESH_TOKEN", None)

        if access_token is None or refresh_token is None:
            return None
        return cls(access_token, refresh_token)


@final
class AppContextEntry[T]:
    def __init__(self, value: T) -> None:
        self._value: T = value

    def value(self) -> T:
        return self._value

    def set_value(self, value: T) -> None:
        self._value = value


@final
class OptionalAppContextEntry[T]:
    def __init__(self, value: Optional[T]) -> None:
        self._value: Optional[T] = value

    def value_unsafe(self) -> Optional[T]:
        return self._value

    def value_or_rise(self) -> T:
        if self._value is None:
            raise RuntimeError("Value is not set")
        return self._value

    def value_or_default(self, default: T) -> T:
        if self._value is None:
            return default
        return self._value

    def set_value(self, value: T) -> None:
        self._value = value

    def is_valid(self) -> bool:
        return self._value is not None


@final
class AppContext:
    _ENV_FILE_PATH: ClassVar = Path(os.getcwd()) / ".env"

    def __init__(
        self,
        discord_token: Optional[str],
        discord_client_id: Optional[str],
        discord_client_secret: Optional[str],
        discord_redirect_uri: str,
        twitch_client_id: Optional[str],
        twitch_credentials: Optional[str],
        twitch_tokens: Optional[TwitchTokens],
        twitch_redirect_uri: str,
        environment_state: Environment,
        jwt_secret: str,
    ) -> None:
        self.discord_token: OptionalAppContextEntry[str] = OptionalAppContextEntry(discord_token)
        self.discord_client_id: OptionalAppContextEntry[str] = OptionalAppContextEntry(discord_client_id)
        self.discord_client_secret: OptionalAppContextEntry[str] = OptionalAppContextEntry(discord_client_secret)
        self.discord_redirect_uri: AppContextEntry[str] = AppContextEntry(discord_redirect_uri)
        self.twitch_client_id: OptionalAppContextEntry[str] = OptionalAppContextEntry(twitch_client_id)
        self.twitch_credentials: OptionalAppContextEntry[str] = OptionalAppContextEntry(twitch_credentials)
        self.twitch_tokens: OptionalAppContextEntry[TwitchTokens] = OptionalAppContextEntry(twitch_tokens)
        self.twitch_redirect_uri: AppContextEntry[str] = AppContextEntry(twitch_redirect_uri)
        self.environment_state: AppContextEntry[Environment] = AppContextEntry(environment_state)
        self.jwt_secret: AppContextEntry[str] = AppContextEntry(jwt_secret)

    def update_twitch_tokens(self, new_access_token: str, new_refresh_token: str) -> None:
        self.twitch_tokens.set_value(TwitchTokens(new_access_token, new_refresh_token))
        self._update_env_file(
            self._ENV_FILE_PATH,
            {"TWITCH_ACCESS_TOKEN": new_access_token, "TWITCH_REFRESH_TOKEN": new_refresh_token},
        )

    @classmethod
    def _update_env_file(cls, path: Path, updates: dict[str, str]) -> None:
        try:
            original = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            original = ""

        lines: Final = original.splitlines(keepends=True)
        found: Final = dict.fromkeys(updates, False)
        new_lines: Final[list[str]] = []

        for line in lines:
            stripped = line.lstrip()

            for key, value in updates.items():
                if stripped.startswith(f"{key}=") or stripped.startswith(f"export {key}="):
                    leading_ws = line[: len(line) - len(stripped)]
                    export_prefix = "export " if stripped.startswith("export ") else ""
                    new_line = "\n" if stripped.endswith(("\r\n", "\n")) else ""
                    new_lines.append(f"{leading_ws}{export_prefix}{key}={value}{new_line}")
                    found[key] = True
                    break
            else:
                new_lines.append(line)

        if new_lines and not new_lines[-1].endswith(("\r\n", "\n")):
            new_lines[-1] = new_lines[-1] + "\n"
        for key, value in updates.items():
            if not found[key]:
                new_lines.append(f"{key}={value}\n")

        new_content = "".join(new_lines)

        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, dir=path.parent) as tmp_file:
            tmp_file.write(new_content)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
            temp_path = tmp_file.name
        os.replace(temp_path, path)


load_dotenv()
APP_CONTEXT = AppContext(
    discord_token=_get_env_var_or_default("DISCORD_TOKEN", None),
    discord_client_id=_get_env_var_or_default("DISCORD_CLIENT_ID", None),
    discord_client_secret=_get_env_var_or_default("DISCORD_CLIENT_SECRET", None),
    discord_redirect_uri=_get_env_var_or_default("DISCORD_REDIRECT_URI", "http://localhost:8000/auth/discord/callback"),
    twitch_client_id=_get_env_var_or_default("TWITCH_CLIENT_ID", None),
    twitch_credentials=_get_env_var_or_default("TWITCH_CREDENTIALS", None),
    twitch_tokens=TwitchTokens.try_load(),
    twitch_redirect_uri=_get_env_var_or_default("TWITCH_REDIRECT_URI", "http://localhost:8000/auth/twitch/callback"),
    environment_state=Environment.from_string(_get_env_var_or_default("ENVIRONMENT_STATE", "production")),
    jwt_secret=_get_env_var_or_rise("JWT_SECRET"),
)
