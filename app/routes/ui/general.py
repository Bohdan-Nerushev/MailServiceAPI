from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from app.routes.ui.utils import render_template

router = APIRouter(tags=["UI General"])


@router.get(
    "/",
    response_class=HTMLResponse
)
async def home_page(request: Request):
    return render_template(
        name="index.html",
        context={"request": request}
    )
