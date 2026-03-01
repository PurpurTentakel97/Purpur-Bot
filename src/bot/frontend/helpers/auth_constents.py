from twitchAPI.type import AuthScope as TwitchAuthScope

TWITCH_SCOPES = [TwitchAuthScope.USER_READ_MODERATED_CHANNELS]
TWITCH_BROADCAST_SCOPES = [
    TwitchAuthScope.CHANNEL_MANAGE_BROADCAST,
    TwitchAuthScope.CHANNEL_READ_SUBSCRIPTIONS,
]
DISCORD_SCOPES = ["identify", "email", "guilds"]
JWT_ALG = "HS256"
JWT_EXPIRY_DAYS = 7  # in days
