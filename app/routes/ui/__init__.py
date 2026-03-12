from fastapi import APIRouter
from app.routes.ui.auth import router as auth_router
from app.routes.ui.mail import router as mail_router
from app.routes.ui.system import router as system_router
from app.routes.ui.general import router as general_router

router = APIRouter(
    prefix="/ui",
    tags=["UI"]
)

router.include_router(general_router)
router.include_router(auth_router)
router.include_router(mail_router)
router.include_router(system_router)
