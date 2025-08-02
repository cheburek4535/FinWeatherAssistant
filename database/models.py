from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sqlalchemy
import os

Base = sqlalchemy.orm.declarative_base()

class UserRequest(Base):
    __tablename__ = 'user_requests'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String, nullable=False)
    request_type = Column(String(20), nullable=False)
    request_data = Column(String(100), nullable=False)
    response_data = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "assistant.db")
engine = create_engine(f'sqlite:///{DB_PATH}')
#engine = create_engine('sqlite:///assistant.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)