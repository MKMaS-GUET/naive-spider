# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductInfoItem(scrapy.Item):
    # define the fields for your item here like:
    ProductId = scrapy.Field()
    ProductName = scrapy.Field()
    ProductDescription = scrapy.Field()
    ProductUrl = scrapy.Field()
    ProductCategories = scrapy.Field()
    ProductPrice = scrapy.Field()
    StoreName = scrapy.Field()
    ProductParameter = scrapy.Field()
    TableName = scrapy.Field()


class ProductReviewItem(scrapy.Item):
    productId = scrapy.Field()
    review_id = scrapy.Field()
    reviewer = scrapy.Field()
    review_content = scrapy.Field()
    review_rating = scrapy.Field()
    review_helpful = scrapy.Field()
    review_time = scrapy.Field()
    TableName = scrapy.Field()