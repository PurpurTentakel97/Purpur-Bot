from bot.database.database import DatabaseGetData
from bot.database.database import DatabaseSaveData
from bot.database.database import DatabaseUpdateData
from bot.types.database_result import DatabaseResult
from bot.types.programm_parts import PROGRAMM_PARTS

TABLE_NAME_TWITCH = "twitch_auth"


def save_or_update_twitch_tokens(
    twitch_id: str, access_token: str, refresh_token: str, expires_at: int
) -> DatabaseResult:
    get_result = PROGRAMM_PARTS.database.get_single(
        DatabaseGetData(table_name=TABLE_NAME_TWITCH, keys=["expires_at"], where={"twitch_id": twitch_id}), {}
    )

    if get_result.result.success:
        return PROGRAMM_PARTS.database.update(
            DatabaseUpdateData(
                table_name=TABLE_NAME_TWITCH,
                data={"access_token": access_token, "refresh_token": refresh_token, "expires_at": expires_at},
                where={"twitch_id": twitch_id},
            )
        )

    return PROGRAMM_PARTS.database.save(
        DatabaseSaveData(
            table_name=TABLE_NAME_TWITCH,
            data={
                "twitch_id": twitch_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
            },
        )
    )
