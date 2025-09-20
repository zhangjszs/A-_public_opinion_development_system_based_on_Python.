#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query import querys

def test_database():
    print("=== 数据库连接测试 ===")
    
    try:
        # 测试基本连接
        print("1. 测试数据库连接...")
        result = querys("SELECT 1 as test", [], 'select')
        print(f"   连接测试结果: {result}")
        
        # 查询用户表结构
        print("\n2. 查询用户表结构...")
        try:
            structure = querys("DESCRIBE user", [], 'select')
            print("   用户表结构:")
            for col in structure:
                print(f"     {col}")
        except Exception as e:
            print(f"   查询表结构失败: {e}")
        
        # 查询所有用户
        print("\n3. 查询所有用户数据...")
        users = querys("SELECT * FROM user", [], 'select')
        print(f"   总用户数: {len(users)}")
        
        for i, user in enumerate(users):
            print(f"   用户{i+1}:")
            print(f"     ID: {user['id']}")
            print(f"     用户名: '{user['username']}' (长度: {len(user['username'])})")
            print(f"     密码: '{user['password']}' (长度: {len(user['password'])})")
            print(f"     创建时间: {user['createTime']}")
            print()
        
        # 测试特定用户查询
        print("4. 测试特定用户查询...")
        test_users = [
            ("kerwin zhang", "123"),
            ("Alex", "123456"),
            ("Admin", "123456")
        ]
        
        for username, password in test_users:
            print(f"\n   测试用户: '{username}' / '{password}'")
            result = querys("SELECT * FROM user WHERE username = %s AND password = %s", 
                          [username, password], 'select')
            print(f"   查询结果: {len(result)} 个匹配")
            if result:
                user = result[0]
                print(f"   匹配用户: ID={user['id']}, 用户名='{user['username']}', 密码='{user['password']}')")
        
        print("\n=== 测试完成 ===")
        return True
        
    except Exception as e:
        print(f"数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database()