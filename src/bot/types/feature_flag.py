from typing import final

from attr import dataclass


@final
@dataclass
class FeatureFlags:
    pass


DEFAULT_TWITCH_FEATURES = FeatureFlags()
DEFAULT_DISCORD_FEATURES = FeatureFlags()
