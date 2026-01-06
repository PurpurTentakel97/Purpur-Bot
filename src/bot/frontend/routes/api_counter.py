from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from bot.database.counter import delete_counter as delete_counter_db
from bot.database.counter import reset_counter as reset_counter_db
from bot.database.counter import save_counter as save_counter_db
from bot.frontend.helpers.auth import get_authenticated_twitch_user

router: Final = APIRouter(prefix="/api/counter", dependencies=[Depends(get_authenticated_twitch_user)])


@router.post("/create")
async def create_counter(request: Request) -> JSONResponse:
    data = await request.json()
    name = data.get("name")
    bot_id = int(data.get("bot_id"))

    result = save_counter_db(bot_id, name)

    if not result:
        return JSONResponse(status_code=400, content={"message": "Failed to create counter"})
    return JSONResponse(status_code=200, content={"message": "Counter created successfully"})


@router.post("/reset")
async def reset_counter(request: Request) -> JSONResponse:
    data = await request.json()
    name = data.get("name")
    bot_id = int(data.get("bot_id"))

    result = reset_counter_db(bot_id, name)

    if not result:
        return JSONResponse(status_code=400, content={"message": "Failed to reset counter"})
    return JSONResponse(status_code=200, content={"message": "Counter reset successfully"})


@router.post("/delete")
async def delete_counter(request: Request) -> JSONResponse:
    data = await request.json()
    name = data.get("name")
    bot_id = int(data.get("bot_id"))

    result = delete_counter_db(bot_id, name)

    if not result:
        return JSONResponse(status_code=400, content={"message": "Failed to delete counter"})
    return JSONResponse(status_code=200, content={"message": "Counter deleted successfully"})
