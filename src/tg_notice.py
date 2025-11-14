import requests
from dotenv import load_dotenv
import os
from config import logger
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()
TOKEN = os.getenv('TG_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def send_telegram(message):
    '''发送通知至telegram机器人'''
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
        logger.info("消息发送成功")
    except Exception as e:
        logger.warn("发送失败:", e)


