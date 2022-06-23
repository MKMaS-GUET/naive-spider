# Scrapy settings for sanchuang_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
BOT_NAME = 'sanchuang_spider'

SPIDER_MODULES = ['sanchuang_spider.spiders']
NEWSPIDER_MODULE = 'sanchuang_spider.spiders'
FEED_EXPORT_ENCODING = 'utf8'

ROBOTSTXT_OBEY = False
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52", \
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2866.71 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:75.0) Gecko/20100101 Firefox/75.0",
    "Mozilla/5.0 (X11; Linux; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.29"
]
Cookies = "thor=279F8B2493C5B003E4EE9A22A8547230E9574633402642639097DEC2A29C77E24F43B7D77E4CAA1020DCD7B7E570843C86C1DCCFA19FDBA16522D125CDE704C3BCDE875E1E630977BED4ED87C1A7F8178303CE5BC43A10712170ACC8F40190CB564F7E8FA78DDD3DB5D3298A563CB87BCA99E386BEF5EF1E704FFEFBA2EC97B3;"
# PROXIES = ['8.218.23.23:59394']
COOKIES_ENABLED = True
COMMANDS_MODULE = 'sanchuang_spider.commands'
DOWNLOADER_MIDDLEWARES = {
    'sanchuang_spider.middlewares.JdSpiderDownloaderMiddleware': None,
    'sanchuang_spider.middlewares.SpiderUserAgentMiddleware': 100,
    # 'sanchuang_spider.middlewares.ProxyMiddleware': 101,
    # 'sanchuang_spider.middlewares.SeleniumMiddleware': 110,
}
ITEM_PIPELINES = {
    'sanchuang_spider.pipelines.JDProductInfoPipeline': 300,
}
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 20
#
CLOSESPIDER_TIMEOUT = 60
# #
# MEDIA_ALLOW_REDIRECTS = True
# #
EXTENSION = {
    'sanchuang_spider.closespider.CloseSpider': 500,
}
LOG_LEVEL = 'DEBUG'
LOG_FILE = './logs/log.txt'

# start MySQL database configure setting
MYSQL_HOST = '124.71.19.9'
MYSQL_DBNAME = 'commodity_spider'
MYSQL_DBNAMEMALL = 'newbee_mall_db'
MYSQL_USER = 'zhu'
MYSQL_PASSWD = 'Zhu#cpss'
MYSQL_CHARSET = 'utf8'
# end of MySQL database configure setting