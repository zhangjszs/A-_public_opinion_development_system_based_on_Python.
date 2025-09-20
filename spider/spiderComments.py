import requests
import csv
import os
import numpy as np
from config import HEADERS, DEFAULT_TIMEOUT, DEFAULT_DELAY, get_random_headers, get_working_proxy
from datetime import datetime
import time # 1. 导入 time 模块
import random # (可选) 导入 random 模块，用于随机延时
import re
from jsonpath import jsonpath

def init():
    # 根据博客优化：增加更多评论字段
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    comments_path = os.path.join(data_dir, 'commentsData.csv')
    
    if not os.path.exists(comments_path):
        with open(comments_path,'w',encoding='utf8',newline='') as csvfile:
            wirter = csv.writer(csvfile)
            wirter.writerow([
                'comment_id',        # 评论ID
                'articleId',         # 文章ID
                'created_at',        # 创建时间
                'like_counts',       # 点赞数
                'region',           # 地区
                'content',          # 评论内容
                'authorName',       # 作者名称
                'authorGender',     # 作者性别
                'authorAddress',    # 作者地址
                'authorAvatar',     # 作者头像
                'user_id',          # 用户ID（新增）
                'reply_count',      # 回复数（新增）
                'comment_source'    # 评论来源（新增）
            ])

def wirterRow(row):
    # (wirterRow 函数保持不变)
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    comments_path = os.path.join(data_dir, 'commentsData.csv')
    
    with open(comments_path,'a',encoding='utf8',newline='') as csvfile:
        wirter = csv.writer(csvfile)
        wirter.writerow(row)

