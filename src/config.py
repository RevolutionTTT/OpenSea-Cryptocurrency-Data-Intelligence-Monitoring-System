import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()
# 数据库配置
db_config = {
    'host':os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),  # 生产环境
    'database': os.getenv('DB_NAME')
}

# 爬虫配置
crawler_config = {
    'storage_file': "storage_state.json",
    'dashboard_url': "https://opensea.io/zh-CN/",
    'url': 'https://opensea.io/zh-CN/profile',
    'timeout': 60000,
    'extra_headers': {
        'sec-ch-ua': '"Chromium";v="141", "Not?A_Brand";v="8"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
}

scheduler_config = {
    'excute_time': "6:12",  # 固定执行时间
    'exit_time': "7:20"
}


# 正确的日志配置
def setup_logging():
    """设置日志配置，避免重复添加handler"""
    logger = logging.getLogger(__name__)

    # 如果已经配置过handler，直接返回
    if logger.handlers:
        return logger

    # 创建日志目录
    log_dir = "../log"
    os.makedirs(log_dir,exist_ok=True)
    log_file = os.path.join(log_dir,"crawler.log")

    # 设置日志级别
    logger.setLevel(logging.INFO)

    # 避免日志向上传播到root logger导致重复输出
    logger.propagate = False

    # 创建formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 文件handler - 使用追加模式，并设置日志轮转
    file_handler = RotatingFileHandler(
        log_file,
        mode='a',  # 追加模式
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=2,  # 保留2个备份
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # 添加handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 初始化logger
logger = setup_logging()

# 测试日志
if __name__ == "__main__":
    logger.info(db_config)
