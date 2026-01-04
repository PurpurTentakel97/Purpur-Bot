from pydantic import BaseModel


class TwitchSessionCookie(BaseModel):
    user_id: str
    login: str
    display_name: str
    profile_image_url: str
    exp: int
    iat: int
