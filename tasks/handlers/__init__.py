from aiogram import Router
from .create_task import router as create_task_router
from .list_tasks import router as list_tasks_router
from .edit_task import router as edit_task_router

router = Router()
router.include_router(create_task_router)
router.include_router(list_tasks_router)
router.include_router(edit_task_router)


__all__ = ["router"]
