import schedule
import time
from datetime import datetime
import sys
import subprocess
import config
from config import logger
from tg_notice import send_telegram
excute_time = config.scheduler_config['excute_time'] # 固定执行时间
exit_time = config.scheduler_config['exit_time'] # 退出时间

# 记录爬虫进程
crawler_process = None

def run_crawler():
    """执行爬虫程序"""
    try:
        global crawler_process
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"开始执行爬虫任务 - {current_time}")

        # 启动爬虫进程
        crawler_process = subprocess.Popen([sys.executable,"crawler.py"])
        logger.info(f"爬虫进程已启动: {crawler_process.pid}")
    except Exception as e:
        logger.error(e)

def main():
    # 设置固定时间执行
    try:
        schedule.every().day.at(excute_time).do(run_crawler)
        message = f"爬虫调度器已启动，将在以下时间执行: {excute_time}"
        logger.info(message)
        send_telegram(message)
    except:
        message = "爬虫运行失败"
        logger.warning(message)
        send_telegram(message)
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M")
            # 检查是否到达退出时间
            if current_time == exit_time:
                message = f"到达退出时间 {exit_time}，程序退出"
                logger.info(message)
                send_telegram(message)
                # 终止爬虫进程
                if crawler_process and crawler_process.poll() is None:
                    crawler_process.terminate()
                break
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warn(f"手动停止了调度器")
        # 终止爬虫进程
        if crawler_process and crawler_process.poll() is None:
            crawler_process.terminate()


if __name__ == "__main__":
    main()
