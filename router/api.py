from fastapi import APIRouter
from .v1 import user,wallet

router = APIRouter(
    prefix="/api/v1"
)


router.include_router(user.router)
router.include_router(wallet.router)
