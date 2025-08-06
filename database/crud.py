from pip._internal import req

from database.models import Session, UserRequest
from Logger.my_logger import logger
from datetime import datetime
def save_request(user_id: int, user_name: str, req_type: str, req_data: str, resp_data: str):
    """Сохраняет запрос пользователя в БД"""
    session = Session()
    try:
        new_request = UserRequest(
            user_id=user_id,
            user_name=user_name,
            request_type=req_type,
            request_data=req_data,
            response_data=str(resp_data),

        )

        session.add(new_request)
        session.commit()
        logger.info(f"Запрос сохранен в БД: ID={new_request.id}")
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при сохранении данных в БД{e}")
    finally:
        session.close()

def show_story(user_id):
    session = Session()
    user_story = session.query(UserRequest).filter(UserRequest.user_id == user_id).all()
    lines = []
    for req in user_story:
        time_str = req.timestamp.isoformat()[11:16] if req.timestamp else "No timestamp"

        line = f"{time_str} - {req.request_data}"
        lines.append(line)

    session.close()
    return lines

story_lines = show_story(6278046215)

#for line in story_lines:

#print(show_story(6278046215))