def get_html(url):
    # 删除原来的 headers 定义，直接使用导入的 HEADERS
    params = {
        'is_new_segment':1,
        'fetch_hot':1
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None

# 建议将函数名改回 get_json，因为它返回的是 json 数据
def get_json(url, id, uid=None):
    # 使用随机headers和代理
    headers = get_random_headers()
    proxy = get_working_proxy()
    
    # 根据博客优化：设置正确的Referer
    if uid:
        # 从articleData.csv中获取的uid和mblogid信息
        headers['Referer'] = f'https://weibo.com/{uid}/'
    
    # 根据博客优化：使用正确的参数
    params = {
        'is_reload': '1',           # 重新加载
        'id': id,                   # 文章ID
        'is_show_bulletin': '2',    # 显示公告
        'is_mix': '0',              # 不混合
        'count': '10',              # 每页数量
        'uid': uid or 'nouid',      # 用户ID
        'fetch_level': '0',         # 获取级别
        'locale': 'zh-CN'           # 语言环境
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
            print(f"Error: Request failed for ID {id} with status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Request exception for ID {id}: {e}")
        return None


# parse_json 和 process_comment 函数保持之前的良好结构，包含错误处理
def parse_json(response, articleId):
    # 根据博客优化：使用jsonpath进行数据提取
    print(f"--- Debug: Processing articleId {articleId} ---")

    if response is None:
        print("Error: Received None response.")
        return "ERROR_NONE_RESPONSE" # 返回一个标记

    if not isinstance(response, dict):
        print(f"Error: Expected response to be a dict, but got {type(response)}.")
        return "ERROR_INVALID_TYPE" # 返回一个标记

    if response.get('ok') == 0:
        error_msg = response.get('msg', 'Unknown API error')
        print(f"Error: API returned failure for articleId {articleId}. Message: {error_msg}")
        if '访问频次过高' in error_msg:
            return "RATE_LIMITED" # 返回特定标记表示频率限制
        else:
            return "API_ERROR" # 返回通用 API 错误标记

    # 根据博客优化：使用jsonpath提取数据
    try:
        # 提取评论相关字段
        comment_texts = jsonpath(response, '$..text')
        comment_ids = jsonpath(response, '$..id') 
        user_names = jsonpath(response, '$..screen_name')
        user_ids = jsonpath(response, '$..uid')
        created_times = jsonpath(response, '$..created_at')
        like_counts = jsonpath(response, '$..attitudes_count')
        
        if not comment_texts or comment_texts == False:
            print(f"No comments found for articleId {articleId}")
            return "NO_COMMENTS"
            
        print(f"Successfully found {len(comment_texts)} comments using jsonpath.")
        
        # 处理提取的数据，确保所有列表长度一致
        max_len = max(len(comment_texts), len(comment_ids or []), len(user_names or []))
        
        for i in range(min(len(comment_texts), max_len)):
            try:
                comment_data = {
                    'comment_id': comment_ids[i] if comment_ids and i < len(comment_ids) else '',
                    'text': comment_texts[i] if i < len(comment_texts) else '',
                    'user_name': user_names[i] if user_names and i < len(user_names) else '',
                    'user_id': user_ids[i] if user_ids and i < len(user_ids) else '',
                    'created_at': created_times[i] if created_times and i < len(created_times) else '',
                    'like_count': like_counts[i] if like_counts and i < len(like_counts) else 0
                }
                
                # 找到完整的评论对象进行详细处理
                commentList = response.get('data', [])
                if i < len(commentList):
                    process_comment(commentList[i], articleId)
                else:
                    process_simple_comment(comment_data, articleId)
                    
            except Exception as e:
                print(f"Error processing comment {i} for article {articleId}: {e}")
                continue
                
    except Exception as e:
        print(f"Error using jsonpath for article {articleId}: {e}")
        # 降级到原有处理方式
        commentList = response.get('data')
        if commentList and isinstance(commentList, list):
            for comment in commentList:
                process_comment(comment, articleId)
        else:
            return "ERROR_NO_DATA"

    return "SUCCESS" # 表示成功处理

def remove_html_tags(html_text):
    """移除HTML标签"""
    if not html_text:
        return ""
    return re.sub(r"<[^>]+>", "", html_text)

def process_simple_comment(comment_data, articleId):
    """处理简化的评论数据"""
    try:
        # 处理时间格式
        created_at = comment_data.get('created_at', 'Unknown')
        if created_at and created_at != 'Unknown':
            try:
                created_at = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        # 清理评论内容
        content = remove_html_tags(comment_data.get('text', '')) or "表情"
        
        wirterRow([
            comment_data.get('comment_id', ''),     # comment_id
            articleId,                              # articleId  
            created_at,                             # created_at
            comment_data.get('like_count', 0),      # like_counts
            '无',                                   # region
            content,                                # content
            comment_data.get('user_name', 'Unknown'), # authorName
            'Unknown',                              # authorGender
            'Unknown',                              # authorAddress
            '',                                     # authorAvatar
            comment_data.get('user_id', ''),        # user_id
            0,                                      # reply_count
            ''                                      # comment_source
        ])
    except Exception as e:
        print(f"Error in process_simple_comment: {e}")


def process_comment(comment, articleId):
    # 根据博客优化：增加更多字段提取
    """处理每条评论的逻辑"""
    try:
        # 微博返回的日期格式通常是 "%a %b %d %H:%M:%S %z %Y"
        created_at = datetime.strptime(comment['created_at'], "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d %H:%M:%S") # 保留时分秒可能更有用
    except (KeyError, ValueError) as e: # 捕获 KeyError 和日期格式错误 ValueError
        print(f"Warning: Could not parse date for comment in article {articleId}: {e}. Raw date: {comment.get('created_at')}")
        created_at = 'Unknown'

    # 根据博客优化：提取更多字段
    comment_id = comment.get('id', '')
    like_counts = comment.get('attitudes_count', 0)  # 使用attitudes_count替代like_counts
    reply_count = comment.get('total_number', 0)      # 回复数

    user = comment.get('user', {}) # 安全获取 user 字典
    user_id = user.get('id', '')                      # 用户ID
    authorName = user.get('screen_name', 'Unknown')
    authorGender = user.get('gender', 'Unknown') # m/f/n
    authorAddress = user.get('location', 'Unknown').split(' ')[0] # 只取省份/城市
    authorAvatar = user.get('avatar_large', '') # 使用空字符串作为默认值可能比 'Unknown' 好

    # region 通常在 source 字段里
    region_source = comment.get('source', '')
    region = region_source.replace('来自', '').strip() if region_source else '无'
    comment_source = comment.get('source', '')  # 评论来源

    # 评论内容 text_raw 可能包含 HTML 实体，text 字段是纯文本但可能不全
    content = comment.get('text_raw', '') # 优先使用 text_raw
    if not content:
        content = comment.get('text', 'No content') # 备选 text
    
    # 根据博客优化：移除HTML标签
    content = remove_html_tags(content) or "表情"

    # 根据博客优化：写入更多字段
    wirterRow([
        comment_id,         # comment_id
        articleId,          # articleId
        created_at,         # created_at
        like_counts,        # like_counts
        region,             # region
        content,            # content
        authorName,         # authorName
        authorGender,       # authorGender
        authorAddress,      # authorAddress
        authorAvatar,       # authorAvatar
        user_id,            # user_id
        reply_count,        # reply_count
        comment_source      # comment_source
    ])


def start():
    init()
    url = 'https://weibo.com/ajax/statuses/buildComments'
    article_csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'articleData.csv') # 更新为data目录下的路径

    if not os.path.exists(article_csv_path):
        print(f"Error: Input file not found at {article_csv_path}")
        return

    with open(article_csv_path,'r',encoding='utf8') as readerFile:
        reader = csv.reader(readerFile)
        try:
            header = next(reader) # 读取标题行
            # 可以选择性地检查标题行是否符合预期
            print(f"Input CSV Header: {header}")
        except StopIteration:
            print(f"Error: Input file {article_csv_path} is empty.")
            return

        for i, article in enumerate(reader):
            if not article: # 跳过空行
                continue
            try:
                articleId = article[0] # 假设 ID 总是在第一列
            except IndexError:
                print(f"Warning: Skipping row {i+2} due to missing article ID.")
                continue

            # 根据博客优化：使用DEFAULT_DELAY配置
            if isinstance(DEFAULT_DELAY, tuple):
                wait_seconds = random.uniform(DEFAULT_DELAY[0], DEFAULT_DELAY[1])
            else:
                wait_seconds = DEFAULT_DELAY
                
            print(f"--- Row {i+2}: Waiting for {wait_seconds:.2f} seconds before fetching comments for article ID {articleId} ---")
            time.sleep(wait_seconds)

            # 根据博客优化：尝试从detailUrl中提取uid
            uid = None
            if len(article) > 9:  # detailUrl 在第10列 (索引9)
                detail_url = article[9]
                if detail_url and 'weibo.com' in detail_url:
                    try:
                        # URL格式: https://weibo.com/uid/mblogid
                        parts = detail_url.replace('https://weibo.com/', '').split('/')
                        if len(parts) >= 1:
                            uid = parts[0]
                            print(f"Extracted uid: {uid} from URL: {detail_url}")
                    except Exception as e:
                        print(f"Failed to extract uid from URL: {detail_url}, error: {e}")

            print(f"Fetching comments for article ID: {articleId}")
            # 根据博客优化：传入uid参数
            response = get_json(url, articleId, uid)

            # 调用 parse_json 并检查其返回值
            parse_result = parse_json(response, articleId)

            # 根据 parse_json 的结果决定下一步操作
            if parse_result == "RATE_LIMITED":
                # 如果遇到频率限制，可以等待更长时间再继续，或者中断
                long_wait = 60 # 等待 1 分钟
                print(f"Rate limit hit. Waiting for {long_wait} seconds...")
                time.sleep(long_wait)
                print("Continuing after rate limit wait...")
            elif parse_result not in ["SUCCESS", "NO_COMMENTS", None]: # None 是为了兼容旧版 parse_json 可能不返回任何东西
                # 处理其他类型的错误，比如打印日志、跳过等
                print(f"Skipping article ID {articleId} due to parsing error: {parse_result}")

    print("Finished processing all articles in the CSV.")


if __name__ == '__main__':
    start()