import logging

from app.enum.action_type import ActionType
from app.repositories.action_log_repository import ActionLogRepository
from app.repositories.managed_action_log_repository import ManagedActionLogRepository
from app.repositories.user_weight_repository import UserWeightRepository
from app.services.weight_strategy import convert_to_weight
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

async def retry_failed_logs(mongo_client: AsyncIOMotorClient):
    managed_repo = ManagedActionLogRepository(mongo_client)
    weight_repo = UserWeightRepository(mongo_client)
    action_log_repo = ActionLogRepository(mongo_client)

    try:
        raise RuntimeError("야호!")
        failed_logs = await managed_repo.find_failed_logs()
    except Exception as e:
            logger.error(
                f"[actionlog_status_update_failed] 보상트랜잭션 실패, error: {e}"
            )
            return

    for log in failed_logs:

        ## action 로그를 확인하여 이미 성공적으로 처리된 로그는 건너뛰기 (중복 가중치 업데이트 방지)
        try:
            status = await action_log_repo.get_status_by_id(log["_id"])

            if status == "SUCCESS":
                await managed_repo.delete_by_id(log["_id"]) # 이미 성공적으로 처리된 로그는 삭제
                print(f"❗ 이미 가중치가 업데이트된 로그입니다: {log['_id']}")
                continue
        except Exception as e:
            logger.error(
                f"[actionlog_status_update_failed] 보상트랜잭션 실패, log_id: {log['_id']}, error: {e}"
            )
            continue

        try:
            weight = await calc_weight(log)
            await weight_repo.update_user_weights_from_log(log, weight)
        except Exception as e:
            logger.error(
                f"[actionlog_status_update_failed] 보상트랜잭션 실패, log_id: {log['_id']}, error: {e}"
            )
            continue

        try:
            await managed_repo.delete_by_id(log["_id"])
        except Exception as e:
            logger.error(
                f"[actionlog_status_update_failed] 보상트랜잭션 실패, log_id: {log['_id']}, error: {e}"
            )
            await weight_repo.decrease_user_weights_from_log(log, weight) 
            continue

        try:
            await action_log_repo.update_status_to_success(log["_id"])
        except Exception as e:
            logger.error(
                f"[actionlog_status_update_failed] 보상트랜잭션 실패, log_id: {log['_id']}, error: {e}"
            )
            await weight_repo.decrease_user_weights_from_log(log, weight) 
            continue


        print(f"✅ 재처리 성공: {log['_id']}")



async def calc_weight(log: dict):
    action_type = ActionType[log["action"]]
    value = log["value"]
    weight = convert_to_weight(action_type, value)
    return weight
