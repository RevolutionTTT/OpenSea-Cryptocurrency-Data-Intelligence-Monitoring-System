import schedule
import time
from datetime import datetime
import sys
import subprocess
import config
from config import logger
import random
from tg_notice import send_telegram

excute_time = config.scheduler_config['excute_time']
exit_time = config.scheduler_config['exit_time']
crawler_process = None

def run_crawler():
    """执行爬虫程序"""
    for i in range(10):  # 重试
        try:
            logger.info(f"执行爬虫任务 (第{i+1}次尝试)")
            crawler_process = subprocess.Popen([sys.executable, "crawler.py"])
            crawler_process.wait()
            if crawler_process.returncode == 0:
                logger.info("爬虫任务成功")
                return
            else:
                raise Exception("爬虫执行失败")
        except Exception as e:
            logger.error(f"尝试{i+1}失败: {e}")
            if i < 9:  # 不是最后一次
                time.sleep(random.uniform(10,15))  # 等待5秒重试
            else:
                send_telegram("以达到最大重试次数")

def main():
    schedule.every().day.at(excute_time).do(run_crawler)
    message = f"调度器启动，执行时间: {excute_time}"
    logger.info(message)
    send_telegram(message)

    try:
        while True:
            current_time = datetime.now().strftime("%H:%M")
            if current_time == exit_time:
                message = f"到达退出时间 {exit_time}"
                logger.info(message)
                send_telegram(message)
                if crawler_process:
                    crawler_process.terminate()
                break
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        if crawler_process:
            crawler_process.terminate()

if __name__ == "__main__":
    main()