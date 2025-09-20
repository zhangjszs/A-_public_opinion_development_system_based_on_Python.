#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博反反爬机制突破工具
解决403 Forbidden问题的综合方案
"""

import requests
import time
import random
import json
from urllib.parse import quote

def get_real_browser_headers():
    """获取更真实的浏览器请求头"""
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'weibo.com',
        'Pragma': 'no-cache',
        'Referer': 'https://weibo.com/',
        'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

def test_cookie_validity(cookie_string):
    """测试Cookie是否有效"""
    print("🔍 测试Cookie有效性...")
    
    headers = get_real_browser_headers()
    headers['Cookie'] = cookie_string
    
    # 测试用户信息API（需要登录）
    test_url = 'https://weibo.com/ajax/statuses/mymblog'
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"Cookie测试状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') == 1:
                print("✅ Cookie有效！")
                return True
            else:
                print(f"❌ Cookie无效 - API返回: {data}")
                return False
        elif response.status_code == 403:
            print("❌ Cookie已失效或被封禁")
            return False
        else:
            print(f"❌ 测试失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cookie测试异常: {e}")
        return False

def test_anonymous_access():
    """测试匿名访问是否可行"""
    print("\n🔍 测试匿名访问...")
    
    headers = get_real_browser_headers()
    # 移除Cookie，测试匿名访问
    headers.pop('Cookie', None)
    
    # 尝试访问公开的热搜API
    test_url = 'https://weibo.com/ajax/statuses/hot_band'
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"匿名访问状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 匿名访问成功！可以尝试不使用Cookie")
            return True
        else:
            print(f"❌ 匿名访问失败")
            return False
            
    except Exception as e:
        print(f"❌ 匿名访问异常: {e}")
        return False

def generate_improved_config():
    """生成改进的配置文件"""
    print("\n📝 生成改进的反反爬配置...")
    
    improved_config = '''
# 改进的微博爬虫配置
# 解决403 Forbidden问题

# 更真实的请求头配置
IMPROVED_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'weibo.com',
    'Pragma': 'no-cache',
    'Referer': 'https://weibo.com/',
    'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    # ⚠️ 请在这里添加您的有效Cookie
    'Cookie': '您的Cookie字符串'
}

# 更保守的请求频率
SAFE_DELAY = (5, 10)  # 5-10秒间隔
SAFE_TIMEOUT = 30     # 30秒超时
MAX_RETRIES = 2       # 最多重试2次
'''
    
    with open('spider/improved_config.py', 'w', encoding='utf-8') as f:
        f.write(improved_config)
    
    print("✅ 配置文件已生成: spider/improved_config.py")

def get_cookie_instructions():
    """获取Cookie的详细说明"""
    instructions = """
🍪 如何获取有效的微博Cookie：

1. 打开Chrome浏览器
2. 访问 https://weibo.com 并登录您的账号
3. 按F12打开开发者工具
4. 切换到 Network（网络）标签页
5. 在微博页面中随便点击一下（触发请求）
6. 在Network列表中找到任意一个对weibo.com的请求
7. 点击该请求，查看Request Headers
8. 复制完整的Cookie值

⚠️ Cookie格式示例：
Cookie: SCF=xxx; XSRF-TOKEN=xxx; PC_TOKEN=xxx; SUB=xxx; SUBP=xxx; ALF=xxx; WBPSESS=xxx

🔧 Cookie更新步骤：
1. 将获取的Cookie复制到config.py文件中
2. 替换BASE_HEADERS中的Cookie值
3. 重新运行爬虫程序

💡 其他建议：
- Cookie通常24小时内有效
- 如果频繁被封，可以尝试更换IP
- 降低爬取频率，增加延迟时间
- 使用代理IP分散请求
"""
    return instructions

def suggest_alternative_approaches():
    """建议其他爬取方法"""
    suggestions = """
🔄 其他爬取策略：

1. 【降频策略】
   - 将延迟时间增加到10-30秒
   - 减少并发线程数
   - 分时段爬取（避开高峰期）

2. 【代理策略】
   - 使用高质量付费代理
   - 轮换多个代理IP
   - 避免免费代理（容易被识别）

3. 【模拟策略】
   - 使用Selenium模拟真实浏览器
   - 添加随机鼠标移动和点击
   - 模拟人类行为模式

4. 【API策略】
   - 寻找官方API接口
   - 使用微博开放平台
   - 考虑RSS或其他数据源

5. 【分布式策略】
   - 使用多台服务器
   - 不同地区IP
   - 错开爬取时间
"""
    return suggestions

def main():
    """主诊断程序"""
    print("🚨 微博爬虫403问题诊断工具")
    print("=" * 50)
    
    # 读取当前配置中的Cookie
    try:
        import sys
        sys.path.append('spider')
        from config import HEADERS
        current_cookie = HEADERS.get('Cookie', '')
        
        if current_cookie and len(current_cookie) > 100:
            print(f"📋 检测到Cookie (长度: {len(current_cookie)})")
            # 测试Cookie有效性
            is_valid = test_cookie_validity(current_cookie)
            if not is_valid:
                print("\n🔧 Cookie已失效，需要更新！")
        else:
            print("❌ 未检测到有效Cookie")
            
    except Exception as e:
        print(f"❌ 配置读取失败: {e}")
    
    # 测试匿名访问
    test_anonymous_access()
    
    # 生成改进配置
    generate_improved_config()
    
    # 显示说明
    print("\n" + get_cookie_instructions())
    print("\n" + suggest_alternative_approaches())
    
    print("\n🎯 推荐的解决步骤：")
    print("1. 更新Cookie（最重要）")
    print("2. 降低爬取频率到10-30秒/请求")
    print("3. 使用代理IP")
    print("4. 如果仍有问题，考虑使用Selenium")
    
    print("\n💡 快速修复：")
    print("- 在config.py中更新Cookie")
    print("- 将DEFAULT_DELAY改为(10, 30)")
    print("- 重新运行爬虫程序")

if __name__ == '__main__':
    main()