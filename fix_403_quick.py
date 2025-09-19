#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复403 Forbidden错误
通过更新配置和降低请求频率解决反爬问题
"""

import os
import time

def show_403_solutions():
    """显示403错误的解决方案"""
    print("🚨 微博爬虫403 Forbidden错误分析")
    print("=" * 60)
    
    print("\n📋 问题原因分析：")
    print("1. ❌ Cookie已过期（最主要原因）")
    print("2. ❌ 请求频率过高（2-5秒间隔太快）") 
    print("3. ❌ 请求头不够真实")
    print("4. ❌ IP被临时封禁")
    
    print("\n🔧 立即可行的解决方案：")
    print("\n方案1: 更新Cookie（推荐）")
    print("1. 打开浏览器访问 https://weibo.com 并登录")
    print("2. 按F12打开开发者工具 → Network标签")
    print("3. 刷新页面，点击任意weibo.com请求")
    print("4. 复制Request Headers中的完整Cookie")
    print("5. 替换config.py中BASE_HEADERS的Cookie值")
    
    print("\n方案2: 降低请求频率（临时解决）")
    print("- 将延迟从(2,5)秒改为(15,30)秒")
    print("- 减少爬取页数，先测试1页")
    
    print("\n方案3: 使用代理IP")
    print("- 购买高质量代理服务")
    print("- 避免使用免费代理")
    
    return True

def create_safe_config():
    """创建安全的配置文件"""
    print("\n📝 创建保守的爬虫配置...")
    
    safe_config_content = '''# 保守的爬虫配置 - 解决403问题
# 请将此配置复制到config.py中相应位置

# 更安全的延迟配置
DEFAULT_DELAY = (15, 30)  # 15-30秒延迟，避免触发反爬
DEFAULT_TIMEOUT = 45      # 45秒超时
MAX_RETRIES = 1          # 只重试1次

# 更真实的请求头
SAFE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://weibo.com/',
    # ⚠️ 重要：请在下面添加您的最新Cookie
    'Cookie': '请在这里粘贴您的最新Cookie'
}
'''
    
    with open('safe_spider_config.txt', 'w', encoding='utf-8') as f:
        f.write(safe_config_content)
    
    print("✅ 安全配置已保存到: safe_spider_config.txt")
    return True

def update_config_delay():
    """直接更新config.py中的延迟配置"""
    config_path = 'spider/config.py'
    
    if not os.path.exists(config_path):
        print("❌ 找不到config.py文件")
        return False
    
    try:
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新延迟配置为更保守的值
        updated_content = content.replace(
            'self.DEFAULT_DELAY = (2, 5)',
            'self.DEFAULT_DELAY = (15, 30)  # 修改为15-30秒，避免403错误'
        )
        
        # 更新超时时间
        updated_content = updated_content.replace(
            'self.DEFAULT_TIMEOUT = 30',
            'self.DEFAULT_TIMEOUT = 45  # 增加到45秒'
        )
        
        # 保存修改
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ 已更新config.py中的延迟配置")
        print("   - 请求延迟: 15-30秒")
        print("   - 超时时间: 45秒")
        return True
        
    except Exception as e:
        print(f"❌ 更新配置失败: {e}")
        return False

def test_with_minimal_requests():
    """使用最小请求进行测试"""
    print("\n🧪 创建最小测试脚本...")
    
    test_script = '''#!/usr/bin/env python3
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
'''
    
    with open('test_weibo_minimal.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ 最小测试脚本已创建: test_weibo_minimal.py")
    print("   请先更新其中的Cookie，然后运行测试")
    return True

def main():
    """主程序"""
    show_403_solutions()
    create_safe_config()
    update_config_delay()
    test_with_minimal_requests()
    
    print("\n🎯 推荐解决步骤：")
    print("1. 【立即执行】更新Cookie（最重要）")
    print("   - 访问weibo.com登录")
    print("   - F12 → Network → 复制Cookie")
    print("   - 更新config.py中的Cookie")
    
    print("\n2. 【已自动完成】降低请求频率")
    print("   - 延迟已改为15-30秒")
    print("   - 超时时间已改为45秒")
    
    print("\n3. 【验证修复】运行测试")
    print("   - 先运行 test_weibo_minimal.py 验证")
    print("   - 如果成功，再运行完整爬虫")
    
    print("\n4. 【可选】如果仍有问题")
    print("   - 考虑使用付费代理IP")
    print("   - 或者使用Selenium模拟浏览器")
    
    print("\n💡 快速验证命令：")
    print("python test_weibo_minimal.py")

if __name__ == '__main__':
    main()