"""
数据库访问模块
唯一数据访问层：SQLAlchemy engine + scoped_session
"""
from __future__ import annotations

import logging
import time
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

from config.settings import Config

logger = logging.getLogger(__name__)

# ── 唯一连接池：SQLAlchemy engine ──────────────────────────────────────────
engine = create_engine(
    Config.get_database_url(),
    pool_size=Config.DB_POOL_SIZE,
    max_overflow=20,
    pool_recycle=Config.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    pool_timeout=Config.DB_POOL_TIMEOUT,
    echo=Config.IS_DEVELOPMENT,
)

db_session = scoped_session(sessionmaker(bind=engine))


# ── 兼容旧调用的查询函数 ───────────────────────────────────────────────────

def querys(sql: str, params: list | None = None, type: str = "no_select") -> Any:
    """
    执行 SQL 语句，兼容旧调用签名。

    Args:
        sql: SQL 语句（支持 %s 占位符）
        params: 参数列表
        type: 'no_select' 表示写操作，其他值表示 SELECT

    Returns:
        SELECT 返回字典列表；写操作返回 '数据库语句执行成功'
    """
    if params is None:
        params = []

    start = time.time()
    # 将 pymysql 风格的位置占位符 %s 替换为 SQLAlchemy 命名参数 :p0, :p1, ...
    # 注意：此替换基于字符串匹配，不解析 SQL 语法。
    # 若 SQL 字符串字面量中包含 %s（如 LIKE '%s%'），请改用 :param 风格直接传入。
    named_params = {f"p{i}": v for i, v in enumerate(params)}
    named_sql = sql
    for i in range(len(params)):
        named_sql = named_sql.replace("%s", f":p{i}", 1)

    with engine.connect() as conn:
        result = conn.execute(text(named_sql), named_params)
        if type != "no_select":
            rows = [dict(row._mapping) for row in result]
            logger.debug("查询完成: %d 条记录, 耗时 %.3fs", len(rows), time.time() - start)
            return rows
        else:
            conn.commit()
            logger.debug("写操作完成: 影响 %d 行, 耗时 %.3fs", result.rowcount, time.time() - start)
            return "数据库语句执行成功"


def query_dataframe(sql: str, params: list | None = None) -> pd.DataFrame:
    """
    执行查询并返回 pandas DataFrame。

    Args:
        sql: SQL 语句
        params: 参数列表

    Returns:
        DataFrame，失败时返回空 DataFrame
    """
    start = time.time()
    try:
        if params:
            named_params = {f"p{i}": v for i, v in enumerate(params)}
            named_sql = sql
            for i in range(len(params)):
                named_sql = named_sql.replace("%s", f":p{i}", 1)
            df = pd.read_sql(text(named_sql), engine, params=named_params)
        else:
            df = pd.read_sql(sql, engine)
        logger.debug("DataFrame 查询完成: %d 行, 耗时 %.3fs", len(df), time.time() - start)
        return df
    except Exception as e:
        logger.error("DataFrame 查询错误: %s", e, exc_info=True)
        return pd.DataFrame()


def get_database_stats() -> dict:
    """返回连接池状态（兼容旧调用）"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
    }
