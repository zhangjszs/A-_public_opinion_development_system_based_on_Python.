#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证模块
功能：处理用户登录、注册和登出操作
作者：微博舆情分析系统
"""

from flask import Flask, session, render_template, redirect, Blueprint, request
from utils.errorResponse import *
import time
from utils.query import querys

# 创建用户蓝图，设置URL前缀和模板文件夹
ub = Blueprint('user', __name__, url_prefix='/user', template_folder='templates')


@ub.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录功能
    GET: 显示登录页面
    POST: 处理登录验证
    """
    if request.method == 'POST':
        # 将表单数据转换为字典格式，便于处理
        request.form = dict(request.form)
        
        # 获取并清理用户输入数据
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # 输入验证：检查用户名和密码是否为空
        if not username or not password:
            return errorResponse('用户名和密码不能为空')

        try:
            # 数据库查询：使用参数化查询防止SQL注入
            # 精确匹配用户名和密码
            users = querys(
                'SELECT * FROM user WHERE username = %s AND password = %s', 
                [username, password], 
                'select'
            )
            
            if len(users) > 0:
                # 登录成功：设置会话信息
                user_info = users[0]
                session['username'] = username
                session['createTime'] = user_info.get('createTime', '')
                session.permanent = True  # 设置会话为永久（直到过期时间）
                
                # 记录登录日志
                print(f"用户登录成功: {username} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 检查是否有待重定向的页面
                redirect_url = request.args.get('redirect', '/page/home')
                
                # 安全检查：确保重定向URL是内部URL
                if redirect_url.startswith('/'):
                    return redirect(redirect_url, 301)
                else:
                    # 如果不是内部URL，重定向到默认主页
                    return redirect('/page/home', 301)
            else:
                # 登录失败：返回错误信息
                return errorResponse('用户名或密码错误，请检查输入')
                
        except Exception as e:
            # 异常处理：记录错误日志并返回友好错误信息
            print(f"登录异常: {e}")
            return errorResponse('登录过程中发生错误，请稍后再试')
    else:
        # GET请求：渲染登录页面模板
        return render_template('login.html')


@ub.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册功能
    GET: 显示注册页面
    POST: 处理用户注册
    """
    if request.method == 'POST':
        # 将表单数据转换为字典格式
        request.form = dict(request.form)
        
        # 获取注册表单数据
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        password_checked = request.form.get('passwordCheked', '').strip()
        
        # 输入验证：检查必填字段
        if not username or not password or not password_checked:
            return errorResponse('所有字段都必须填写')
        
        # 密码确认验证
        if password != password_checked:
            return errorResponse('两次输入的密码不一致')
        
        # 密码强度验证（可选）
        if len(password) < 3:
            return errorResponse('密码长度至少3位')
            
        try:
            # 检查用户名是否已存在
            existing_users = querys(
                'SELECT * FROM user WHERE username = %s', 
                [username], 
                'select'
            )
            
            if len(existing_users) > 0:
                return errorResponse('该用户名已被注册，请选择其他用户名')
            
            # 生成当前时间作为创建时间
            current_time = time.strftime('%Y-%m-%d', time.localtime())
            
            # 插入新用户到数据库
            querys(
                'INSERT INTO user(username, password, createTime) VALUES(%s, %s, %s)',
                [username, password, current_time]
            )
            
            print(f"新用户注册成功: {username} at {current_time}")
            
            # 注册成功后重定向到登录页面
            return redirect('/user/login', 301)
            
        except Exception as e:
            # 异常处理：记录错误并返回友好错误信息
            print(f"注册异常: {e}")
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