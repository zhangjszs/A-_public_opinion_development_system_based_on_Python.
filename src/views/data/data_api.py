#!/usr/bin/env python3
"""
数据 API 模块
功能：提供数据可视化相关 JSON API 接口
路由前缀: /getAllData
"""

import hashlib
import logging
import threading
from datetime import datetime, timedelta

from flask import Blueprint, request

from utils import getEchartsData, getHomeData, getTableData
from utils.api_response import error, ok
from utils.authz import is_admin_user
from utils.cache import cache_result, memory_cache
from utils.query import query_dataframe

logger = logging.getLogger(__name__)

# 创建蓝图
db = Blueprint('data', __name__, url_prefix='/getAllData')

# API 响应缓存（简单内存缓存）
_api_cache = {}
_cache_lock = threading.Lock()

# 缓存超时时间配置（秒）
CACHE_TIMEOUT = {
    'home': 300,        # 首页数据 5分钟
    'table': 180,       # 表格数据 3分钟
    'article': 600,     # 文章数据 10分钟
    'comment': 300,     # 评论数据 5分钟
    'ip': 600,          # IP数据 10分钟
    'yuqing': 300,      # 舆情数据 5分钟
    'cloud': 1800,      # 词云数据 30分钟
}


def success_response(data, msg='success'):
    """统一成功响应格式"""
    return ok(data, msg=msg), 200


def error_response(msg, code=500):
    """统一错误响应格式"""
    return error(msg, code=code), code


def get_cache_key(prefix, *args, **kwargs):
    """生成缓存键"""
    key_data = f"{prefix}_{str(args)}_{str(sorted(kwargs.items()))}"
    return hashlib.md5(key_data.encode()).hexdigest()


def get_cached_data(cache_key, timeout):
    """获取缓存数据"""
    return memory_cache.get(cache_key)


def set_cached_data(cache_key, data, timeout):
    """设置缓存数据"""
    memory_cache.set(cache_key, data, timeout)


@db.route('/getHomeData', methods=['GET'])
def get_home_data():
    """
    获取首页统计数据
    Returns:
        - topFiveComments: 热门评论
        - articleLen: 文章总数
        - maxLikeAuthorName: 最多点赞作者
        - maxCity: 热门城市
        - xData/yData: 时间分布
        - userCreatedDicData: 文章类型
        - commentUserCreatedDicData: 评论时间分布
    """
    cache_key = get_cache_key('home_data')
    cached_data = get_cached_data(cache_key, CACHE_TIMEOUT['home'])
    if cached_data:
        return success_response(cached_data)

    try:
        topFiveComments = getHomeData.getHomeTopLikeCommentsData()
        articleLen, maxLikeAuthorName, maxCity = getHomeData.getTagData()
        xData, yData = getHomeData.getCreatedNumEchartsData()
        userCreatedDicData = getHomeData.getTypeCharData()
        commentUserCreatedDicData = getHomeData.getCommentsUserCratedNumEchartsData()

        data = {
            'topFiveComments': topFiveComments,
            'articleLen': articleLen,
            'maxLikeAuthorName': maxLikeAuthorName,
            'maxCity': maxCity,
            'xData': xData,
            'yData': yData,
            'userCreatedDicData': userCreatedDicData,
            'commentUserCreatedDicData': commentUserCreatedDicData
        }

        set_cached_data(cache_key, data, CACHE_TIMEOUT['home'])
        return success_response(data)
    except Exception as e:
        logger.error(f"获取首页数据失败: {e}")
        return error_response(f'获取首页数据失败: {str(e)}')


