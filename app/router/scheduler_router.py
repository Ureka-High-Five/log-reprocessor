from fastapi import APIRouter, Request
from app.repositories.action_log_repository import ActionLogRepository
from app.repositories.user_weight_repository import UserWeightRepository
from app.services.daily_weight_resizer import resize_weight

router = APIRouter()

@router.post("/resize-weight")
async def trigger_resize_weight(request: Request):
    mongo_client = request.app.state.mongo_client

    action_log_repo = ActionLogRepository(mongo_client)
    user_weight_repo = UserWeightRepository(mongo_client)

    await resize_weight(action_log_repo, user_weight_repo)

    return {"message": "ok"}
