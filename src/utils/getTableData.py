import logging
from datetime import datetime

from snownlp import SnowNLP

from utils.getPublicData import getAllCiPingTotal, getAllCommentsData, getAllData
from utils.query import query_dataframe

logger = logging.getLogger(__name__)


def _extract_date_part(value):
    """从时间字符串中提取 YYYY-MM-DD 日期部分，失败返回 None。"""
    if value is None:
        return None

    date_part = str(value).strip().split(" ")[0]
    try:
        datetime.strptime(date_part, "%Y-%m-%d")
        return date_part
    except ValueError:
        logger.debug(f"跳过无效日期格式: {value}")
        return None


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
        df = query_dataframe(
            """
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
        """,
            params=(f"%{hotWord}%",),
        )

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
    # 先统计每日条数，避免后续频繁 index 查找导致 O(n^2)
    date_count = {}
    for comment in tableList:
        if not (
            isinstance(comment, (list, tuple))
            and len(comment) > 1
        ):
            continue
        date_part = _extract_date_part(comment[1])
        if not date_part:
            continue
        date_count[date_part] = date_count.get(date_part, 0) + 1

    if not date_count:
        return [], []

    try:
        xData = sorted(
            date_count.keys(),
            key=lambda x: datetime.strptime(x, "%Y-%m-%d").timestamp(),
            reverse=True,
        )
    except ValueError as e:
        logger.warning(f"日期排序失败: {e}")
        return [], []

    yData = [date_count.get(day, 0) for day in xData]
    return xData, yData


def getTableDataArticle(flag):
    if flag:
        tableListOld = getAllData()
        tableList = []
        for item in tableListOld:
            item = list(item)
            emotionValue = SnowNLP(item[5]).sentiments
            if emotionValue > 0.5:
                emotionValue = "正面"
            elif emotionValue == 0.5:
                emotionValue = "中性"
            elif emotionValue < 0.5:
                emotionValue = "负面"
            item.append(emotionValue)
            tableList.append(item)
    else:
        tableList = getAllData()
    return tableList
