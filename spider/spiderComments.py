import requests
import csv
import os
from datetime import datetime
import time # 1. 导入 time 模块
import random # (可选) 导入 random 模块，用于随机延时

def init():
    # (init 函数保持不变)
    if not os.path.exists('commentsData.csv'):
        with open('commentsData.csv','w',encoding='utf8',newline='') as csvfile:
            wirter = csv.writer(csvfile)
            wirter.writerow([
                'articleId',
                'created_at',
                'like_counts',
                'region',
                'content',
                'authorName',
                'authorGender',
                'authorAddress',
                'authorAvatar'
            ])

def wirterRow(row):
    # (wirterRow 函数保持不变)
    with open('commentsData.csv','a',encoding='utf8',newline='') as csvfile:
        wirter = csv.writer(csvfile)
        wirter.writerow(row)

# 建议将函数名改回 get_json，因为它返回的是 json 数据
def get_json(url,id): # <--- 函数名建议修改
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        # !!! 注意：这里的 Cookie 仍然是硬编码的，它会过期 !!!
        'Cookie': 'SINAGLOBAL=7212852614896.057.1722674779243; SCF=AuBnnYbv5UcU0Em9mzgayCIUin7u9gaSXe7Ioo3XKiTjesfDU7n5afCo3g09azYPzLTX9x6dK2qs4urCz3KBY5I.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5gY88XPngQwoKk7GKTwF4N5JpX5KzhUgL.FoM4SoM0eo.pS0.2dJLoI74u9PiNIg4kwJyydJM0eBtt; ULV=1745148345761:2:1:1:8580936394154.282.1745148345707:1722674779248; SUB=_2A25FAK7cDeRhGeFH7VUS8ifNzDWIHXVmf64UrDV8PUNbmtAYLWbAkW1NermJZDytnabRK03Lq9P5cWrT1OLtFZXJ; ALF=02_1747741580'
    }
    params = {
        'is_show_bulletin':2,
        'id':id
    }
    try:
        response = requests.get(url,headers=headers,params=params, timeout=10) # 添加超时设置
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
    # (保持之前的 parse_json 函数不变，它包含了处理 'ok':0 的逻辑)
    print(f"--- Debug: Processing articleId {articleId} ---")
    # print("Raw API Response:", response)  # 可以在需要时取消注释进行调试

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

    commentList = response.get('data')

    if commentList is None:
        print(f"Error: Could not find 'data' key in the response for articleId {articleId}, and no API error indicator found.")
        print("Full response:", response)
        return "ERROR_NO_DATA" # 返回标记

    if not isinstance(commentList, list):
        print(f"Warning: Expected 'data' to be a list, but got {type(commentList)} for articleId {articleId}.")
        return "ERROR_DATA_NOT_LIST" # 返回标记

    print(f"Successfully found 'data' key with {len(commentList)} items.")
    for comment in commentList:
        process_comment(comment, articleId)

    return "SUCCESS" # 表示成功处理


def process_comment(comment, articleId):
    # (保持之前的 process_comment 函数不变，它使用了 .get() 来安全访问)
    """处理每条评论的逻辑"""
    try:
        # 微博返回的日期格式通常是 "%a %b %d %H:%M:%S %z %Y"
        created_at = datetime.strptime(comment['created_at'], "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d %H:%M:%S") # 保留时分秒可能更有用
    except (KeyError, ValueError) as e: # 捕获 KeyError 和日期格式错误 ValueError
        print(f"Warning: Could not parse date for comment in article {articleId}: {e}. Raw date: {comment.get('created_at')}")
        created_at = 'Unknown'

    like_counts = comment.get('like_counts', 0)

    user = comment.get('user', {}) # 安全获取 user 字典
    authorName = user.get('screen_name', 'Unknown')
    authorGender = user.get('gender', 'Unknown') # m/f/n
    authorAddress = user.get('location', 'Unknown').split(' ')[0] # 只取省份/城市
    authorAvatar = user.get('avatar_large', '') # 使用空字符串作为默认值可能比 'Unknown' 好

    # region 通常在 source 字段里
    region_source = comment.get('source', '')
    region = region_source.replace('来自', '').strip() if region_source else '无'

    # 评论内容 text_raw 可能包含 HTML 实体，text 字段是纯文本但可能不全
    content = comment.get('text_raw', '') # 优先使用 text_raw
    if not content:
        content = comment.get('text', 'No content') # 备选 text

    wirterRow([
        articleId,
        created_at,
        like_counts,
        region,
        content,
        authorName,
        authorGender,
        authorAddress,
        authorAvatar,
    ])


def start():
    init()
    url = 'https://weibo.com/ajax/statuses/buildComments'
    article_csv_path = './articleData.csv' # 将文件名定义为变量

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

            # --- 2. 添加延时 ---
            wait_seconds = 1  # 设置等待时间（秒），可以根据需要调整
            print(f"--- Row {i+2}: Waiting for {wait_seconds:.2f} seconds before fetching comments for article ID {articleId} ---")
            time.sleep(wait_seconds)
            # -----------------

            print(f"Fetching comments for article ID: {articleId}")
            # 确保调用的是修改了名字的 get_json 函数
            response = get_json(url, articleId)

            # 调用 parse_json 并检查其返回值
            parse_result = parse_json(response, articleId)

            # 根据 parse_json 的结果决定下一步操作
            if parse_result == "RATE_LIMITED":
                # 如果遇到频率限制，可以等待更长时间再继续，或者中断
                long_wait = 60 # 等待 1 分钟
                print(f"Rate limit hit. Waiting for {long_wait} seconds...")
                time.sleep(long_wait)
                # 这里可以选择是否要重试当前 articleId，或者直接继续下一个
                # 如果要重试，可能需要调整循环逻辑或使用 while 循环
                print("Continuing after rate limit wait...")
            elif parse_result not in ["SUCCESS", None]: # None 是为了兼容旧版 parse_json 可能不返回任何东西
                # 处理其他类型的错误，比如打印日志、跳过等
                print(f"Skipping article ID {articleId} due to parsing error: {parse_result}")

    print("Finished processing all articles in the CSV.")


if __name__ == '__main__':
    start()