from functools import wraps
from flask import request
from config.settings import Config
from utils.api_response import error


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = getattr(request, 'current_user', None) or {}
        username = user.get('username')
        if Config.ADMIN_USERS and username not in Config.ADMIN_USERS:
            return error('权限不足', code=403), 403
        return func(*args, **kwargs)

    return wrapper

