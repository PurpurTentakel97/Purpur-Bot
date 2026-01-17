from http import HTTPStatus

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from starlette.requests import Request

from bot.core.alias_dict import add_alias as add_alias_core
from bot.core.alias_dict import delete_alias as delete_alias_core
from bot.core.alias_dict import edit_dict_alias as edit_dict_alias_core
from bot.core.alias_dict import edit_dict_explanation as edit_dict_explanation_core
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.cast import to_int_or_raise

router = APIRouter(prefix="/api/alias", dependencies=[Depends(get_authenticated_twitch_user)])


@router.post("/create")
async def create_alias(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))
        alias = data.get("alias")
        explanation = data.get("explanation")

        result = add_alias_core(bot_id, alias, explanation)
        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Failed to add alias | reason: {result.state.name}"},
            )
        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Alias added successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/update/alias")
async def update_alias(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))
        alias = data.get("alias")
        new_alias = data.get("new_alias")

        result = edit_dict_alias_core(bot_id, alias, new_alias)
        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Failed to edit alias | reason: {result.state.name}"},
            )
        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Alias edited successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/update/explanation")
async def update_explanation(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))
        alias = data.get("alias")
        new_explanation = data.get("new_explanation")

        result = edit_dict_explanation_core(bot_id, alias, new_explanation)
        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Failed to edit explanation | reason: {result.state.name}"},
            )
        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Explanation edited successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/delete")
async def delete_alias(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))
        alias = data.get("alias")

        result = delete_alias_core(bot_id, alias)
        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Failed to delete alias | reason: {result.state.name}"},
            )
        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Alias deleted successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})
