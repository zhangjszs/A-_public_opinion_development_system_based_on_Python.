import time
import requests
import csv
import os
import re
import random
from datetime import datetime
from config import HEADERS, DEFAULT_TIMEOUT, DEFAULT_DELAY, get_random_headers, get_working_proxy

def init():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    article_path = os.path.join(data_dir, 'articleData.csv')
    
    if not os.path.exists(article_path):
        with open(article_path,'w',encoding='utf8',newline='') as csvfile:
            wirter = csv.writer(csvfile)
            wirter.writerow([
                'id',
                'likeNum',
                'commentsLen',
                'reposts_count',
                'region',
                'content',
                'contentLen',
                'created_at',
                'type',
                'detailUrl',# followBtnCode>uid + mblogid
                'authorAvatar',
                'authorName',
                'authorDetail',
                'isVip' # v_plus
            ])

def wirterRow(row):
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    article_path = os.path.join(data_dir, 'articleData.csv')
    
    with open(article_path,'a',encoding='utf8',newline='') as csvfile:
            wirter = csv.writer(csvfile)
            wirter.writerow(row)

def get_json(url, params):
    # 使用随机headers和代理
    headers = get_random_headers()
    proxy = get_working_proxy()
    
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            proxies=proxy,
            timeout=DEFAULT_TIMEOUT
        )
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                print(f"JSON解析失败: {e}")
                print(f"响应内容: {response.text[:200]}...")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None

def parse_json(response,type):
    for article in response:
        id = article['id']
        likeNum = article['attitudes_count']
        commentsLen = article['comments_count']
        reposts_count = article['reposts_count']
        try:
            region = article['region_name'].replace('发布于 ','')
        except:
            region = '无'
        content = article['text_raw']
        contentLen = article.get('textLength', 0)
        created_at = datetime.strptime(article['created_at'],"%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d")
        type = type
        try:
            detailUrl = 'https://weibo.com/' + str(article['user']['id']) +'/'+ str(article['mblogid'])
        except:
            detailUrl = '无'
        authorAvatar = article['user']['avatar_large']
        authorName = article['user']['screen_name']
        authorDetail = 'https://weibo.com' + article['user']['profile_url']
        if  article['user']['v_plus']:
            isVip = article['user']['v_plus']
        else:
            isVip = 0
        wirterRow([
                id,
                likeNum,
                commentsLen,
                reposts_count,
                region,
                content,
                contentLen,
                created_at,
                type,
                detailUrl,
                authorAvatar,
                authorName,
                authorDetail,
                isVip
            ])

def search_weibo(keyword, pageNum=3):
    """
    根据关键词搜索微博
    """
    search_url = 'https://weibo.com/ajax/statuses/search'
    init()
    
    print(f'开始搜索关键词: {keyword}')
    
    for page in range(1, pageNum + 1):
        # 延时防爬
        if isinstance(DEFAULT_DELAY, tuple):
            delay = random.uniform(DEFAULT_DELAY[0], DEFAULT_DELAY[1])
        else:
            delay = DEFAULT_DELAY
        time.sleep(delay)
        
        print(f'正在爬取关键词 [{keyword}] 的第 {page} 页数据')
        
        # 构造搜索参数
        params = {
            'q': keyword,
            'type': 'all',
            'sub': 'all',
            'timescope': 'custom',
            'refer': 'g',
            'page': page,
            'count': 10
        }
        
        response = get_json(search_url, params)
        if response is None:
            print(f'请求失败，跳过第 {page} 页')
            continue
            
        if 'data' not in response or 'list' not in response['data']:
            print(f'响应格式异常，跳过第 {page} 页，可能无更多数据')
            continue
            
        # 搜索接口返回的数据结构可能与hottimeline不同，需要适配
        # 通常搜索接口的微博列表在 response['data']['list']
        statuses = response['data']['list']
        
        # 过滤掉非微博内容（如推广等）
        valid_statuses = [s for s in statuses if 'text_raw' in s or 'text' in s]
        
        if valid_statuses:
            parse_json(valid_statuses, f"搜索:{keyword}")
        else:
            print(f"第 {page} 页未找到有效微博数据")

def start(typeNum=2, pageNum=2, mode='category', keyword=None):
    """
    启动爬虫
    :param typeNum: 爬取的类型数量 (category模式)
    :param pageNum: 每个类型的爬取页数 (category模式) or 搜索页数 (search模式)
    :param mode: 'category' (分类) or 'search' (关键词搜索)
    :param keyword: 搜索关键词 (search模式需提供)
    """
    if mode == 'search':
        if not keyword:
            print("搜索模式必须提供关键词！")
            return
        search_weibo(keyword, pageNum)
    else:
        # 默认为分类爬取
        articleUrl = 'https://weibo.com/ajax/feed/hottimeline'
        init()
        typeNumCount = 0
        base_dir = os.path.dirname(os.path.dirname(__file__))
        nav_path = os.path.join(base_dir, 'data', 'navData.csv')
        
        if not os.path.exists(nav_path):
            print(f"导航文件不存在: {nav_path}")
            return

        with open(nav_path,'r',encoding='utf8') as readerFile:
            reader = csv.reader(readerFile)
            next(reader)
            for nav in reader:
                if typeNumCount > typeNum:return
                for page in range(0,pageNum):
                    # 处理DEFAULT_DELAY
                    if isinstance(DEFAULT_DELAY, tuple):
                        delay = random.uniform(DEFAULT_DELAY[0], DEFAULT_DELAY[1])
                    else:
                        delay = DEFAULT_DELAY
                    time.sleep(delay)
                    
                    print('正在爬取类型：' + nav[0] + '中的第' + str(page + 1) + '页数据')
                    
                    params = {
                        'group_id':nav[1],
                        'containerid':nav[2],
                        'max_id':page,
                        'count':10,
                        'extparam':'discover|new_feed'
                    }
                    
                    if page == 0:
                        params['since_id'] = '0'
                        params['refresh'] = '0'
                    else:
                        params['refresh'] = '2'
                    
                    response = get_json(articleUrl,params)
                    if response is None:
                        print(f'请求失败，跳过类型：{nav[0]} 第{page + 1}页')
                        continue
                    if 'statuses' not in response:
                        print(f'响应格式异常，跳过类型：{nav[0]} 第{page + 1}页')
                        continue
                    parse_json(response['statuses'],nav[0])
                typeNumCount += 1

if __name__ == '__main__':
    start()