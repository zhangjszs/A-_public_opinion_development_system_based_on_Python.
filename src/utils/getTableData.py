from utils.getPublicData import *
from datetime import datetime
from snownlp import SnowNLP
from utils.query import query_dataframe
import logging

logger = logging.getLogger(__name__)


def getTableDataPageData():
    return getAllCiPingTotal()


def getTableData(hotWord):
    """
    根据关键词获取评论数据（优化版：使用数据库查询代替Python过滤）
    
    Args:
        hotWord: 搜索关键词
        
    Returns:
        list: 匹配的评论列表
    """
    try:
        # 使用参数化查询在数据库层面进行过滤，避免N+1查询问题
        # 使用LIKE进行模糊匹配，并限制返回数量
        # MySQL使用%s作为占位符
        # 只查询数据库中实际存在的字段
        df = query_dataframe('''
            SELECT 
                articleId,
                created_at,
                like_counts,
                region,
                content,
                authorName,
                authorGender,
                authorAddress,
                authorAvatar
            FROM comments 
            WHERE content LIKE %s
            ORDER BY created_at DESC
            LIMIT 1000
        ''', params=(f'%{hotWord}%',))
        
        # 转换为列表格式以保持向后兼容
        if df.empty:
            logger.info(f"未找到包含关键词 '{hotWord}' 的评论")
            return []
        
        logger.info(f"找到 {len(df)} 条包含关键词 '{hotWord}' 的评论")
        return df.values.tolist()
        
    except Exception as e:
        logger.error(f"查询评论数据失败: {e}")
        # 降级到原始方法
        logger.warning("降级到原始查询方法")
        commentList = getAllCommentsData()
        tableData = []
        for comment in commentList:
            if comment[4].find(hotWord) != -1:
                tableData.append(comment)
        return tableData


def getTableDataEchartsData(hotWord):
    tableList = getTableData(hotWord)
    # 提取原始的日期字符串
    raw_xData = [item[1] for item in tableList if
                 isinstance(item, (list, tuple)) and len(item) > 1 and item[1] is not None]  # 增加健壮性检查

    # --- 预处理步骤 ---
    processed_dates = set()
    for date_str in raw_xData:
        if not isinstance(date_str, str):  # 跳过非字符串类型
            print(f"警告：跳过非字符串类型的数据：{date_str}")
            continue
        try:
            # 假设日期是空格前的第一部分
            date_part = date_str.strip().split(' ')[0]
            # 验证这部分是否是有效的 YYYY-MM-DD 格式
            datetime.strptime(date_part, '%Y-%m-%d')
            processed_dates.add(date_part)
        except ValueError:
            # 处理无效格式的字符串
            print(f"警告：跳过无效的日期格式：'{date_str}'")
            pass  # 选择跳过

    xData = list(processed_dates)
    # --- 预处理结束 ---

    # 如果预处理后 xData 为空，直接返回
    if not xData:
        return [], []

    # 现在使用清理过的日期格式进行排序
    try:
        xData = list(sorted(xData, key=lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp(), reverse=True))
    except ValueError as e:
        # 这理论上不应该再发生，但以防万一
        print(f"排序时发生意外错误: {e}")
        return [], []  # 出错时返回空

    # 根据原始 tableList 和处理后的 xData（仅日期）重新计算 yData
    yData = [0 for _ in range(len(xData))]
    for comment in tableList:
        # 确保 comment 结构符合预期且日期数据存在
        if not (isinstance(comment, (list, tuple)) and len(comment) > 1 and isinstance(comment[1], str)):
            continue

        try:
            # 从原始评论数据中提取日期部分进行匹配
            comment_date_part = comment[1].strip().split(' ')[0]
            if comment_date_part in xData:
                idx = xData.index(comment_date_part)
                yData[idx] += 1
        except ValueError:
            # 忽略 tableList 中日期格式不符合预期的条目
            pass
    return xData, yData


def getTableDataArticle(flag):
    if flag:
        tableListOld = getAllData()
        tableList = []
        for item in tableListOld:
            item = list(item)
            emotionValue = SnowNLP(item[5]).sentiments
            if emotionValue > 0.5:
                emotionValue = '正面'
            elif emotionValue == 0.5:
                emotionValue = '中性'
            elif emotionValue < 0.5:
                emotionValue = '负面'
            item.append(emotionValue)
            tableList.append(item)
    else:
        tableList = getAllData()
    return tableList
