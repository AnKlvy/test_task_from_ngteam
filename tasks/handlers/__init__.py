from aiogram import Router
from .create_task import router as create_task_router


router = Router()
router.include_router(create_task_router)


__all__ = ["router"]