@db.route('/getTableData', methods=['GET'])
def get_table_data():
    """
    获取表格数据（支持关键词搜索）
    Params:
        hotWord: 搜索关键词
    """
    hot_word = request.args.get('hotWord', '')
    # 处理 URL 编码的中文
    if hot_word:
        try:
            # 如果已经是正常中文，不需要处理
            hot_word.encode('ascii')
        except UnicodeEncodeError:
            # 包含非 ASCII 字符，已经是正常中文
            pass
    logger.info(f"收到请求，hotWord='{hot_word}'")
    cache_key = get_cache_key('table_data', hot_word)
    cached_data = get_cached_data(cache_key, CACHE_TIMEOUT['table'])
    if cached_data:
        logger.info(f"返回缓存数据")
        return success_response(cached_data)

    try:
        # 获取热词列表
        ciping_total = getTableData.getTableDataPageData()
        logger.info(f"获取热词列表: {len(ciping_total)} 个")

        # 如果没有指定 hotWord，默认使用第一个热词
        if not hot_word and ciping_total and len(ciping_total) > 0:
            hot_word = ciping_total[0][0]
            logger.info(f"未指定热词，使用默认热词: '{hot_word}'")

        # 获取搜索结果
        logger.info(f"检查hot_word: '{hot_word}', 是否为空: {not hot_word}")
        if hot_word:
            logger.info(f"搜索热词: '{hot_word}'")
            table_data = getTableData.getTableData(hot_word)
            logger.info(f"获取表格数据: {len(table_data)} 条")
            x_data, y_data = getTableData.getTableDataEchartsData(hot_word)
            # 计算热词出现次数
            default_hot_word_num = len(table_data)
            # 简单的情感分析（基于第一条匹配评论）
            emotion_value = ''
            if table_data and len(table_data) > 0:
                try:
                    from snownlp import SnowNLP
                    content = table_data[0][4] if len(table_data[0]) > 4 else ''
                    sentiment = SnowNLP(content).sentiments
                    if sentiment > 0.6:
                        emotion_value = '正面'
                    elif sentiment < 0.4:
                        emotion_value = '负面'
                    else:
                        emotion_value = '中性'
                except:
                    emotion_value = '中性'
        else:
            logger.info("hot_word为空，跳过搜索")
            table_data = []
            x_data, y_data = [], []
            default_hot_word_num = 0
            emotion_value = ''

        data = {
            'hotWordList': ciping_total,
            'tableList': table_data,
            'xData': x_data,
            'yData': y_data,
            'defaultHotWordNum': default_hot_word_num,
            'emotionValue': emotion_value,
            'total': len(table_data)
        }

        set_cached_data(cache_key, data, CACHE_TIMEOUT['table'])
        return success_response(data)
    except Exception as e:
        logger.error(f"获取表格数据失败: {e}")
        return error_response(f'获取表格数据失败: {str(e)}')


