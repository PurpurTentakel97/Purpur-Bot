import asyncio
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
from typing import Self

from twitchAPI.eventsub.webhook import EventSubWebhook
from twitchAPI.helper import first
from twitchAPI.object.eventsub import StreamOnlineEvent

from bot.core.app_context import APP_CONTEXT
from bot.core.types.twitch_online_message import TwitchOnlineMessageLight
from bot.helpers.log import LogLevel, log_default
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

        callback_url = APP_CONTEXT.twitch_subscription_callback_url.value_or_rise()
        if callback_url.endswith("/callback"):
            callback_url = callback_url[: -len("/callback")]
        if callback_url.endswith("/"):
            callback_url = callback_url[:-1]

        log_twitch(LogLevel.INFO, f"Starting Twitch Event Hub with callback URL: {callback_url}")

        try:
            event_sub = EventSubWebhook(
                callback_url=callback_url,
                port=APP_CONTEXT.twitch_eventsub_port.value(),
                twitch=PROGRAMM_PARTS.twitch.client,
                callback_loop=asyncio.get_running_loop(),
            )
        except RuntimeError as e:
            if "HTTPS is required" in str(e):
                log_exception(e, LogProgram.Twitch, "Failed to start Twitch Event Hub")
            raise e

        event_sub.secret = APP_CONTEXT.twitch_eventsub_secret.value_or_rise()
        event_sub.unsubscribe_on_stop = False
        # The library's EventSubWebhook expects its own /callback endpoint
        event_sub.start()

        log_twitch(LogLevel.INFO, "Twitch Event Hub started successfully.")

        return cls(event_sub)

    async def terminate(self) -> None:
        await self._webhook.stop()
        log_twitch(LogLevel.INFO, "Twitch Event Hub terminated successfully.")

    async def subscribe(self, broadcaster_id: str) -> None:
        if broadcaster_id in self._sub_ids_by_broadcaster:
            log_twitch(LogLevel.INFO, f"Already subscribed to {broadcaster_id}. Skipping.")
            return

        try:
            sub_id = await self._webhook.listen_stream_online(
                broadcaster_user_id=broadcaster_id, callback=self._on_stream_online
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

    @staticmethod
    async def get_current_subscriptions() -> list[dict[str, Any]]:
        """
        Fetches all current EventSub subscriptions from Twitch for this App ID.
        """
        from bot.core.types.programm_parts import PROGRAMM_PARTS

        if TYPE_CHECKING:
            assert PROGRAMM_PARTS.twitch

        subscriptions: list[dict[str, Any]] = []
        try:
            # get_eventsub_subscriptions returns a Coroutine that resolves to GetEventSubSubscriptionResult
            # which has a .data attribute containing the list of subscriptions
            result: Any = await PROGRAMM_PARTS.twitch.client.get_eventsub_subscriptions()
            data: Any = getattr(result, "data", [])
            for sub in data:
                subscriptions.append(
                    {
                        "id": str(getattr(sub, "id", "")),
                        "type": str(getattr(sub, "type", "")),
                        "status": str(getattr(sub, "status", "")),
                        "condition": dict(getattr(sub, "condition", {})),
                    }
                )
        except Exception as e:
            log_exception(e, LogProgram.Twitch, "Failed to fetch current subscriptions")

        return subscriptions

    async def sync_subscriptions(self) -> None:
        """
        Fetches active subscriptions from Twitch and updates the internal mapping.
        """

        subscriptions = await self.get_current_subscriptions()
        for sub in subscriptions:
            # We only support stream.online events for now
            if sub["type"] != "stream.online":
                continue

            # The broadcaster ID is stored in the 'condition' dictionary
            broadcaster_id = sub["condition"].get("broadcaster_user_id")
            log_default(LogLevel.DEBUG, f"Found subscription: {sub} | Broadcaster ID: {broadcaster_id}")
            if broadcaster_id and sub["status"] == "enabled":
                self._sub_ids_by_broadcaster[broadcaster_id] = sub["id"]
                # We need to manually add the callback to the library's internal mapping
                # so that it knows how to handle incoming events for this existing subscription.
                # _add_callback is a method of EventSubBase (parent of EventSubWebhook)
                if hasattr(self._webhook, "_add_callback"):
                    self._webhook._add_callback(sub["id"], self._on_stream_online, StreamOnlineEvent)  # type: ignore
                    # Mark the callback as active so it's not discarded
                    callbacks: dict[str, Any] = getattr(self._webhook, "_callbacks", {})
                    if sub["id"] in callbacks:
                        callbacks[sub["id"]]["active"] = True

                log_twitch(LogLevel.INFO, f"Synced subscription for {broadcaster_id} (ID: {sub['id']})")

    async def _on_stream_online(self, event: StreamOnlineEvent) -> None:
        asyncio.create_task(self._on_stream_online_task(event))

    async def _on_stream_online_task(self, event: StreamOnlineEvent) -> None:
        from bot.core.types.programm_parts import PROGRAMM_PARTS

        if TYPE_CHECKING:
            assert PROGRAMM_PARTS.twitch

        broadcaster_id = event.event.broadcaster_user_id
        broadcaster_name = event.event.broadcaster_user_name

        stream_title = "No Title"
        category_name = "No Category"

        try:
            if PROGRAMM_PARTS.twitch:
                channel_infos = await PROGRAMM_PARTS.twitch.client.get_channel_information(broadcaster_id)
                if channel_infos:
                    channel_info = channel_infos[0]
                    stream_title = channel_info.title
                    category_name = channel_info.game_name
        except Exception as e:
            log_exception(e, LogProgram.Twitch, f"Failed to fetch channel info for {broadcaster_id}")

        message_light = TwitchOnlineMessageLight(
            broadcaster_id=broadcaster_id,
            broadcaster_name=broadcaster_name,
            channel_url=f"https://twitch.tv/{event.event.broadcaster_user_login}",
            stream_title=stream_title,
            category_name=category_name,
        )

        log_twitch(LogLevel.DEBUG, f"Received stream online event for {broadcaster_id}. | {message_light}")

        from bot.core.twitch_event_hub_management import send_twitch_event_hub_entry

        await send_twitch_event_hub_entry(broadcaster_id, message_light)
