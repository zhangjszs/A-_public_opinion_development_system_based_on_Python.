import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    create_time = Column('createTime', DateTime, default=datetime.datetime.utcnow)

    def __init__(self, username=None, password=None, create_time=None):
        self.username = username
        self.password = password
        self.create_time = create_time

    def __repr__(self):
        return f'<User {self.username!r}>'
