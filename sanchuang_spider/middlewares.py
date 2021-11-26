# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from sanchuang_spider.settings import USER_AGENT_LIST, Cookies
import time
import random


class SpiderUserAgentMiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        agent = random.choice(list(USER_AGENT_LIST))
        # print("user-agent:", agent)
        request.headers['User-Agent'] = agent
        if spider.name == "SpiderJD" or spider.name == 'JDcomments' or spider.name == 'test':
            # request.headers['referer'] = 'https://search.jd.com/'
            request.headers['cookie'] = Cookies
            # request.headers['accept-language'] = 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
            # print(request.headers)
        if spider.name == "SpiderVip ":
            request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            request.headers['cookies'] = 'vip_cps_cid=1632294601691_4a000a364ee9221cfaa5dde81f83278e; PAPVisitorId=a3171b17fdc42950ae69e0b30f137ddd;'
            request.headers['referer'] = 'https://category.vip.com/'


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        #
        # if request.meta.get('type') == 'price':
        #     return None
        # else:
        proxy = random.choice(PROXIES)
        print("请求ip是：" + proxy)
        request.meta['proxy'] = 'http://' + proxy


class SeleniumMiddleware(object):
    def __init__(self):
        chrome_opt = webdriver.ChromeOptions()
        # chrome_opt.add_argument('--headless')
        prefs = {'profile.managed_default_content_settings.images': 2}  # 不加载图片
        chrome_opt.add_experimental_option('prefs', prefs)
        # chrome_opt.add_argument("-referer=https://search.jd.com/")
        # chrome_opt.add_argument("-cookies:thor=279F8B2493C5B003E4EE9A22A8547230BD08F345BE6C5A0CB26B3C14B10E80A943CB9D4C385876E8F9518E4CC0BB83C892B8D354724BFFEDE0E5168130B25DC7ADDF471E9D0711895D32FEAC8CA22405F53E82A25D8D961CA4E276517A4FFBDA2736F4E8717239B76F05F7BC46DDAC71F251A4A8B22D8E6807731F521690FAFE;")
        self.driver = webdriver.Chrome(chrome_options=chrome_opt)
        self.driver.set_page_load_timeout(60)  # 页面加载超时时间
        self.driver.set_script_timeout(60)  # 页面js加载超时时间

    def __del__(self):
        self.driver.close()

    def process_request(self, request, spider):
        try:
            if spider.name == 'SpiderJD' and request.meta.get('sign') == 'SeleniumMiddleware':
                print("selenium is Running..." + self.driver.current_url)
                self.driver.get(request.url)
                # print(self.driver.page_source)
                # EC.visibility_of_element_located((By.XPATH, '//div[@class="sku-name"]/text()'), True)
                time.sleep(2)
                return HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, request=request,
                                    encoding="utf-8", status=200)
            else:
                return None
        except TimeoutException:
            print("time out")
            return HtmlResponse(url=self.driver.current_url, status=500, request=request)

