from typing import Final

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

router: Final = APIRouter()


@router.get("/imprint")
async def imprint(
    request: Request,
) -> Response:
    template = Jinja2Templates(directory="src/bot/frontend/templates")
    return template.TemplateResponse(
        request=request,
        name="imprint.html",
        context={"name": "Purpur"},
    )
