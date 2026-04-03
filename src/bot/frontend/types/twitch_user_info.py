from pydantic import BaseModel


class TwitchUserInfo(BaseModel):
    id_: str
    login: str
    display_name: str
    profile_image_url: str
