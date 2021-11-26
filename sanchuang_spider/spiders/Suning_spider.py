import re
import scrapy
from sanchuang_spider.items import ProductInfoItem, ProductReviewItem
import json
from urllib import parse


class SuningSpider(scrapy.Spider):
    name = 'SpiderSuning'
    # allowed_domains = ['https://search.suning.com/']
    # segment = 0
    # same_page_url = "https://list.suning.com/emall/searchV1Product.do?ci=258003&pg=03&yjhx=&cp="
    # same_page_url_center = "&il=0&st=0&iy=0&isNoResult=0&n=1&sesab=ACBAABC&id=IDENTIFYING&cc=773&paging="
    # same_page_url_tail = "&sub=1&jzq=40634"
    # next_segment = 15
    # next_page_url = "https://list.suning.com/emall/searchV1Product.do?ci=258003&pg=03&yjhx=&cp="
    # next_page_url_tail = "&il=0&st=0&iy=0&adNumber=0&isNoResult=0&n=1&sesab=ACBAABC&id=IDENTIFYING&cc=773&sub=1&jzq=40610"

    def __init__(self, *args, **kwawrgs):
        super(SuningSpider, self).__init__(*args, **kwawrgs)
        self.keywords = ""
        self.sort_type = 0
        self.keywords = kwawrgs.get('keywords')
        self.keywords = parse.quote(self.keywords)
        self.sort_type = kwawrgs.get("sort_type")

    def start_requests(self):
        start_urls = 'https://search.suning.com/{0}/&st={1}'.format(self.keywords, self.sort_type)
        yield scrapy.Request(start_urls, callback=self.getpages)
        # 下滑加载的url

    def getpages(self, response):
        numstr = response.xpath("//span[@class='page-more']/text()").extract()[0]
        pagenum = numstr[1:3]
        for page in range(int(pagenum)):
            self.segment = 0
            for i in range(4):
                segurl = "https://search.suning.com/emall/searchV1Product.do?keyword={0}&ci=0&pg=01&cp=0&il=0&st={1}&iy=0&isNoResult=0&sesab=MCAABBABCAAA&id=IDENTIFYING&paging={2}".format(self.keywords, page, self.segment)
                yield scrapy.Request(segurl, callback=self.get_product_id, dont_filter=True)

    def get_product_id(self, response):
        product_list = response.xpath("//div[@class='title-selling-point']")
        # print(review_list)
        for each in product_list:
            # 获取电脑商品列表中的url
            product_url = each.xpath("./a/@href").extract()[0]
            nextUrl = 'https:' + product_url
            product_data = eval(each.xpath("./a/@sa-data").extract()[0])
            # print(product_data)
            ProductId = product_data["prdid"]
            ShopId = product_data["shopid"]

            # # 跳转到商品详细的页面
            yield scrapy.Request(url=nextUrl, meta={'ProductId': ProductId, 'ShopId': ShopId, 'ProductUrl': nextUrl},
                                 callback=self.productDetail, dont_filter=True)
        #     管道保存商品url
        #     su_item = ProductInfoItem()
        #     su_item['ProductUrl'] = nextUrl
        #     yield su_item

    #     # 处理下滑动态加载的页面
    #     print("segment:")
    #     print(self.segment)
    #     if self.segment < 4:
    #         yield scrapy.Request(
    #             'https://search.suning.com/emall/searchV1Product.do?keyword={0}&ci=0&pg=01&yjhx=&cp={1}&il=0&st=0&iy=0&adNumber=18&isNoResult=0&n=1&sesab=MCAABBABCAAA&id=IDENTIFYING&cc=771&paging={2}'.format(
    #                 self.keywords, self.segment, self.pagenum)
    #             , self.same_page_url + str(self.next_segment) + self.same_page_url_center + str(
    #                 self.segment) + self.same_page_url_tail, callback=self.parse)
    #         self.segment += 1
    #
    #     # 进行翻页
    #     if self.segment >= 4:
    #         self.segment = 0;
    #         if self.next_segment <= 50:
    #             yield scrapy.Request(self.next_page_url + str(self.next_segment) + self.next_page_url_tail,
    #                                  callback=self.parse)
    #             self.next_segment += 1
    #
    # 跳转商品详细页面
    def productDetail(self, response):
        get_meta = response.meta
        # 商品id
        product_id = get_meta['ProductId']
        # 商品的url
        product_url = get_meta['ProductUrl']
        # 店铺的id
        shop_id = get_meta['ShopId']
        # 商品描述
        product_description = response.xpath("//meta[@name='description']/@content").extract()[0]
        # #店铺名称
        # product_store_name=response.xpath("//a[@id='chead_indexUrl']/@title").extract()[0]
        # #商品类别
        # product_category=response.xpath("//table[@id='bzqd_tag']/tbody/tr[2]/td[2]/text()").extract()[0]
        # 商品参数
        product_parameter = response.xpath("//table[@id='itemParameter']/tbody/tr")
        parameter_dict = {}
        for i in product_parameter:
            # print(i)
            text1 = i.xpath("./td[1]/div/span/text()").extract()
            text2 = i.xpath("./td[2]/text()").extract()
            text3 = i.xpath("./td[2]/a/text()").extract()

            punctuation = '!,;:?".\''
            if len(text1) != 0 and len(text2) != 0:
                # print(text1)
                key1 = re.sub(r'[{}]+'.format(punctuation), "_", text1[0])  # 以为key中不能有".",不然无法存到mongodb
                # print(key1)
                parameter_dict[key1] = text2[0]
            if len(text1) != 0 and len(text3) != 0:
                key2 = text1[0]
                parameter_dict[key2] = text3[0]
        # print(parameter_dict)

        # 获取评论的cluster_id
        script = response.xpath("//script[@type='text/javascript']/text()").extract()  # 获取script代码，有很多有用信息
        cluster = re.findall(r'\"clusterId\":\".*?\"', script[0])
        cluster_id = json.loads("{" + cluster[0] + "}")['clusterId']
        # 商品名
        product_display = re.findall(r'\"itemDisplayName\":\".*?\"', script[0])
        product_name = json.loads("{" + product_display[0] + "}")['itemDisplayName']
        # 店铺名称
        flagshipName = re.findall(r'\"flagshipName\":\".*?\"', script[0])
        product_store_name = json.loads("{" + flagshipName[0] + "}")['flagshipName']
        # print(product_store_name)
        # 商品描述
        product_category = {}
        category = re.findall(r'\"categoryName\d\":\".*?\"', script[0])
        categoryName = {}
        for it in category:
            categoryName.update(json.loads("{" + it + "}"))
        product_category['0'] = categoryName['categoryName1']
        product_category['1'] = categoryName['categoryName2']
        product_category['2'] = categoryName['categoryName3']

        brandName = re.findall(r'\"brandName\":\".*?\"', script[0])
        itemDisplayName = re.findall(r'\"itemDisplayName\":\".*?\"', script[0])

        brandName = json.loads("{" + brandName[0] + "}")
        itemDisplayName = json.loads("{" + itemDisplayName[0] + "}")

        product_category['3'] = brandName['brandName']
        product_category['4'] = itemDisplayName['itemDisplayName']
        # print(product_category)

        # headers = datasetSpider.settings.DEFAULT_REQUEST_HEADERS
        price_url = "https://icps.suning.com/icps-web/getVarnishAllPriceNoCache/0000000" + str(
            product_id) + "_773_7730199_" + str(shop_id) + "_1_getClusterPrice.jsonp"
        # res = requests.get(price_url, headers=headers)
        meta = {"ProductId": product_id, "ShopId": shop_id, "ProductUrl": product_url,
                "ProductName": product_name, "ProductDescription": product_description,
                "ProductCategories": product_category, "StoreName": product_store_name,
                "ProductParameter": parameter_dict, "cluster_id": cluster_id}
        yield scrapy.Request(url=price_url, meta=meta, callback=self.Price)

    # 获取价格
    def Price(self, response):
        get_meta = response.meta
        price_dirt = re.findall(r'[(](.*)[)]', response.text)[0]
        price_dirt = json.loads(price_dirt)[0]
        # 商品初始价格
        product_price = price_dirt['price']
        # print(product_price)
        product_id = get_meta["ProductId"]
        shop_id = get_meta["ShopId"]
        product_url = get_meta["ProductUrl"]
        product_name = get_meta["ProductName"]
        product_description = get_meta["ProductDescription"]
        product_category = get_meta["ProductCategories"]
        product_store_name = get_meta["StoreName"]
        parameter_dict = get_meta["ProductParameter"]
        cluster_id = get_meta["cluster_id"]
        # 交给管道处理
        su_item = ProductInfoItem()
        su_item['TableName'] = 'Suning_Product_info'
        su_item["ProductId"] = product_id
        su_item["StoreName"] = shop_id
        su_item['ProductUrl'] = product_url
        su_item["ProductName"] = product_name
        su_item["ProductDescription"] = product_description
        su_item["ProductCategories"] = product_category
        su_item["ProductPrice"] = product_price
        su_item["StoreName"] = product_store_name
        su_item["ProductParameter"] = parameter_dict
        yield su_item
        # print(su_item)

        # 评论
        total_review_url = "https://review.suning.com/ajax/cluster_review_satisfy/cluster-" + str(
            cluster_id) + "-0000000" + str(product_id) + "-" + str(shop_id) + "-----satisfy.htm"
        yield scrapy.Request(url=total_review_url,
                             meta={"product_id": product_id, "shop_id": shop_id, "cluster_id": cluster_id},
                             callback=self.Review)

    # 跳转评论页面
    def Review(self, response):
        get_meta = response.meta
        cluster_id = get_meta["cluster_id"]
        product_id = get_meta["product_id"]
        shop_id = get_meta["shop_id"]
        # 最多只能访问50页评论
        for i in range(1, 51):
            # review_url = "https://review.suning.com/ajax/cluster_review_lists/cluster-"+str(cluster_id)+"-0000000"+str(product_id)+"-"+str(shop_id)+"-total-1-default-10-----reviewList.htm"
            review_url = "https://review.suning.com/ajax/cluster_review_lists/cluster-" + str(
                cluster_id) + "-0000000" + str(product_id) + "-" + str(shop_id) + "-total-" + str(
                i) + "-default-10-----reviewList.htm"
            yield scrapy.Request(url=review_url, meta={"product_id": product_id}, callback=self.ReviewList)

    # 处理每一页评论
    def ReviewList(self, response):
        # print(response.text)
        get_meta = response.meta
        product_id = get_meta["product_id"]
        # review_text = json.loads(response.text)
        review_list = re.findall(r'[(](.*)[)]', response.text)  # 使用贪婪匹配才能获取括号所有数据
        # review_text = response.text
        review_text = ''.join(review_list)  # 拼接字符串
        # print(review_text)
        review_dirt = json.loads(review_text)
        # 先判断是否有commodityReviews消息返回
        if "commodityReviews" in review_dirt:
            commodityReviews = review_dirt['commodityReviews']
            for item in commodityReviews:
                # print(item)
                commodityReviewId = item['commodityReviewId']
                content = item['content']
                qualityStar = item['qualityStar']
                publishTime = item['publishTime']
                userInfo = item['userInfo']
                nickName = userInfo['nickName']
                # 评论点赞的数量
                usefulCnt_url = "https://review.suning.com/ajax/useful_count/" + str(
                    commodityReviewId) + "-usefulCnt.htm"
                meta = {"product_id": product_id, "commodityReviewId": commodityReviewId, "content": content,
                        "qualityStar": qualityStar, "publishTime": publishTime, "nickName": nickName}
                yield scrapy.Request(url=usefulCnt_url, meta=meta, callback=self.ReviewUsefulCnt)

    # 是否有用
    def ReviewUsefulCnt(self, response):
        get_meta = response.meta
        ProductId = get_meta["product_id"]
        ReviewId = get_meta["commodityReviewId"]
        ReviewEr = get_meta["nickName"]
        ReviewContent = re.sub('<br/>', "", get_meta["content"])
        ReviewRating = get_meta["qualityStar"]
        ReviewTime = get_meta["publishTime"]
        # 点赞评论的次数
        reviewUsefuAndReplylList = re.findall(r'[(](.*?)[)]', response.text)[0]
        reviewUsefuAndReplylList = json.loads(reviewUsefuAndReplylList)
        ReviewHelful = reviewUsefuAndReplylList["reviewUsefuAndReplylList"][0]["usefulCount"]

        reviewItem = ProductReviewItem()
        reviewItem["TableName"] = "Suning_Product_Review"
        reviewItem["productId"] = ProductId
        reviewItem["review_id"] = ReviewId
        reviewItem["reviewer"] = ReviewEr
        reviewItem["review_content"] = ReviewContent
        reviewItem["review_rating"] = ReviewRating
        reviewItem["review_time"] = ReviewTime
        reviewItem["review_helpful"] = ReviewHelful
        yield reviewItem