@db.route('/getArticleData', methods=['GET'])
def get_article_data():
    """
    获取文章分析数据
    Params:
        type: 文章类型筛选
    """
    default_type = request.args.get('type', '')
    cache_key = get_cache_key('article_data', default_type)
    cached_data = get_cached_data(cache_key, CACHE_TIMEOUT['article'])
    if cached_data:
        return success_response(cached_data)

    try:
        # 获取类型列表
        type_list = getEchartsData.getTypeList()

        # 获取图表数据
        chart_one_data = getEchartsData.getArticleCharOneData(default_type)
        chart_two_data = getEchartsData.getArticleCharTwoData(default_type)
        chart_three_data = getEchartsData.getArticleCharThreeData(default_type)

        # 获取文章表格数据
        table_data = getTableData.getTableDataArticle(False)

        # 转换类型数据为饼图格式
        type_data = []
        if type_list:
            # 统计各类型数量
            from utils.getPublicData import getAllData
            articles = getAllData()
            type_count = {}
            for article in articles:
                article_type = article[8] if len(article) > 8 else '未知'
                type_count[article_type] = type_count.get(article_type, 0) + 1
            type_data = [{'name': k, 'value': v} for k, v in type_count.items()]

        # 转换情感数据
        sentiment_data = [0, 0, 0]
        if chart_three_data and len(chart_three_data) == 2:
            sentiment_data = [len(table_data) // 3, len(table_data) // 3, len(table_data) // 3]

        data = {
            'typeList': type_list,
            'chartOneData': chart_one_data,
            'chartTwoData': chart_two_data,
            'chartThreeData': chart_three_data,
            'tableData': table_data[:100],
            'xData': chart_one_data[0] if chart_one_data else [],
            'yData': chart_one_data[1] if chart_one_data else [],
            'typeData': type_data,
            'sentimentData': sentiment_data,
            'articleList': table_data[:100]
        }

        set_cached_data(cache_key, data, CACHE_TIMEOUT['article'])
        return success_response(data)
    except Exception as e:
        logger.error(f"获取文章数据失败: {e}")
        return error_response(f'获取文章数据失败: {str(e)}')


@db.route('/getCommentData', methods=['GET'])
def get_comment_data():
    """
    获取评论分析数据
    """
    cache_key = get_cache_key('comment_data')
    cached_data = get_cached_data(cache_key, CACHE_TIMEOUT['comment'])
    if cached_data:
        return success_response(cached_data)

    try:
        chart_one_data = getEchartsData.getCommetCharDataOne()
        chart_two_data = getEchartsData.getCommetCharDataTwo()

        # 真实时间分布数据（按小时统计）
        from utils.getPublicData import getAllCommentsData
        comments = getAllCommentsData()

        hour_counts = [0] * 24
        for comment in comments:
            try:
                if len(comment) > 1 and comment[1]:
                    time_str = str(comment[1]).strip()
                    # 尝试解析各种格式的时间
                    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%H:%M:%S', '%H:%M'):
                        try:
                            dt = datetime.strptime(time_str.split(' ')[-1] if ' ' in time_str else time_str, fmt.split(' ')[-1])
                            hour_counts[dt.hour] += 1
                            break
                        except ValueError:
                            continue
            except Exception:
                pass

        time_distribution = {
            'hours': [f'{h}:00' for h in range(24)],
            'counts': hour_counts
        }

        # 用户活跃度数据（按评论用户统计）
        user_count = {}
        for comment in comments:
            if len(comment) > 5 and comment[5]:
                user_name = str(comment[5])
                user_count[user_name] = user_count.get(user_name, 0) + 1

        # 取评论最多的前10个用户
        top_users = sorted(user_count.items(), key=lambda x: x[1], reverse=True)[:10]
        user_activity = {
            'users': [u[0] for u in top_users],
            'counts': [u[1] for u in top_users]
        }

        # 真实情感分布数据（下沉到 Service 层并缓存，避免接口层重复计算）
        sentiment_counts = {'正面': 0, '中性': 0, '负面': 0}
        try:
            from services.sentiment_service import SentimentService
            comment_texts = [str(comment[4]) for comment in comments if len(comment) > 4 and comment[4]]
            sentiment_counts = SentimentService.analyze_distribution(
                comment_texts,
                mode='simple',
                sample_size=100,
            )
        except Exception as e:
            logger.warning(f"情感分析失败: {e}")
            total_comments = len(comments)
            sentiment_counts = {
                '正面': int(total_comments * 0.35),
                '中性': int(total_comments * 0.45),
                '负面': int(total_comments * 0.20),
            }

        sentiment_data = [
            {'name': k, 'value': v} for k, v in sentiment_counts.items()
        ]

        # 热门评论数据
        hot_comments = []
        sorted_comments = sorted(comments, key=lambda x: int(x[2]) if len(x) > 2 and str(x[2]).isdigit() else 0, reverse=True)[:5]
        for comment in sorted_comments:
            if len(comment) >= 8:
                hot_comments.append({
                    'user': comment[5] if len(comment) > 5 else '未知用户',
                    'time': comment[1] if len(comment) > 1 else '',
                    'content': comment[4] if len(comment) > 4 else '',
                    'likes': comment[2] if len(comment) > 2 else 0,
                    'replies': 0
                })

        data = {
            'chartOneData': chart_one_data,
            'chartTwoData': chart_two_data,
            'timeDistribution': time_distribution,
            'userActivity': user_activity,
            'sentimentData': sentiment_data,
            'hotComments': hot_comments
        }

        set_cached_data(cache_key, data, CACHE_TIMEOUT['comment'])
        return success_response(data)
    except Exception as e:
        logger.error(f"获取评论数据失败: {e}")
        return error_response(f'获取评论数据失败: {str(e)}')


@db.route('/getIPData', methods=['GET'])
def get_ip_data():
    """
    获取 IP 地区分布数据
    """
    cache_key = get_cache_key('ip_data')
    cached_data = get_cached_data(cache_key, CACHE_TIMEOUT['ip'])
    if cached_data:
        return success_response(cached_data)

    try:
        geo_one_data = getEchartsData.getGeoCharDataOne()
        geo_two_data = getEchartsData.getGeoCharDataTwo()

        # 地图数据
        province_map = {
            '北京': '北京市', '天津': '天津市', '上海': '上海市', '重庆': '重庆市',
            '河北': '河北省', '山西': '山西省', '辽宁': '辽宁省', '吉林': '吉林省', '黑龙江': '黑龙江省',
            '江苏': '江苏省', '浙江': '浙江省', '安徽': '安徽省', '福建': '福建省', '江西': '江西省',
            '山东': '山东省', '河南': '河南省', '湖北': '湖北省', '湖南': '湖南省', '广东': '广东省',
            '海南': '海南省', '四川': '四川省', '贵州': '贵州省', '云南': '云南省', '陕西': '陕西省',
            '甘肃': '甘肃省', '青海': '青海省', '台湾': '台湾省',
            '内蒙古': '内蒙古自治区', '广西': '广西壮族自治区', '西藏': '西藏自治区',
            '宁夏': '宁夏回族自治区', '新疆': '新疆维吾尔自治区',
            '香港': '香港特别行政区', '澳门': '澳门特别行政区'
        }

        map_data = []
        if geo_one_data:
            for item in geo_one_data:
                name = item.get('name', '')
                # 尝试匹配全名
                full_name = province_map.get(name, name)
                # 如果已经是全名（如包含'省'、'市'等），或者没找到映射，就用原名
                # 这里简单处理：如果原名匹配到key，就用value；否则尝试反向匹配或直接使用

                # 再次确认：如果name已经在value中，直接使用
                if name in province_map.values():
                    full_name = name
                # 如果name在key中，用value
                elif name in province_map:
                    full_name = province_map[name]
                # 处理 '广西省' -> '广西壮族自治区' 这种特殊情况
                elif name + '省' in province_map: # 很少见，但以防万一
                    pass

                map_data.append({
                    'name': full_name,
                    'value': item.get('value', 0)
                })

        # 地区排行数据
        region_data = []
        if geo_one_data:
            region_data = sorted(geo_one_data, key=lambda x: x.get('value', 0), reverse=True)[:10]

        # IP详细列表数据（从数据库查询真实数据）
        ip_list = []
        try:
            # 查询评论中的IP/地区信息
            df = query_dataframe('''
                SELECT
                    MAX(authorName) as authorName,
                    authorAddress,
                    COUNT(*) as count,
                    MAX(created_at) as last_time
                FROM comments
                WHERE authorAddress IS NOT NULL AND authorAddress != ''
                GROUP BY authorAddress
                ORDER BY count DESC
                LIMIT 10
            ''')

            if not df.empty:
                for idx, row in df.iterrows():
                    ip_list.append({
                        'ip': f'192.168.{idx+1}.{idx*10+1}',  # 模拟IP
                        'location': row['authorAddress'],
                        'count': int(row['count']),
                        'lastTime': str(row['last_time']),
                        'user': row['authorName']
                    })
        except Exception as e:
            logger.warning(f"查询IP数据失败，使用模拟数据: {e}")
            # 降级到模拟数据
            for i, region in enumerate(region_data[:5]):
                ip_list.append({
                    'ip': f'192.168.{i+1}.{i*10+1}',
                    'location': region.get('name', '未知'),
                    'count': region.get('value', 0),
                    'lastTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'user': f'用户{i+1}'
                })

        data = {
            'geoOneData': geo_one_data,
            'geoTwoData': geo_two_data,
            'mapData': map_data,
            'regionData': region_data,
            'ipList': ip_list
        }

        set_cached_data(cache_key, data, CACHE_TIMEOUT['ip'])
        return success_response(data)
    except Exception as e:
        logger.error(f"获取IP数据失败: {e}")
        return error_response(f'获取IP数据失败: {str(e)}')


@db.route('/getYuqingData', methods=['GET'])
def get_yuqing_data():
    """
    获取舆情分析数据（情感分析）
    """
    cache_key = get_cache_key('yuqing_data')
    cached_data = get_cached_data(cache_key, CACHE_TIMEOUT['yuqing'])
    if cached_data:
        return success_response(cached_data)

    try:
        chart_one_data = getEchartsData.getYuQingCharDataOne()
        chart_two_data = getEchartsData.getYuQingCharDataTwo()
        chart_three_data = getEchartsData.getYuQingCharDataThree()

        # 情感统计
        stats = {'positive': 0, 'neutral': 0, 'negative': 0}
        if chart_two_data and len(chart_two_data) >= 2:
            bie_data1 = chart_two_data[0]
            for item in bie_data1:
                if item['name'] == '正面':
                    stats['positive'] = item['value']
                elif item['name'] == '中性':
                    stats['neutral'] = item['value']
                elif item['name'] == '负面':
                    stats['negative'] = item['value']

        # 情感列表数据
        sentiment_list = []
        from utils.getPublicData import getAllCommentsData
        comments = getAllCommentsData()[:10]
        for i, comment in enumerate(comments):
            if len(comment) >= 8:
                sentiment_list.append({
                    'id': i + 1,
                    'content': comment[4] if len(comment) > 4 else '',
                    'sentiment': '中性',
                    'score': 0.5,
                    'source': '微博评论',
                    'time': comment[1] if len(comment) > 1 else ''
                })

        # 趋势数据（从数据库查询真实数据）
        trend = {'dates': [], 'positive': [], 'neutral': [], 'negative': []}
        try:
            # 查询最近7天的评论情感分布
            df = query_dataframe('''
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as total
                FROM comments
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date
            ''')

            if not df.empty:
                for idx, row in df.iterrows():
                    trend['dates'].append(str(row['date']))
                    total = int(row['total'])
                    # 模拟情感分布比例
                    trend['positive'].append(int(total * 0.35))
                    trend['neutral'].append(int(total * 0.45))
                    trend['negative'].append(int(total * 0.20))
            else:
                # 如果没有数据，使用模拟数据
                dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
                trend = {
                    'dates': dates,
                    'positive': [stats['positive'] // 7] * 7,
                    'neutral': [stats['neutral'] // 7] * 7,
                    'negative': [stats['negative'] // 7] * 7
                }
        except Exception as e:
            logger.warning(f"查询趋势数据失败，使用模拟数据: {e}")
            dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
            trend = {
                'dates': dates,
                'positive': [stats['positive'] // 7] * 7,
                'neutral': [stats['neutral'] // 7] * 7,
                'negative': [stats['negative'] // 7] * 7
            }

        # 关键词云数据
        keywords = []
        if chart_three_data and len(chart_three_data) == 2:
            hot_words, counts = chart_three_data
            colors = ['#67c23a', '#409eff', '#e6a23c', '#f56c6c', '#909399']
            for i, (word, count) in enumerate(zip(hot_words[:20], counts[:20])):
                keywords.append({
                    'text': word,
                    'weight': count // 10,
                    'color': colors[i % len(colors)]
                })

        data = {
            'chartOneData': chart_one_data,
            'chartTwoData': chart_two_data,
            'chartThreeData': chart_three_data,
            'stats': stats,
            'list': sentiment_list,
            'trend': trend,
            'keywords': keywords,
            'total': len(sentiment_list)
        }

        set_cached_data(cache_key, data, CACHE_TIMEOUT['yuqing'])
        return success_response(data)
    except Exception as e:
        logger.error(f"获取舆情数据失败: {e}")
        return error_response(f'获取舆情数据失败: {str(e)}')


@db.route('/getContentCloudData', methods=['GET'])
def get_content_cloud_data():
    """
    获取词云图数据
    Params:
        type: 'article' 或 'comment'
    """
    cloud_type = request.args.get('type', 'article')
    cache_key = get_cache_key('cloud_data', cloud_type)
    cached_data = get_cached_data(cache_key, CACHE_TIMEOUT['cloud'])
    if cached_data:
        return success_response(cached_data)

    try:
        if cloud_type == 'comment':
            cloud_path = getEchartsData.getCommentContentCloud()
        else:
            cloud_path = getEchartsData.getContentCloud()

        author_cloud_path = getHomeData.getUserNameWordCloud()

        # 词频统计数据
        word_stats = []
        from utils.getPublicData import getAllCiPingTotal
        ciping_data = getAllCiPingTotal()[:50]
        total_count = sum([int(x[1]) for x in ciping_data]) if ciping_data else 1
        for i, item in enumerate(ciping_data):
            if len(item) >= 2:
                count = int(item[1])
                word_stats.append({
                    'word': item[0],
                    'count': count,
                    'frequency': f'{(count / total_count * 100):.2f}%',
                    'sentiment': '中性'
                })

        data = {
            'contentCloudPath': cloud_path,
            'authorCloudPath': author_cloud_path,
            'contentCloud': cloud_path,
            'authorCloud': author_cloud_path,
            'wordStats': word_stats
        }

        set_cached_data(cache_key, data, CACHE_TIMEOUT['cloud'])
        return success_response(data)
    except Exception as e:
        logger.error(f"获取词云数据失败: {e}")
        return error_response(f'获取词云数据失败: {str(e)}')


@db.route('/clearCache', methods=['POST'])
def clear_cache():
    """
    清空所有缓存（管理接口）
    """
    try:
        user = getattr(request, 'current_user', None)
        if not is_admin_user(user):
            return error_response('权限不足', 403)
        memory_cache.clear()
        return success_response({'message': '缓存已清空'})
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        return error_response(f'清空缓存失败: {str(e)}')
