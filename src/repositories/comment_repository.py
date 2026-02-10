from typing import List, Dict, Any, Tuple

from sqlalchemy import desc

from .base_repository import BaseRepository
from models.comment import Comment


class CommentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Comment)

    def find_with_filter(
        self,
        keyword: str = '',
        article_id: str = '',
        user: str = '',
        start_time: str = '',
        end_time: str = '',
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = self.session.query(Comment)

        if article_id:
            query = query.filter(Comment.rootId == article_id)

        if user:
            query = query.filter(Comment.user.like(f"%{user}%"))

        if keyword:
            query = query.filter(Comment.content.like(f"%{keyword}%"))

        if start_time and end_time:
            query = query.filter(Comment.created_at.between(start_time, end_time))

        total = query.count()
        rows = query.order_by(desc(Comment.created_at)).limit(limit).offset(offset).all()

        result: List[Dict[str, Any]] = []
        for c in rows:
            result.append(
                {
                    "id": c.id,
                    "rootId": c.rootId,
                    "content": c.content,
                    "likeNum": c.likeNum,
                    "created_at": c.created_at,
                    "user": c.user,
                }
            )

        return result, total

