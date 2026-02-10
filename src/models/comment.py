from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
import datetime

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(String(50), primary_key=True)
    rootId = Column(String(50)) # 关联的文章ID
    content = Column(Text)
    likeNum = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = Column(String(100))
    
    def __repr__(self):
        return f'<Comment {self.id!r}>'
