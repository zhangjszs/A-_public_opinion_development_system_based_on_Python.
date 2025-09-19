import requests
import csv
import os
import numpy as np
from datetime import datetime
import time
import random
from config import HEADERS, DEFAULT_TIMEOUT, get_random_headers, get_working_proxy

def init():
    if not os.path.exists('navData.csv'):
        with open('navData.csv','w',encoding='utf8',newline='') as csvfile:
            wirter = csv.writer(csvfile)
            wirter.writerow([
                'typeName',
                'gid',
                'containerid'
            ])

def wirterRow(row):
        with open('navData.csv','a',encoding='utf8',newline='') as csvfile:
            wirter = csv.writer(csvfile)
            wirter.writerow(row)

def get_html(url):
    # 使用随机headers和代理
    headers = get_random_headers()
    proxy = get_working_proxy()
    
    params = {
        'is_new_segment':1,
        'fetch_hot':1
    }
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            proxies=proxy,
            timeout=DEFAULT_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None

def parse_json(response):
    navList = np.append(response['groups'][3]['group'],response['groups'][4]['group'])
    for nav in navList:
        navName = nav['title']
        gid = nav['gid']
        containerid = nav['containerid']
        wirterRow([
            navName,
            gid,
            containerid,
        ])

def get_json(url, id):
    # 使用导入的 HEADERS，删除原来的 headers 定义
    params = {
        'is_show_bulletin': 2,
        'id': id
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Request failed for ID {id} with status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Request exception for ID {id}: {e}")
        return None

if __name__ == '__main__':
    url = 'https://weibo.com/ajax/feed/allGroups'
    init()
    response = get_html(url)
    parse_json(response)