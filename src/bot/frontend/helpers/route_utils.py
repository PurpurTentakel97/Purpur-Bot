from functools import lru_cache
from pathlib import Path

from starlette.templating import Jinja2Templates


@lru_cache
def get_templates() -> Jinja2Templates:
    path = Path(__file__).parent.parent / "templates"

    if not path.exists():
        raise FileNotFoundError(f"Templates directory not found: {path}")

    return Jinja2Templates(directory=path)
