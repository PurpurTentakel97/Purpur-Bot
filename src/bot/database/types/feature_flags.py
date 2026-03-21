from pydantic import BaseModel


class FeatureFlagsDB(BaseModel):
    id: int
    bot_id: int
    can_commands: bool
    can_alias: bool
    can_broadcast: bool
    can_twitch_live: bool
    can_quotes: bool


class TwitchFeatureFlagsDB(FeatureFlagsDB):
    channel_name: str


class DiscordFeatureFlagsDB(FeatureFlagsDB):
    server_id: int
