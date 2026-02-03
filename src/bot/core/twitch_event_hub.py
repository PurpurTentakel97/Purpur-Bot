from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
from typing import Self

from twitchAPI.eventsub.webhook import EventSubWebhook
from twitchAPI.helper import first

from bot.core.app_context import APP_CONTEXT
from bot.helpers.log import LogLevel
from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception
from bot.helpers.log import log_twitch


class TwitchEventHub:
    def __init__(self, webhook: EventSubWebhook) -> None:
        self._webhook: EventSubWebhook = webhook
        self._sub_ids_by_broadcaster: dict[str, str] = {}

    @classmethod
    async def get_broadcaster_id(cls, channel_name: str) -> Optional[str]:
        from bot.core.types.programm_parts import PROGRAMM_PARTS

        if TYPE_CHECKING:
            assert PROGRAMM_PARTS.twitch
        if not PROGRAMM_PARTS.twitch:
            raise ValueError("Twitch client must be initialized")

        user = await first(PROGRAMM_PARTS.twitch.client.get_users(logins=[channel_name]))
        if not user:
            return None

        return user.id

    @classmethod
    def create(cls) -> Optional[Self]:
        from bot.core.types.programm_parts import PROGRAMM_PARTS

        if TYPE_CHECKING:
            assert PROGRAMM_PARTS.twitch
        if (
            not APP_CONTEXT.twitch_subscription_callback_url.is_valid()
            or not APP_CONTEXT.twitch_eventsub_secret.is_valid()
        ):
            log_twitch(
                LogLevel.WARNING,
                "Twitch subscription callback URL and EventSub secret must be provided to start the Event Hub. "
                + "Event Hub will not be started.",
            )
            return None

        if not PROGRAMM_PARTS.twitch:
            raise ValueError("Twitch client must be initialized")

        if not APP_CONTEXT.twitch_subscription_callback_url.value_or_rise().startswith("https://"):
            log_twitch(LogLevel.ERROR, "Twitch subscription callback URL must be HTTPS.")
            return None

        try:
            event_sub = EventSubWebhook(
                callback_url=APP_CONTEXT.twitch_subscription_callback_url.value_or_rise(),
                port=APP_CONTEXT.twitch_eventsub_port.value(),
                twitch=PROGRAMM_PARTS.twitch.client,
            )
        except RuntimeError as e:
            if "HTTPS is required" in str(e):
                log_exception(e, LogProgram.Twitch, "Failed to start Twitch Event Hub")
            raise e

        event_sub.secret = APP_CONTEXT.twitch_eventsub_secret.value_or_rise()
        # The library's EventSubWebhook expects its own /callback endpoint
        event_sub.start()

        log_twitch(LogLevel.INFO, "Twitch Event Hub started successfully.")

        return cls(event_sub)

    async def terminate(self) -> None:
        await self._webhook.stop()
        log_twitch(LogLevel.INFO, "Twitch Event Hub terminated successfully.")

    async def subscribe(self, broadcaster_id: str) -> None:
        async def _on_stream_online(event: Any) -> None:
            log_twitch(LogLevel.DEBUG, f"Received stream online event for {broadcaster_id}. | {event}")

        if broadcaster_id in self._sub_ids_by_broadcaster:
            log_twitch(LogLevel.INFO, f"Already subscribed to {broadcaster_id}. Skipping.")
            return

        try:
            sub_id = await self._webhook.listen_stream_online(
                broadcaster_user_id=broadcaster_id, callback=_on_stream_online
            )
            self._sub_ids_by_broadcaster[broadcaster_id] = sub_id
            log_twitch(LogLevel.INFO, f"Subscribed to {broadcaster_id} (Subscription ID: {sub_id}).")
        except Exception as e:
            log_exception(e, LogProgram.Twitch, f"Failed to subscribe to {broadcaster_id}")

    async def unsubscribe(self, broadcaster_id: str) -> None:
        if broadcaster_id not in self._sub_ids_by_broadcaster:
            log_twitch(LogLevel.INFO, f"Not subscribed to {broadcaster_id} while unsubscribe. Skipping.")
            return

        try:
            sub_id = self._sub_ids_by_broadcaster[broadcaster_id]
            await self._webhook.unsubscribe_topic(sub_id)
            del self._sub_ids_by_broadcaster[broadcaster_id]
            log_twitch(LogLevel.INFO, f"Unsubscribed from {broadcaster_id} (Subscription ID: {sub_id}).")
        except Exception as e:
            log_exception(e, LogProgram.Twitch, f"Failed to unsubscribe from {broadcaster_id}")
