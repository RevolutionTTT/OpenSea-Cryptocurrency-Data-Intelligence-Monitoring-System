from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent
from lxml import etree
import random
import time
import config
import storage
from config import logger
from tenacity import retry, stop_after_attempt, wait_fixed # 导入重试库
from tg_notice import send_telegram
#目前1161条数据
ua = UserAgent()#请求头轮换
storage_file = config.crawler_config["storage_file"]# 登录信息
dashboard_url = config.crawler_config["dashboard_url"]# 目标网站
def like_human(a,b):
    '''模拟人类'''
    time.sleep(random.uniform(a, b))

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1.5))
def get_html_tree(page):
    '''获取网页内容'''
    html = page.content()
    return etree.HTML(html)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1.5))
def get_name(tree):
    try:
        '''获取代币名'''
        hot_coin_names = tree.xpath("//div[@class='flex *:last:!mr-0 pl-4 md:pl-6 lg:pl-0']//span[@class='leading-normal text-text-primary text-sm']")
        HOT_COIN_NAMES = []
        for hot_coin_name in hot_coin_names:
            if hot_coin_name is None:
                hot_coin_name = 'none'
            HOT_COIN_NAMES.append(hot_coin_name.text)
        logger.info(HOT_COIN_NAMES)
        return HOT_COIN_NAMES
    except Exception as e:
        logger.error(e)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1.5))
def get_symbol(tree):
    '''获取简称'''
    try:
        symbols = tree.xpath("//div[@class='flex *:last:!mr-0 pl-4 md:pl-6 lg:pl-0']//span[@class='leading-normal font-normal text-text-secondary text-sm']")
        SYMBOL = []
        for symbol in symbols:
            SYMBOL.append(symbol.text if symbol is not None and symbol.text else 'none')
        logger.info(SYMBOL)
        return SYMBOL
    except Exception as e:
        logger.error(e)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(random.uniform(1.6,2)))
def get_button(page):
    '''点击按钮元素渲染页面'''
    try:
        button = page.locator("button.inline-flex.rounded-full.bg-bg-primary[aria-label='Next']")
        for _ in range(3):  # 点击3次
            like_human(2,3)
            button.first.click()
            logger.info('点击成功')
    except Exception as e:
        logger.warning(e)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1.5))
def get_price(page):
    try:
        '''获取价格'''
        selector = "//div[@class='flex w-full gap-3 p-0 items-stretch rounded-lg border border-border-1-transparent bg-bg-primary-transparent pr-4 text-text-primary duration-200 ease-out-circ perspective-[0] translate-z-0 backface-hidden hover:-translate-y-0.5 hover:scale-[1.01] active:scale-[1.005] shadow-xs hover:shadow-xs overflow-visible']//span[@class='font-mono']"
        price_elements = page.query_selector_all(f"xpath= {selector} ")
        logger.info(f"找到 {len(price_elements)} 个价格元素")
        coin_price = []
        for i,element in enumerate(price_elements):
            text = element.inner_text().strip() if element else 'none'
            logger.info(f"{i + 1}: {text}")
            coin_price.append(text)
        logger.info(coin_price)
        return coin_price
    except Exception as e:
        logger.error(e)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1.5))
def get_percent_0(tree):
    '''获取百分数的前8个'''
    COIN_PERCENT_0 = []
    percent_selector = "//div[@class='flex *:last:!mr-0 pl-4 md:pl-6 lg:pl-0']//div[@class='max-w-full truncate break-all']//following-sibling::span[@class='font-mono text-success-1 cursor-pointer']"
    coin_percent = tree.xpath(percent_selector)
    for percent in coin_percent:
        logger.info(percent.text)
        COIN_PERCENT_0.append(percent.text if percent is not None and percent.text else 'none')
    return COIN_PERCENT_0

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1.5))
def get_percent(tree,COIN_PERCENT_0: list):
    '''获取涨跌幅'''
    try:
        percent_selector = "//div[@class='flex *:last:!mr-0 pl-4 md:pl-6 lg:pl-0']//div[@class='max-w-full truncate break-all']//following-sibling::span[@class='font-mono text-success-1 cursor-pointer']"
        coin_percent = tree.xpath(percent_selector)
        COIN_PERCENT = []
        for percent in coin_percent:
            logger.info(percent.text)
            COIN_PERCENT.append(percent.text if percent is not None and percent.text else 'none')
        COIN_PERCENT = COIN_PERCENT_0 + COIN_PERCENT[:4]
        logger.info(COIN_PERCENT)
        return COIN_PERCENT
    except Exception as e:
        logger.error(e)

def organize_dict(SYMBOL: list ,HOT_COIN_NAMES: list,coin_price: list,COIN_PERCENT: list):
    '''整理数据'''
    try:
        coin_data = []
        for coin_index in range(len(SYMBOL)):
            coin_dict = {
                'symbol': SYMBOL[coin_index],
                'hot_coin_name': HOT_COIN_NAMES[coin_index],
                'coin_price': coin_price[coin_index],
                'coin_percent': COIN_PERCENT[coin_index]
            }
            coin_data.append(coin_dict)
        logger.info(f"总共收集到 {len(coin_data)} 个代币数据:{coin_data}")
        return coin_data
    except Exception as e:
        logger.error(e)

def crawler_main(p):
        try:
            browser = p.chromium.launch(headless=True)
            # 使用已保存的登录状态创建浏览器上下文
            context = browser.new_context(user_agent=ua.random,storage_state=storage_file)

            page = context.new_page()
            # 设置额外的headers
            page.set_extra_http_headers(config.crawler_config['extra_headers'])
            # 直接访问登录后页面
            page.goto(dashboard_url,timeout=config.crawler_config["timeout"])
            logger.info('任务启动中...')
            send_telegram("循环任务开始...")
            while True:
                # 等待页面加载完成，可以考虑'networkidle'
                page.wait_for_load_state(timeout=config.crawler_config["timeout"])
                like_human(2,3)
                tree = get_html_tree(page)
                HOT_COIN_NAMES= get_name(tree)#获取代币名
                SYMBOL = get_symbol(tree)#获取代币简称
                COIN_PERCENT_0 = get_percent_0(tree)#获取百分数的前8个
                get_button(page)
                page.wait_for_load_state('networkidle')
                coin_price = get_price(page)#获取价格
                tree = get_html_tree(page)# 按钮点击后tree对象更新，需重新获取
                COIN_PERCENT = get_percent(tree,COIN_PERCENT_0)#获取完整百分数
                #整理数据
                coin_data = organize_dict(SYMBOL,HOT_COIN_NAMES,coin_price,COIN_PERCENT)
                storage.save_batch(coin_data)#保存至数据库
                # page.evaluate("window.location.reload(true)")#刷新页面，确保数据更新
                page.reload(wait_until='networkidle',timeout=config.crawler_config["timeout"])
                page.wait_for_load_state('networkidle')
                page.screenshot(path="../screen/screenshot.png")
                # 等待几分钟
                time.sleep(random.uniform(18,30))  # 毫秒单位
        except Exception as e:
            logger.error(e)
            send_telegram("爬虫任务运行失败")

def main():
    with sync_playwright() as p:
        crawler_main(p)
if __name__ == "__main__":
    main()