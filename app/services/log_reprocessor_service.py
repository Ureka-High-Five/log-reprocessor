import logging
from app.enum.action_type import ActionType
from app.repositories.action_log_repository import ActionLogRepository
from app.repositories.managed_action_log_repository import ManagedActionLogRepository
from app.repositories.user_weight_repository import UserWeightRepository
from app.services.weight_strategy import convert_to_weight
from motor.motor_asyncio import AsyncIOMotorClient


async def retry_failed_logs(mongo_client: AsyncIOMotorClient):
    repo = ManagedActionLogRepository(mongo_client)
    weight_repo = UserWeightRepository(mongo_client)
    action_log_repo = ActionLogRepository(mongo_client)
    failed_logs = await repo.find_failed_logs()

    for log in failed_logs:
        try:
            weight = await calc_weight(log)
            await weight_repo.update_user_weights_from_log(log, weight)
            await repo.delete_by_id(log["_id"])
            await action_log_repo.update_status_to_success(log["_id"])

            print(f"✅ 재처리 성공: {log['_id']}")
        except Exception as e:
            logging.error(
                f"[actionlog_status_update_failed] 보상트랜잭션 실패, log_id: {log['_id']}, error: {e}"
            )


async def calc_weight(log: dict):
    action_type = ActionType[log["action"]]
    value = log["value"]
    weight = convert_to_weight(action_type, value)
    return weight
