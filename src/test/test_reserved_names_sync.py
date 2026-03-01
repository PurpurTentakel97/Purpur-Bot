import ast
from pathlib import Path
from typing import Any
from typing import cast

from bot.core.reserved_names import RESERVED_NAMES


def test_handle_commands_reserved_sync() -> None:
    handle_commands_path = Path("src/bot/chat/handle_commands.py")
    assert handle_commands_path.exists()

    with open(handle_commands_path) as f:
        tree = ast.parse(f.read())

    found_builtin_commands: set[str] = set()

    # We are looking for 'case ["!cmd", ...]:'
    # In AST terms (Python 3.10+), this involves 'match_case' and 'MatchSequence'
    for node in ast.walk(tree):
        # The node class name is 'match_case' but its instance can be checked
        if node.__class__.__name__ == "match_case":
            node_any = cast(Any, node)
            pattern = node_any.pattern
            # Handle case ["!cmd", ...]:
            if pattern.__class__.__name__ == "MatchSequence":
                if len(pattern.patterns) > 0:
                    first_pattern = pattern.patterns[0]
                    if first_pattern.__class__.__name__ == "MatchValue":
                        value_node = first_pattern.value
                        if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
                            if value_node.value.startswith("!"):
                                cmd_name: str = value_node.value.lstrip("!")
                                found_builtin_commands.add(cmd_name)

            # Handle case "!cmd":
            if pattern.__class__.__name__ == "MatchValue":
                value_node = pattern.value
                if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
                    if value_node.value.startswith("!"):
                        cmd_name: str = value_node.value.lstrip("!")
                        found_builtin_commands.add(cmd_name)

    # Check that all found commands are reserved
    for cmd in found_builtin_commands:
        assert cmd in RESERVED_NAMES, (
            f"Command '!{cmd}' found in handle_commands.py but not in RESERVED_NAMES in src/bot/core/reserved_names.py"
        )

    # Optional: check that all reserved names are actually used (to avoid keeping stale ones)
    # However, sometimes we might reserve names for future use.
    # For now, let's just ensure we didn't forget any.
