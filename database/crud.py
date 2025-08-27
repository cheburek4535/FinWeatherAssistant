from cffi.model import char_array_type
from pycparser.c_ast import Return

from database.models import Session, UserRequest, DailyConfig, DailyMode, Users
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


def get_daily_config(user_id: str, time: str):
   session = Session()
   try:
       config = session.query(DailyConfig).filter(DailyConfig.user_id == user_id, DailyConfig.daily_schedule.contains(time)).order_by(DailyConfig.id.desc()).first()

       dtype = config.daily_type
       chat_id = config.chat_id
       city = config.daily_city
       valute = config.daily_valute


       return dtype, chat_id, city, valute
   except Exception as e:
       session.rollback()
       logger.error(f"Ошибка получения конфига: {e}")
   finally:
       session.close()

def get_daily_config_without_time(user_id: int):
    session = Session()
    try:
        config = session.query(DailyConfig).filter(DailyConfig.user_id == user_id).order_by(
            DailyConfig.id.desc()).first()

        dtype = config.daily_type
        chat_id = config.chat_id
        city = config.daily_city
        valute = config.daily_valute
        time = config.daily_schedule

        return dtype, chat_id, city, valute, time
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка получения конфига: {e}")
    finally:
        session.close()

def delete_daily_config(user_name: str):
    session = Session()
    try:
        objs = session.query(DailyConfig).filter(DailyConfig.user_name == user_name).all()

        if objs:
            for obj in objs:
                session.delete(obj)
            session.commit()
            print(f"Конфигурация юзера {user_name} успешно удалена")
        else:
            print(f"Конфигурация юзера {user_name} не найдена")

    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при удалении записи из БД: {e}")

    finally:
        session.close()


def get_daily_mode(user_id: int):
    session = Session()
    try:
        obj = session.query(DailyMode).filter(DailyMode.user_id == user_id).order_by(DailyMode.id.desc()).first()
        if obj:
            mode = obj.daily_mode
            last_id = obj.id

            session.query(DailyMode).filter(DailyMode.user_id == user_id, DailyMode.id < last_id).delete(synchronize_session=False)
            session.commit()
            print('Режимы юзеров успешно найдены в БД')
            return mode

        else:
            print("Юзер не найден в БД")
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка получения режима рассылки: {e}")
    finally:
        session.close()



def save_daily_mode(user_name: str, user_id: int, daily_mode: str):
    session = Session()
    try:
        new_mode = DailyMode(
            user_name=user_name,
            user_id=user_id,
            daily_mode=daily_mode,
        )
        session.add(new_mode)
        session.commit()
        logger.info(f"Режим рассылки сохранена в БД: ID={new_mode.id}")

    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка сохранения режима в БД: {e}")

    finally:
        session.close()

def get_all_users_with_daily_mode():
    session = Session()
    try:
        objs = session.query(DailyMode).all()
        if objs:
            users = [obj.user_id for obj in objs]

            return users
        else:
            print("Юзер не найден в БД")
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка получения юзеров: {e}")
    finally:
        session.close()

# def save_user_data(user_name: str, chat_id: int, data: str):
#     session = Session()
#     try:
#story_lines = show_story(6278046215)

#for line in story_lines:

#print(show_story(6278046215))

#save_daily_config(123456789, "TEST", "test_type", "Тесто город", "Тесто валюта", "test_schedule")

#save_daily_mode('@chebureck999', 'OFF')


#print(get_daily_config_without_time('6278046215'))

#print(get_daily_mode(res))