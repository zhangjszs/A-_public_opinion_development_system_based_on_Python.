#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证模块
功能：处理用户登录、注册和登出操作
特性：密码哈希存储、输入验证、安全日志
作者：微博舆情分析系统
"""

from flask import Flask, session, render_template, redirect, Blueprint, request, jsonify
from utils.errorResponse import *
from utils.input_validator import validate_username, validate_password, sanitize_input
from utils.log_sanitizer import SafeLogger
from utils.jwt_handler import jwt_required
from services.auth_service import AuthService
import time
import logging

logger = SafeLogger('user_auth', logging.INFO)
auth_service = AuthService()

# 创建用户蓝图，设置URL前缀和模板文件夹
ub = Blueprint('user', __name__, url_prefix='/user', template_folder='templates')


@ub.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录功能
    GET: 显示登录页面
    POST: 处理登录验证（使用密码哈希）
    """
    if request.method == 'POST':
        # 支持 JSON 和表单两种格式
        if request.is_json:
            data = request.get_json() or {}
            username_raw = data.get('username', '').strip()
            password_raw = data.get('password', '').strip()
        else:
            request.form = dict(request.form)
            username_raw = request.form.get('username', '').strip()
            password_raw = request.form.get('password', '').strip()
        
        # 输入验证
        username_validation = validate_username(username_raw)
        if not username_validation['valid']:
            return errorResponse(username_validation['message'])
        
        password_validation = validate_password(password_raw)
        if not password_validation['valid']:
            return errorResponse(password_validation['message'])
        
        username = sanitize_input(username_raw, max_length=20)
        password = password_raw

        # 调用 Service 层
        success, msg, data = auth_service.login(username, password)

        if success:
            # Session 设置 (保持向后兼容)
            user_info = data['user']
            session['username'] = user_info['username']
            session['user_id'] = user_info['id']
            session['createTime'] = user_info['createTime']
            session.permanent = True
            
            # API 响应
            is_api_request = (
                request.is_json or 
                request.headers.get('Accept', '').startswith('application/json')
            )
            
            if is_api_request:
                return jsonify({
                    'code': 200,
                    'msg': msg,
                    'data': data
                })
            else:
                redirect_url = request.args.get('redirect', '/page/home')
                return redirect(redirect_url if redirect_url.startswith('/') else '/page/home', 301)
        else:
            if request.is_json:
                return jsonify({'code': 401, 'msg': msg}), 401
            return errorResponse(msg)

    else:
        return render_template('login.html')


@ub.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册功能
    GET: 显示注册页面
    POST: 处理用户注册（使用密码哈希）
    """
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username_raw = data.get('username', '').strip()
            password_raw = data.get('password', '').strip()
            confirm_raw = (data.get('confirmPassword', '') or data.get('passwordCheked', '')).strip()
        else:
            request.form = dict(request.form)
            username_raw = request.form.get('username', '').strip()
            password_raw = request.form.get('password', '').strip()
            confirm_raw = (request.form.get('confirmPassword', '') or request.form.get('passwordCheked', '')).strip()
        
        username = sanitize_input(username_raw, max_length=20)
        password = password_raw
        confirm = sanitize_input(confirm_raw, max_length=32)
        
        # 调用 Service 层
        success, msg = auth_service.register(username, password, confirm)
        
        if success:
            if request.is_json:
                return jsonify({'code': 200, 'msg': msg})
            return redirect('/user/login', 301)
        else:
            return errorResponse(msg)
            
    else:
        return render_template('register.html')


@ub.route('/logOut', methods=['GET', 'POST'])
def logOut():
    """
    用户登出功能
    清理会话信息并重定向到登录页面
    """
    current_user = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"用户登出: {current_user}")
    
    is_api_request = (
        request.is_json or 
        request.headers.get('Accept', '').startswith('application/json')
    )
    
    if is_api_request:
        return jsonify({'code': 200, 'msg': '登出成功'})
    return redirect('/user/login')


@ub.route('/info', methods=['GET'])
@jwt_required
def get_user_info():
    """
    获取当前登录用户信息
    需要 JWT Token 认证
    """
    user = request.current_user
    # 这里的 querys 也可以重构，但为了演示 Service 模式，暂且保留或稍后重构
    # 更好的做法是在 AuthService 中添加 get_user_by_id
    from utils.query import querys
    try:
        users = querys(
            'SELECT id, username, createTime FROM user WHERE id = %s',
            [user['user_id']],
            'select'
        )
        if users:
            user_info = users[0]
            return jsonify({
                'code': 200,
                'msg': 'success',
                'data': {
                    'id': user_info.get('id'),
                    'username': user_info.get('username'),
                    'createTime': str(user_info.get('createTime', ''))
                }
            })
        else:
            return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    except Exception as e:
        logger.error(f"获取用户信息异常: {e}")
        return jsonify({'code': 500, 'msg': '获取用户信息失败'}), 500
