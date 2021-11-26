from scrapy import Request
from scrapy.spiders import Spider
import json
from sanchuang_spider.items import ProductInfoItem
import time
from urllib import parse


class jdSpider(Spider):
    name = 'SpiderJD'

    def __init__(self, *args, **kwawrgs):
        super(jdSpider, self).__init__(*args, **kwawrgs)
        self.keywords = ""
        self.sort_type = None
        self.keywords = kwawrgs.get('keywords')
        self.keywords = parse.quote(self.keywords)


    def start_requests(self):
        url = 'https://search.jd.com/Search?keyword={0}&psort={1}'.format(self.keywords, self.sort_type)
        print("开始依据规则{0}爬取{1}商品信息".format(self.sort_type, parse.unquote(self.keywords)))
        yield Request(url)

    def parse(self, response):
        pagenum = response.xpath("//div[@class='f-pager']/span/i/text()").extract()[0]
        print("有" + pagenum + "页商品！")
        s = 1
        for i in range(1, int(pagenum)+1):
            # print("————————正在爬取第{0}页————————".format(i))
            logid = time.time()
            logid = '%.5f' % logid
            pageurl = "https://search.jd.com/Search?keyword={0}&page={1}&psort={2}".format(self.keywords, i * 2 - 1,
                                                                                           self.sort_type)
            resturl = "https://search.jd.com/s_new.php?keyword={0}&page={1}&s={2}&psort={3}&scrolling=y&&tpl=1_M&isList=0&log_id=".format(
                self.keywords, i * 2, s, self.sort_type) + str(logid)
            s = s + 60
        yield Request(url=pageurl, callback=self.get_product_id)
        yield Request(url=resturl, callback=self.get_product_id, headers={'referer': pageurl})

    def get_product_id(self, response):
        # print(response.url)
        productdis = response.xpath('//li[@class="gl-item"]/@data-sku').extract()
        # print(productdis)
        for productid in productdis:
            producturl = 'https://item.jd.com/{0}.html'.format(productid)
            yield Request(producturl, callback=self.prase_product_info,
                          meta={'sign': 'SeleniumMiddleware', 'id': productid}, dont_filter=True)

    def prase_product_info(self, response):
        # print("++++++++++++++++++++++" + response.url)
        description = response.xpath('//meta[@name="description"]/@content').extract()[0].strip()
        name = response.xpath('//title/text()').extract()[0].strip()
        storename = response.xpath('//div[@class="name"]/a/text()').extract()[0]
        category = {}
        category['0'] = response.xpath('//div[@class = "item first"]/a/text()').extract()[0]
        cate = response.xpath('//div[@class="crumb fl clearfix"]/div[@class = "item"]//a/text()').extract()
        for i in range(3):
            category[str(i + 1)] = cate[i]
        category['4'] = response.xpath('//div[@class = "item ellipsis"]/text()').extract()[0]
        # print(category)
        keylist = response.xpath('//dl[@class="clearfix"]/dt/text()').extract()
        valuelist = response.xpath('//dl[@class="clearfix"]/dd[not(@class)]/text()').extract()
        parameter = {}
        for key, value in zip(keylist, valuelist):
            parameter[key] = value
        # print(parameter)
        productid = response.meta['id']
        item = ProductInfoItem()
        item['TableName'] = 'JD_Product_info'
        item['ProductId'] = productid
        item['ProductName'] = name
        item['ProductDescription'] = description
        item['ProductUrl'] = response.url
        item['ProductCategories'] = category
        item['StoreName'] = storename
        item['ProductParameter'] = parameter
        priceUrl = "http://p.3.cn/prices/mgets?callback=jQuery&type=1&skuIds=J_" + productid
        yield Request(priceUrl, callback=self.get_price, meta={'item': item}, dont_filter=True)

    def get_price(self, response):
        # print("here here")
        temp = response.text.split('jQuery([')
        try:
            priceinfo = temp[1][:-4]
            content = json.loads(priceinfo)
            Price = content['p']
        except:
            print("None")
            return None
        item = response.meta['item']
        item['ProductPrice'] = Price
        # print(item)
        return item
