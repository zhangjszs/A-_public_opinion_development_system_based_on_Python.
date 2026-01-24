#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证模块
功能：处理用户登录、注册和登出操作
特性：密码哈希存储、输入验证、安全日志
作者：微博舆情分析系统
"""

from flask import Flask, session, render_template, redirect, Blueprint, request
from utils.errorResponse import *
from utils.password_hasher import hash_password, verify_password, check_password_strength
from utils.input_validator import validate_username, validate_password, sanitize_input
from utils.log_sanitizer import SafeLogger
import time
from utils.query import querys
import logging

logger = SafeLogger('user_auth', logging.INFO)

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
        # 将表单数据转换为字典格式，便于处理
        request.form = dict(request.form)
        
        # 获取并清理用户输入数据
        username_raw = request.form.get('username', '').strip()
        password_raw = request.form.get('password', '').strip()
        
        # 输入验证和清理
        username_validation = validate_username(username_raw)
        if not username_validation['valid']:
            logger.warning(f"登录失败：{username_validation['message']} | IP: {request.remote_addr}")
            return errorResponse(username_validation['message'])
        
        password_validation = validate_password(password_raw)
        if not password_validation['valid']:
            logger.warning(f"登录失败：{password_validation['message']} | IP: {request.remote_addr}")
            return errorResponse(password_validation['message'])
        
        # 清理输入（防止XSS）
        username = sanitize_input(username_raw, max_length=20)
        password = password_raw  # 密码不清理，用于验证
        
        # 输入验证：检查用户名和密码是否为空
        if not username or not password:
            logger.warning(f"登录失败：用户名或密码为空 | IP: {request.remote_addr}")
            return errorResponse('用户名和密码不能为空')

        try:
            # 数据库查询：使用参数化查询防止SQL注入
            # 只查询用户名，不直接比较密码
            users = querys(
                'SELECT * FROM user WHERE username = %s', 
                [username], 
                'select'
            )
            
            if len(users) > 0:
                user_info = users[0]
                
                # 使用bcrypt验证密码
                if verify_password(password, user_info.get('password', '')):
                    # 登录成功：设置会话信息
                    session['username'] = username
                    session['user_id'] = user_info.get('id')
                    session['createTime'] = user_info.get('createTime', '')
                    session.permanent = True  # 设置会话为永久（直到过期时间）
                    
                    # 记录登录日志（脱敏处理）
                    logger.info(f"用户登录成功: {username} at {time.strftime('%Y-%m-%d %H:%M:%S')} | IP: {request.remote_addr}")
                    
                    # 检查是否有待重定向的页面
                    redirect_url = request.args.get('redirect', '/page/home')
                    
                    # 安全检查：确保重定向URL是内部URL
                    if redirect_url.startswith('/'):
                        return redirect(redirect_url, 301)
                    else:
                        # 如果不是内部URL，重定向到默认主页
                        return redirect('/page/home', 301)
                else:
                    # 密码错误
                    logger.warning(f"登录失败：密码错误 | 用户名: {username} | IP: {request.remote_addr}")
                    return errorResponse('用户名或密码错误，请检查输入')
            else:
                # 用户不存在
                logger.warning(f"登录失败：用户不存在 | 用户名: {username} | IP: {request.remote_addr}")
                return errorResponse('用户名或密码错误，请检查输入')
                
        except Exception as e:
            # 异常处理：记录错误日志并返回友好错误信息
            logger.error(f"登录异常: {e} | 用户名: {username} | IP: {request.remote_addr}")
            return errorResponse('登录过程中发生错误，请稍后再试')
    else:
        # GET请求：渲染登录页面模板
        return render_template('login.html')


@ub.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册功能
    GET: 显示注册页面
    POST: 处理用户注册（使用密码哈希）
    """
    if request.method == 'POST':
        # 将表单数据转换为字典格式
        request.form = dict(request.form)
        
        # 获取并清理用户输入数据
        username_raw = request.form.get('username', '').strip()
        password_raw = request.form.get('password', '').strip()
        password_checked_raw = request.form.get('passwordCheked', '').strip()
        
        # 输入验证和清理
        username_validation = validate_username(username_raw)
        if not username_validation['valid']:
            logger.warning(f"注册失败：{username_validation['message']} | IP: {request.remote_addr}")
            return errorResponse(username_validation['message'])
        
        password_validation = validate_password(password_raw)
        if not password_validation['valid']:
            logger.warning(f"注册失败：{password_validation['message']} | IP: {request.remote_addr}")
            return errorResponse(password_validation['message'])
        
        # 清理输入（防止XSS）
        username = sanitize_input(username_raw, max_length=20)
        password = password_raw  # 密码不清理，用于哈希
        password_checked = sanitize_input(password_checked_raw, max_length=32)
        
        # 输入验证：检查必填字段
        if not username or not password or not password_checked:
            logger.warning(f"注册失败：字段不完整 | 用户名: {username} | IP: {request.remote_addr}")
            return errorResponse('所有字段都必须填写')
        
        # 密码确认验证
        if password != password_checked:
            logger.warning(f"注册失败：密码不一致 | 用户名: {username} | IP: {request.remote_addr}")
            return errorResponse('两次输入的密码不一致')
        
        # 密码强度检查
        strength_check = check_password_strength(password)
        if not strength_check['valid']:
            logger.warning(f"注册失败：密码强度不足 | 用户名: {username} | IP: {request.remote_addr}")
            return errorResponse(f'密码强度不足：{", ".join(strength_check["suggestions"])}')
        
        try:
            # 检查用户名是否已存在
            existing_users = querys(
                'SELECT * FROM user WHERE username = %s', 
                [username], 
                'select'
            )
            
            if len(existing_users) > 0:
                logger.warning(f"注册失败：用户名已存在 | 用户名: {username} | IP: {request.remote_addr}")
                return errorResponse('该用户名已被注册，请选择其他用户名')
            
            # 哈希密码
            hashed_password = hash_password(password)
            
            # 生成当前时间作为创建时间
            current_time = time.strftime('%Y-%m-%d', time.localtime())
            
            # 插入新用户到数据库（存储哈希后的密码）
            querys(
                'INSERT INTO user(username, password, createTime) VALUES(%s, %s, %s)',
                [username, hashed_password, current_time]
            )
            
            # 记录注册日志（脱敏处理）
            logger.info(f"新用户注册成功: {username} at {current_time} | IP: {request.remote_addr}")
            
            # 注册成功后重定向到登录页面
            return redirect('/user/login', 301)
            
        except ValueError as e:
            # 密码哈希错误
            logger.error(f"注册异常（密码哈希）: {e} | 用户名: {username} | IP: {request.remote_addr}")
            return errorResponse(str(e))
        except Exception as e:
            # 其他异常处理：记录错误并返回友好错误信息
            logger.error(f"注册异常: {e} | 用户名: {username} | IP: {request.remote_addr}")
            return errorResponse('注册过程中发生错误，请稍后再试')
            
    else:
        # GET请求：渲染注册页面模板
        return render_template('register.html')


@ub.route('/logOut', methods=['GET', 'POST'])
def logOut():
    """
    用户登出功能
    清理会话信息并重定向到登录页面
    """
    # 获取当前用户名用于日志记录
    current_user = session.get('username', 'Unknown')
    
    # 清除所有会话数据
    session.clear()
    
    # 记录登出日志
    print(f"用户登出: {current_user} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 重定向到登录页面
    return redirect('/user/login')