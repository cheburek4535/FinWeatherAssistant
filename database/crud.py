from database.models import Session, UserRequest
from Logger.my_logger import logger
def save_request(user_id: int, user_name: str, req_type: str, req_data: str, resp_data: str):
    """Сохраняет запрос пользователя в БД"""
    session = Session()
    try:
        new_request = UserRequest(
            user_id=user_id,
            user_name=user_name,
            request_type=req_type,
            request_data=req_data,
            response_data=str(resp_data)
        )

        session.add(new_request)
        session.commit()
        logger.info(f"Запрос сохранен в БД: ID={new_request.id}")
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при сохранении данных в БД{e}")
    finally:
        session.close()