#!/usr/bin/env python3
# 最小微博API测试脚本
import requests
import time

def test_weibo_api():
    """测试微博API访问"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://weibo.com/',
        # ⚠️ 请在下面添加您的Cookie
        'Cookie': '请替换为您的Cookie'
    }
    
    # 测试API
    test_url = 'https://weibo.com/ajax/feed/hottimeline'
    params = {
        'since_id': '0',
        'refresh': '0', 
        'group_id': '102803',
        'containerid': '102803',
        'extparam': 'discover|new_feed',
        'max_id': '0',
        'count': '5'  # 只请求5条数据
    }
    
    print("🔍 测试微博API访问...")
    print("等待30秒以避免频率限制...")
    time.sleep(30)
    
    try:
        response = requests.get(test_url, headers=headers, params=params, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'statuses' in data:
                print(f"✅ 成功！获取到 {len(data['statuses'])} 条数据")
                return True
            else:
                print(f"❌ 数据格式异常: {data}")
        elif response.status_code == 403:
            print("❌ 仍然403 - Cookie可能无效或需要更长延迟")
        else:
            print(f"❌ 状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    return False

if __name__ == '__main__':
    test_weibo_api()
