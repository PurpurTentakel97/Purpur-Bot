from typing import Final, Annotated

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.frontend.helpers.route_utils import get_templates

router: Final = APIRouter()


@router.get("/login")
async def login(request: Request, template: Annotated[Jinja2Templates, Depends(get_templates)]) -> Response:
    return template.TemplateResponse(request=request, name="login.html", context={})
