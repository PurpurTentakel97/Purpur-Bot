from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.frontend.helpers.route_utils import get_templates

router: Final = APIRouter()


@router.get("/login")
async def login(request: Request, templates: Annotated[Jinja2Templates, Depends(get_templates)]) -> Response:
    return templates.TemplateResponse(request=request, name="login.html", context={})
