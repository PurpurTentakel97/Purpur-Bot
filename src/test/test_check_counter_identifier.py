from bot.core.helpers.string import check_counter_identifier
from bot.core.types.result import ResultState


def test_valid_name_returns_success() -> None:
    result = check_counter_identifier("deaths")
    assert result.state == ResultState.SUCCESS
    assert result.value == "deaths"


def test_valid_name_is_lowercased() -> None:
    result = check_counter_identifier("Deaths")
    assert result.state == ResultState.SUCCESS
    assert result.value == "deaths"


def test_valid_name_with_numbers_returns_success() -> None:
    result = check_counter_identifier("deaths2")
    assert result.state == ResultState.SUCCESS
    assert result.value == "deaths2"


def test_name_starting_with_at_returns_reserved_name() -> None:
    result = check_counter_identifier("@sender")
    assert result.state == ResultState.RESERVED_NAME
    assert result.value is None


def test_name_only_at_returns_reserved_name() -> None:
    result = check_counter_identifier("@")
    assert result.state == ResultState.RESERVED_NAME
    assert result.value is None


def test_empty_name_returns_empty_name_error() -> None:
    result = check_counter_identifier("")
    assert result.state == ResultState.EMPTY_NAME
    assert result.value is None


def test_whitespace_only_returns_empty_name_error() -> None:
    result = check_counter_identifier("   ")
    assert result.state == ResultState.EMPTY_NAME
    assert result.value is None


def test_name_with_whitespace_returns_whitespace_error() -> None:
    result = check_counter_identifier("my counter")
    assert result.state == ResultState.WHITESPACE_ERROR
    assert result.value is None


def test_reserved_name_returns_reserved_name_error() -> None:
    result = check_counter_identifier("counter")
    assert result.state == ResultState.RESERVED_NAME
    assert result.value is None


def test_name_with_leading_whitespace_is_stripped() -> None:
    result = check_counter_identifier("  deaths  ")
    assert result.state == ResultState.SUCCESS
    assert result.value == "deaths"


def test_name_not_starting_with_at_is_valid() -> None:
    result = check_counter_identifier("sender")
    assert result.state == ResultState.SUCCESS
    assert result.value == "sender"
