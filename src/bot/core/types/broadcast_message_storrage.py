from datetime import datetime

from bot.database.types.twitch_broadcast_message import TwitchBroadcastMessageDB


class BroadcastMessageStorage:
    def __init__(self, messages: list[TwitchBroadcastMessageDB]) -> None:
        self._messages: dict[int, TwitchBroadcastMessageDB] = {}
        self._timestamps: dict[int, float] = {}

        for message in messages:
            self._messages[message.id] = message
            self._timestamps[message.id] = datetime.now().timestamp()

    def add_or_update_message(self, message: TwitchBroadcastMessageDB) -> None:
        self._messages[message.id] = message
        self._timestamps[message.id] = datetime.now().timestamp() - message.interval_in_minutes * 60

    def remove_message(self, message_id: int) -> None:
        del self._messages[message_id]
        del self._timestamps[message_id]

    def get_next_messages(self) -> list[TwitchBroadcastMessageDB]:
        current_time = datetime.now().timestamp()

        messages: list[TwitchBroadcastMessageDB] = []

        for message_id, timestamp in self._timestamps.items():
            if current_time - timestamp >= self._messages[message_id].interval_in_minutes * 60:
                message = self._messages[message_id]
                if message.enabled:
                    messages.append(self._messages[message_id])
                self._timestamps[message_id] += self._messages[message_id].interval_in_minutes * 60

        return messages

    def cleanup(self) -> None:
        self._messages = {}
        self._timestamps = {}
