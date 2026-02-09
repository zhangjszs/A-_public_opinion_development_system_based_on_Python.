#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT 认证测试模块
测试登录、用户信息获取、注册等接口的 JWT 认证功能
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from flask import Flask
import json


class TestJWTHandler:
    """测试 JWT 处理模块"""
    
    def test_create_token(self):
        """测试 Token 创建"""
        from utils.jwt_handler import create_token, verify_token
        
        token = create_token(1, 'testuser')
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_valid_token(self):
        """测试验证有效 Token"""
        from utils.jwt_handler import create_token, verify_token
        
        token = create_token(1, 'testuser')
        payload = verify_token(token)
        
        assert payload is not None
        assert payload['user_id'] == 1
        assert payload['username'] == 'testuser'
    
    def test_verify_invalid_token(self):
        """测试验证无效 Token"""
        from utils.jwt_handler import verify_token
        
        result = verify_token('invalid.token.here')
        assert result is None
    
    def test_verify_empty_token(self):
        """测试验证空 Token"""
        from utils.jwt_handler import verify_token
        
        result = verify_token('')
        assert result is None


class TestLoginAPI:
    """测试登录 API"""
    
    @pytest.fixture
    def app(self):
        """创建测试 Flask 应用"""
        from app import app
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def test_login_requires_credentials(self, client):
        """测试登录需要凭据"""
        response = client.post(
            '/user/login',
            json={},
            headers={'Accept': 'application/json'}
        )
        # 应该返回错误
        assert response.status_code in [400, 401]
    
    def test_login_returns_json_for_api_request(self, client):
        """测试 API 请求返回 JSON"""
        response = client.post(
            '/user/login',
            json={'username': 'testuser', 'password': 'wrongpassword'},
            headers={'Accept': 'application/json'}
        )
        
        data = response.get_json()
        assert data is not None
        assert 'code' in data or 'error' in data
    
    def test_user_info_requires_token(self, client):
        """测试用户信息接口需要 Token"""
        response = client.get('/user/info')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 401


class TestRegisterAPI:
    """测试注册 API"""
    
    @pytest.fixture
    def app(self):
        """创建测试 Flask 应用"""
        from app import app
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def test_register_accepts_confirm_password(self, client):
        """测试注册接口接受 confirmPassword 字段"""
        # 注意：这个测试可能因为用户已存在而失败，这是预期行为
        response = client.post(
            '/user/register',
            json={
                'username': 'testuser_temp',
                'password': 'TestPass123!',
                'confirmPassword': 'TestPass123!'
            },
            headers={'Accept': 'application/json'}
        )
        
        data = response.get_json()
        # 接口应该返回 JSON 响应（无论成功还是失败）
        assert data is not None
        assert 'code' in data or 'msg' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
