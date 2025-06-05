from fastapi import APIRouter
from .v1 import user,wallet,project,transaction

router = APIRouter(
    prefix="/api/v1"
)


router.include_router(user.router)
router.include_router(wallet.router)
router.include_router(project.router)
router.include_router(transaction.router)
