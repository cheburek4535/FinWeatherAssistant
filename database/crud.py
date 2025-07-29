from .models import Session, UserRequest
from Logger.my_logger import logger
def save_request(user_id: int, req_type: str, req_data: str, resp_data: str):
    """Сохраняет запрос пользователя в БД"""
    session = Session()
    try:
        new_request = UserRequest(
            user_id=user_id,
            request_type=req_type,
            request_data=req_data,
            response_data=str(resp_data)
        )

        session.add(new_request)
        session.commit()

    except Exception as e:
        logger.session.rollback()