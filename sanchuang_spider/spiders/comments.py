from scrapy import Request
from scrapy.spiders import Spider
import json
from sanchuang_spider.items import ProductReviewItem
import time
from urllib import parse


class CommentsSpider(Spider):

    name = 'JDcomments'

    def __init__(self, *args, **kwawrgs):
        super(CommentsSpider, self).__init__(*args, **kwawrgs)
        self.keywords = ""
        self.sort_type = None
        self.keywords=kwawrgs.get('keywords')
        self.keywords = parse.quote(self.keywords)
        self.sort_type = kwawrgs.get("sort_type")


    def start_requests(self):
        url = 'https://search.jd.com/Search?keyword={0}&psort={1}'.format(self.keywords, self.sort_type)
        print("开始依据规则{0}爬取{1}评论信息".format(self.sort_type, parse.unquote(self.keywords)))
        yield Request(url)

    def parse(self, response):
        pagenum = response.xpath("//div[@class='f-pager']/span/i/text()").extract()[0]
        print("有" + pagenum + "页商品！")
        s = 1
        for i in range(1, 2):
            logid = time.time()
            logid = '%.5f' % logid
            pageurl = "https://search.jd.com/Search?keyword={0}&page={1}&psort={2}".format(self.keywords, i * 2 - 1, self.sort_type)
            resturl = "https://search.jd.com/s_new.php?cat={0}&page={1}&s={2}&psort={3}&scrolling=y&&tpl=1_M&isList=1&log_id=".format(self.keywords,
                i * 2, s, self.sort_type) + str(logid)
            s = s + 60
            yield Request(url=pageurl, callback=self.get_product_count)
            yield Request(url=resturl, callback=self.get_product_count, headers={'referer': pageurl})

    def get_product_count(self, response):
        productdis = response.xpath('//li[@class="gl-item"]/@data-sku').extract()
        for productid in productdis:
            commentcounturl = "https://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=" + productid
            yield Request(commentcounturl, callback=self.get_comment_url, meta={'productid': productid})

    def get_comment_url(self, response):
        # print(response.text)
        productid = response.meta['productid']
        content = json.loads(response.text)
        count = content['CommentsCount'][0]['CommentCountStr'].split('+')[0]
        # print(count)
        if count.endswith('万'):
            page = 100
        else:
            page = int(count) / 10
            if page >= 100:
                page = 100
            else:
                page = page

        for i in range(int(page)):
            commenturl = 'https://club.jd.com/comment/productPageComments.action?productId={0}&score=0&sortType=6&page={1}&pageSize=10&isShadowSku=0&fold=1'.format(
                productid, i)
            yield Request(commenturl, callback=self.get_comment_info, meta={'productid': productid}, dont_filter=True)

    def get_comment_info(self, response):
        # print(response.url)
        try:
            content = json.loads(response.text)
            content = content['comments']
            # print(content)
            if content == None:
                print("No comment in this page")
                return
            else:
                for i in range(len(content)):
                    item = ProductReviewItem()
                    item['TableName'] = 'JD_Product_Review'
                    item['productId'] = response.meta['productid']
                    item['review_id'] = content[i]['id']
                    item['reviewer'] = content[i]['guid']
                    item['review_content'] = content[i]['content']
                    item['review_rating'] = content[i]['score']
                    item['review_helpful'] = content[i]['usefulVoteCount']
                    item['review_time'] = content[i]['creationTime']
                    # print(item)
                    yield item
        except Exception as e:
            print(e)
            pass
