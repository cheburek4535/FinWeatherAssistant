from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sqlalchemy

Base = sqlalchemy.orm.declarative_base()

class UserRequest(Base):
    __tablename__ = 'user_requests'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    request_type = Column(String(20), nullable=False)
    request_data = Column(String(100), nullable=False)
    response_data = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


engine = create_engine('sqlite:///assistant.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)