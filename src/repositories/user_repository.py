from typing import Any, Dict, Optional

from models.user import User

from .base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        user = self.session.query(User).filter_by(username=username).first()
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'password': user.password,
                'create_time': user.create_time
            }
        return None

    def create(self, username: str, password_hash: str, create_time: str) -> None:
        user = User(username=username, password=password_hash, create_time=create_time)
        self.save(user)
