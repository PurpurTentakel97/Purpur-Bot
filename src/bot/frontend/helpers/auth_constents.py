from twitchAPI.type import AuthScope as TwitchAuthScope

TWITCH_SCOPES = [TwitchAuthScope.USER_READ_MODERATED_CHANNELS]
JWT_ALG = "HS256"
JWT_EXPIRY_DAYS = 7  # in days
