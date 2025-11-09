import asyncio
from typing import Final


class SharedState:
    def __init__(self):
        self.lock = asyncio.Lock()


SHARED_STATE: Final = SharedState()
