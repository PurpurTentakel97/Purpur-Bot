from bot.helpers.log import LogLevel
from bot.helpers.log import log_default


def handle_console() -> None:
    exit_command = "exit"
    log_default(LogLevel.INFO, f"Console input enabled | type '{exit_command}' to exit")
    while True:
        command = input()
        if command == exit_command:
            break
