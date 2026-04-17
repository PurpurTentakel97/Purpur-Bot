from unittest.mock import MagicMock

from bot.chat.types.user_ref import DiscordUserRef
from bot.chat.types.user_ref import TwitchUserRef
from bot.chat.types.user_ref import UserRef
from bot.core.commands import MENTION_MENTION
from bot.core.commands import OWNER_MENTION
from bot.core.commands import SENDER_MENTION
from bot.core.commands import _replace_user_mentions  # type: ignore[reportPrivateUsage]


def _make_msg(text: str, sender: UserRef, owner: UserRef, mentions: list[UserRef]) -> MagicMock:
    msg = MagicMock()
    msg.text = text
    msg.sender = sender
    msg.owner = owner
    msg.mentions = mentions
    return msg


# --- {@sender} ---


def test_sender_replaced_twitch() -> None:
    sender = TwitchUserRef("streamer")
    msg = _make_msg(f"Hello {SENDER_MENTION}!", sender, TwitchUserRef("owner"), [])
    result = _replace_user_mentions(msg)
    assert result == "Hello @streamer!"


def test_sender_replaced_discord() -> None:
    sender = DiscordUserRef(123456)
    msg = _make_msg(f"Hello {SENDER_MENTION}!", sender, DiscordUserRef(999), [])
    result = _replace_user_mentions(msg)
    assert result == "Hello <@123456>!"


# --- {@owner} ---


def test_owner_replaced_twitch() -> None:
    owner = TwitchUserRef("channelowner")
    msg = _make_msg(f"Owner is {OWNER_MENTION}.", TwitchUserRef("viewer"), owner, [])
    result = _replace_user_mentions(msg)
    assert result == "Owner is @channelowner."


def test_owner_replaced_discord() -> None:
    owner = DiscordUserRef(777)
    msg = _make_msg(f"Owner is {OWNER_MENTION}.", DiscordUserRef(1), owner, [])
    result = _replace_user_mentions(msg)
    assert result == "Owner is <@777>."


# --- {@mention} ---


def test_mention_single_twitch() -> None:
    msg = _make_msg(f"Hi {MENTION_MENTION}!", TwitchUserRef("sender"), TwitchUserRef("owner"), [TwitchUserRef("alice")])
    result = _replace_user_mentions(msg)
    assert result == "Hi @alice!"


def test_mention_single_discord() -> None:
    msg = _make_msg(f"Hi {MENTION_MENTION}!", DiscordUserRef(1), DiscordUserRef(2), [DiscordUserRef(42)])
    result = _replace_user_mentions(msg)
    assert result == "Hi <@42>!"


def test_mention_multiple_twitch() -> None:
    mentions: list[UserRef] = [TwitchUserRef("alice"), TwitchUserRef("bob"), TwitchUserRef("carol")]
    msg = _make_msg(f"Shoutout to {MENTION_MENTION}!", TwitchUserRef("sender"), TwitchUserRef("owner"), mentions)
    result = _replace_user_mentions(msg)
    assert result == "Shoutout to @alice @bob @carol!"


def test_mention_multiple_discord() -> None:
    mentions: list[UserRef] = [DiscordUserRef(10), DiscordUserRef(20), DiscordUserRef(30)]
    msg = _make_msg(f"Shoutout to {MENTION_MENTION}!", DiscordUserRef(1), DiscordUserRef(2), mentions)
    result = _replace_user_mentions(msg)
    assert result == "Shoutout to <@10> <@20> <@30>!"


def test_mention_no_mentions_shows_fallback() -> None:
    msg = _make_msg(f"Hi {MENTION_MENTION}!", TwitchUserRef("sender"), TwitchUserRef("owner"), [])
    result = _replace_user_mentions(msg)
    assert result == "Hi [no mentions found]!"


# --- multiple tags in one message ---


def test_all_tags_replaced_twitch() -> None:
    text = f"{SENDER_MENTION} mentioned {MENTION_MENTION} and owner is {OWNER_MENTION}"
    msg = _make_msg(text, TwitchUserRef("sender"), TwitchUserRef("owner"), [TwitchUserRef("alice")])
    result = _replace_user_mentions(msg)
    assert result == "@sender mentioned @alice and owner is @owner"


def test_all_tags_replaced_discord() -> None:
    text = f"{SENDER_MENTION} mentioned {MENTION_MENTION} and owner is {OWNER_MENTION}"
    msg = _make_msg(text, DiscordUserRef(1), DiscordUserRef(2), [DiscordUserRef(3)])
    result = _replace_user_mentions(msg)
    assert result == "<@1> mentioned <@3> and owner is <@2>"


# --- no tags in message ---


def test_no_tags_returns_original_text() -> None:
    msg = _make_msg("Hello world!", TwitchUserRef("sender"), TwitchUserRef("owner"), [])
    result = _replace_user_mentions(msg)
    assert result == "Hello world!"


# --- mixed Twitch/Discord (cross-platform safety) ---


def test_twitch_message_discord_owner() -> None:
    """Sender is Twitch user, owner is Discord user (edge case)."""
    msg = _make_msg(
        f"{SENDER_MENTION} / {OWNER_MENTION}",
        TwitchUserRef("twitchsender"),
        DiscordUserRef(999),
        [],
    )
    result = _replace_user_mentions(msg)
    assert result == "@twitchsender / <@999>"
