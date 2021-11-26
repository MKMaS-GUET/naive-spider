import scrapy
import re
import json
from scrapy import Request
from urllib import parse
from sanchuang_spider.items import ProductInfoItem, ProductReviewItem


class vipSpider(scrapy.Spider):
    name = 'SpiderVip'
    allowed_domains = ['vip.com']
    start_urls = ['http://vip.com/']

    def __init__(self, *args, **kwawrgs):
        super(vipSpider, self).__init__(*args, **kwawrgs)
        self.keywords = ""
        self.sort_type = 0
        self.keywords = kwawrgs.get('keywords')
        self.keywords = parse.quote(self.keywords)
        self.sort_type = kwawrgs.get("sort_type")

    def start_requests(self):
        url = 'https://mapi.vip.com/vips-mobile/rest/shopping/pc/search/product/rank?&app_name=shop_pc&app_version=4.0&warehouse=VIP_NH&fdc_area_id=104105103&client=pc&mobile_platform=1&province_id=104105&api_key=70f71280d5d547b2a7bb370a529aeea1&user_id=&mars_cid=1632567328744_c295ab67a18738fc69051188b93f4158&wap_consumer=a&standby_id=nature&keyword={0}&lv3CatIds=&lv2CatIds=&lv1CatIds=&brandStoreSns=&props=&priceMin=&priceMax=&vipService=&sort={1}&pageOffset={2}&channelId=1&gPlatform=PC&batchSize=120&_=1632750377127'.format(
            self.keywords, self.sort_type, 0)
        yield Request(url, callback=self.get_page_num)

    def get_page_num(self, response):
        page = json.loads(response.text)['data']['total']
        pagenum = int(page)/120
        for i in range(int(pagenum)):
            pids_offset = i * 120
            products_url = 'https://mapi.vip.com/vips-mobile/rest/shopping/pc/search/product/rank?callback=getMerchandiseIds&app_name=shop_pc&app_version=4.0&warehouse=VIP_NH&fdc_area_id=104105103&client=pc&mobile_platform=1&province_id=104105&api_key=70f71280d5d547b2a7bb370a529aeea1&user_id=&mars_cid=1632567328744_c295ab67a18738fc69051188b93f4158&wap_consumer=a&standby_id=nature&keyword={0}&lv3CatIds=&lv2CatIds=&lv1CatIds=&brandStoreSns=&props=&priceMin=&priceMax=&vipService=&sort={1}&pageOffset={2}&channelId=1&gPlatform=PC&batchSize=120&_=1632750377127'.format(
                self.keywords, self.sort_type, pids_offset)
            yield Request(url=products_url, callback=self.get_products_info)

    def get_products_info(self, response):
        pids_json = response.text
        pid_pattern = re.compile('pid.*?(\d+)', re.S)
        pids_list = re.findall(pid_pattern, pids_json)
        for pid in pids_list:
            product_url = 'https://mapi.vip.com/vips-mobile/rest/shopping/pc/product/module/list/v2?callback=getMerchandiseDroplets1&app_name=shop_pc&app_version=4.0&warehouse=VIP_NH&fdc_area_id=104105103&client=pc&mobile_platform=1&province_id=104105&api_key=70f71280d5d547b2a7bb370a529aeea1&user_id=&mars_cid=1632567328744_c295ab67a18738fc69051188b93f4158&wap_consumer=a&productIds={}%2C&scene=search&standby_id=nature&extParams=%7B%22stdSizeVids%22%3A%22%22%2C%22preheatTipsVer%22%3A%223%22%2C%22couponVer%22%3A%22v2%22%2C%22exclusivePrice%22%3A%221%22%2C%22iconSpec%22%3A%222x%22%2C%22ic2label%22%3A1%7D&context=&_=1632750377129'.format(pid)
            yield Request(url=product_url, callback=self.product_info_parse)

    def product_info_parse(self, response):

        product_html = response.text
        product_pattern = re.compile('{.*}', re.S)
        product_info = re.findall(product_pattern, product_html)[0]
        product_json = json.loads(product_info)
        product_data = product_json['data']['products'][0]
        params = str(product_data['attrs']).strip('[').strip(']')
        params = params.replace("'", "\"").replace("},", "},,")
        params = params.split(",,")
        parameters = {}
        for i in params:
            text = json.loads(i)
            parameters[text['name']] = text['value']

        item = ProductInfoItem()
        item['TableName'] = 'Vip_Product_info'
        # params needed to enter the next page
        BrandId = product_data['brandId']
        SpuId = product_data['spuId']
        ProductId = product_data['productId']
        # ---------------------------------------
        item['ProductId'] = product_data['productId']  # 商品号（主码）
        item['ProductName'] = product_data['title']  # 商品名
        item['ProductDescription'] = product_data['title']  # 商品描述
        item['ProductUrl'] = 'https://detail.vip.com/detail-{}-{}.html'.format(BrandId, ProductId)  # 商品链接（打开商品页面的url）
        item['ProductCategories'] = product_data['categoryId']  # 商品索引（形式如{'0': '电脑 办公打印 文仪', '1': '电脑整机', '2': '笔记本', '3': '戴尔(DELL)', '4': '戴尔（DELL）灵越15Plus 7510英特尔11代 15.6英寸轻薄笔记本电脑(i7-11800H 16G 512G RTX 3050 4G独显)银'}）
        item['ProductPrice'] = product_data['price']['salePrice']  # 商品价格
        item['StoreName'] = product_data['brandShowName']  # 店铺名
        item['ProductParameter'] = parameters  # 商品参数
        yield item

        for j in range(1, 51):
            comments_url = 'https://mapi.vip.com/vips-mobile/rest/content/reputation/queryBySpuId_for_pc?callback=getCommentDataCb&app_name=shop_pc&app_version=4.0&warehouse=VIP_NH&fdc_area_id=104105103&client=pc&mobile_platform=1&province_id=104105&api_key=70f71280d5d547b2a7bb370a529aeea1&user_id=&mars_cid=1632567328744_c295ab67a18738fc69051188b93f4158&wap_consumer=a&spuId={}&brandId={}&page={}&pageSize=10'.format(SpuId, BrandId, j)
            yield Request(url=comments_url, callback=self.comments_info_parse)

    def comments_info_parse(self, response):
        comments_html = response.text
        comments_pattern = re.compile('{.*}', re.S)
        comments_info = re.findall(comments_pattern, comments_html)[0]
        comments_json = json.loads(comments_info)
        comments_list = comments_json['data']

        item = ProductReviewItem()
        item['TableName'] = 'Vip_Product_Review'
        for comment in comments_list:
            item['productId'] = comment['reputationProduct']['goodsId']  # 商品编号（进行连接查询）
            item['review_id'] = comment['reputation']['reputationId']  # 评论编码（主码）
            item['reviewer'] = comment['reputationUser']['authorName']  # 评论人
            item['review_content'] = comment['reputation']['content']  # 评论内容
            item['review_rating'] = comment['reputation']['nlpScore']  # 评论的打分
            item['review_helpful'] = comment['reputation']['usefulCount']  # 评论点赞数
            item['review_time'] = comment['reputation']['timeDesc']  # 评论时间
            yield item


    '''
    def parse(self, response):
        pass
    '''


