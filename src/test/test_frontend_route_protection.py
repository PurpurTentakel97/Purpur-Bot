"""Tests to ensure protected routes enforce authentication and ownership checks."""

from collections.abc import Iterator
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.decorators import get_owned_bot
from bot.frontend.helpers.decorators import get_owned_twitch_user
from bot.frontend.types.twitch_user_info import TwitchUserInfo
from bot.main import app

OWNER_USER = TwitchUserInfo(id_="123", login="owner", display_name="Owner", profile_image_url="")
OTHER_USER = TwitchUserInfo(id_="999", login="other", display_name="Other", profile_image_url="")
OWNER_BOT = BotConfigDB(id=1, twitch_user_id="123", name="testbot", enabled=True)
OTHER_BOT = BotConfigDB(id=1, twitch_user_id="456", name="otherbot", enabled=True)


@pytest.fixture()
def unauthenticated_client() -> TestClient:
    """Client with no session — simulates a visitor who is not logged in."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def authenticated_owner_client() -> Iterator[TestClient]:
    """Client where the logged-in user owns bot 1."""
    app.dependency_overrides[get_owned_twitch_user] = lambda: OWNER_USER
    app.dependency_overrides[get_owned_bot] = lambda: OWNER_BOT
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def authenticated_non_owner_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Client where the logged-in user does NOT own bot 1."""
    from bot.core.types.result import Result
    from bot.core.types.result import ResultState

    app.dependency_overrides[get_owned_twitch_user] = lambda: OTHER_USER
    # Do NOT override get_owned_bot — let the real decorator run and raise 403
    monkeypatch.setattr(
        "bot.frontend.helpers.decorators.get_bot_core",
        MagicMock(return_value=Result(ResultState.SUCCESS, OTHER_BOT)),
    )
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Routes that MUST be protected (require login + ownership)
# ---------------------------------------------------------------------------

PROTECTED_GET_ROUTES = [
    "/dashboard/global/1",
    "/dashboard/commands/1",
    "/dashboard/alias/1",
    "/dashboard/counter/1",
    "/dashboard/quotes/1",
]


@pytest.mark.parametrize("path", PROTECTED_GET_ROUTES)
def test_protected_route_requires_login(unauthenticated_client: TestClient, path: str) -> None:
    """Unauthenticated requests to protected routes must return 401."""
    response = unauthenticated_client.get(path)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize("path", PROTECTED_GET_ROUTES)
def test_protected_route_rejects_non_owner(authenticated_non_owner_client: TestClient, path: str) -> None:
    """Requests from a user who does not own the bot must return 403."""
    response = authenticated_non_owner_client.get(path)
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.parametrize("path", PROTECTED_GET_ROUTES)
def test_protected_route_allows_owner(authenticated_owner_client: TestClient, path: str) -> None:
    """Requests from the bot owner must not be rejected with 401 or 403."""
    response = authenticated_owner_client.get(path)
    assert response.status_code not in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)


# ---------------------------------------------------------------------------
# Routes that are intentionally PUBLIC (no login required)
# ---------------------------------------------------------------------------

PUBLIC_GET_ROUTES = [
    "/view/",
    "/view/1/",
    "/view/1/commands",
    "/view/1/counter",
    "/view/1/alias",
]


@pytest.mark.parametrize("path", PUBLIC_GET_ROUTES)
def test_public_route_accessible_without_login(
    unauthenticated_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    path: str,
) -> None:
    """Public view routes must be accessible without authentication."""
    from bot.core.types.result import Result
    from bot.core.types.result import ResultState

    monkeypatch.setattr(
        "bot.frontend.helpers.decorators.get_bot_core",
        MagicMock(return_value=Result(ResultState.SUCCESS, OWNER_BOT)),
    )
    response = unauthenticated_client.get(path)
    assert response.status_code not in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
