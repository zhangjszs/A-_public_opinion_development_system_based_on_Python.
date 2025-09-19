import time
import requests
import csv
import os
import re
import random
from datetime import datetime
from config import HEADERS, DEFAULT_TIMEOUT, DEFAULT_DELAY, get_random_headers, get_working_proxy

def init():
    if not os.path.exists('articleData.csv'):
        with open('articleData.csv','w',encoding='utf8',newline='') as csvfile:
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
        with open('articleData.csv','a',encoding='utf8',newline='') as csvfile:
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

def start(typeNum=2,pageNum=2):
    articleUrl = 'https://weibo.com/ajax/feed/hottimeline'
    init()
    typeNumCount = 0
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nav_path = os.path.join(base_dir, 'navData.csv')
    with open(nav_path,'r',encoding='utf8') as readerFile:
        reader = csv.reader(readerFile)
        next(reader)
        for nav in reader:
            if typeNumCount > typeNum:return
            for page in range(0,pageNum):
                # 处理DEFAULT_DELAY - 如果是元组则取随机值，否则直接使用
                if isinstance(DEFAULT_DELAY, tuple):
                    delay = random.uniform(DEFAULT_DELAY[0], DEFAULT_DELAY[1])
                else:
                    delay = DEFAULT_DELAY
                time.sleep(delay)
                print('正在爬取类型：' + nav[0] + '中的第' + str(page + 1) + '页数据')
                
                # 根据博客优化：动态参数处理
                params = {
                    'group_id':nav[1],
                    'containerid':nav[2],
                    'max_id':page,
                    'count':10,
                    'extparam':'discover|new_feed'
                }
                
                # 第一页需要特殊参数since_id=0和refresh=0
                if page == 0:
                    params['since_id'] = '0'
                    params['refresh'] = '0'
                else:
                    # 后续页面使用refresh=2
                    params['refresh'] = '2'
                
                response = get_json(articleUrl,params)
                if response is None:
                    print(f'请求失败，跳过类型：{nav[0]} 第{page + 1}页')
                    continue
                if 'statuses' not in response:
                    print(f'响应格式异常，跳过类型：{nav[0]} 第{page + 1}页，响应：{response}')
                    continue
                parse_json(response['statuses'],nav[0])
            typeNumCount += 1

if __name__ == '__main__':
    start()