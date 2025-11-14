import pymysql
from pymysql.cursors import DictCursor
import config
from config import logger

def get_connection():
    """按需创建数据库连接，避免模块加载时连接"""
    return pymysql.connect(
        host=config.db_config['host'],
        port=config.db_config['port'],
        user=config.db_config['user'],
        password=config.db_config['password'],
        database=config.db_config['database'],
        charset='utf8mb4',
        cursorclass=DictCursor,
        autocommit=True  # 自动提交
    )


def save_batch(coin_data: list[dict]):
    """使用连接上下文管理"""
    try:
        sql = "INSERT INTO coin_data (symbol, hot_coin_name, coin_price, coin_percent) VALUES (%s, %s, %s, %s)"
        values = []
        for item in coin_data:
            values.append((
                item['symbol'],
                item['hot_coin_name'],
                item['coin_price'],
                item['coin_percent']
            ))

        with get_connection() as conn:  # 使用上下文管理器
            with conn.cursor() as cursor:
                cursor.executemany(sql,values)
        logger.info(f"成功插入{len(coin_data)}条数据")

    except Exception as e:
        logger.error(f"数据库插入失败: {e}")
        # 可以考虑添加重试逻辑或降级方案（如保存到文件）

