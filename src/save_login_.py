from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent
import config
from config import logger
STORAGE_FILE = config.crawler_config["storage_file"]
ua = UserAgent()
def playwright_access():
     with sync_playwright() as p:
        browser =  p.chromium.launch(headless=False)
        context =  browser.new_context(user_agent=ua.random)
        page =  context.new_page()
        # 设置额外的headers
        page.set_extra_http_headers(config.crawler_config['extra_headers'])
        # 导航到页面
        page.goto(config.crawler_config['url'],wait_until='networkidle')
        # 等待页面加载完成
        page.wait_for_selector('body',timeout=config.crawler_config['timeout'])
        logger.info("请手动完成登录，登录完成后按 Enter 继续...")
        input()  # 等待登录
        # 登录完成后保存浏览器状态
        try:
            context.storage_state(path=STORAGE_FILE)
            logger.info(f"登录信息已保存到 {STORAGE_FILE}")
        except Exception as e:
            logger.warning(e)
        browser.close()
def main():
    playwright_access()
if __name__ == "__main__":
    main()




