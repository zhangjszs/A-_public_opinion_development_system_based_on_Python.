
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
