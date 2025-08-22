

from database.models import Session, UserRequest, DailyConfig
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



def save_daily_config(user_id: int, user_name: str, chat_id: int, daily_type:str, city: str, valute: str, daily_schedule:str):
    session = Session()

    try:
        new_config = DailyConfig(
            user_id=user_id,
            user_name=user_name,
            chat_id=chat_id,
            daily_type=daily_type,
            daily_city=city,
            daily_valute=valute,
            daily_schedule=daily_schedule
        )

        session.add(new_config)
        session.commit()
        logger.info(f"Конфигурация рассылки сохранена в БД: ID={new_config.id}")

    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка сохранения конфигурации в БД: {e}")

    finally:
        session.close()



#story_lines = show_story(6278046215)

#for line in story_lines:

#print(show_story(6278046215))

#save_daily_config(123456789, "TEST", "test_type", "Тесто город", "Тесто валюта", "test_schedule")