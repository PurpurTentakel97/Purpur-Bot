from typing import Final

from fastapi import APIRouter
from fastapi import Request
from fastapi import Response
from fastapi import status

router: Final = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/twitch/online")
async def twitch_online(request: Request) -> Response:
    # Twitch EventSub sends a challenge when subscribing.
    # We need to return the challenge to confirm the subscription.

    # Twitch EventSub headers:
    # Twitch-Eventsub-Message-Type: notification | webhook_callback_verification | revocation

    message_type = request.headers.get("Twitch-Eventsub-Message-Type")

    if message_type == "webhook_callback_verification":
        body = await request.json()
        challenge = body.get("challenge")
        if challenge:
            return Response(content=challenge, media_type="text/plain")

    if message_type == "notification":
        # TODO: Handle the stream.online notification
        # For now, just return 204 No Content as we only implement the API first.
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
