# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
import pymysql.cursors
from twisted.enterprise import adbapi
from .items import ProductReviewItem, ProductInfoItem
from scrapy.utils.project import get_project_settings


class JDProductInfoPipeline(object):
    def __init__(self):
        settings = get_project_settings()
        dbparms= dict(
            host=settings.get('MYSQL_HOST'),
            db=settings.get('MYSQL_DBNAME'),
            user=settings.get('MYSQL_USER'),
            passwd=settings.get('MYSQL_PASSWD'),
            charset=settings.get('MYSQL_CHARSET'),
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        #指定数据库模块名和数据库参数
        self.dbpool = adbapi.ConnectionPool("pymysql", **dbparms)

    def process_item(self, item, spider):
        if (type(item) == ProductInfoItem):
            query = self.dbpool.runInteraction(self.do_insert, item)
        if (type(item) == ProductReviewItem):
            query = self.dbpool.runInteraction(self.do_insert_review, item)
        query.addErrback(self.handle_error)

    def handle_error(self, failure):
        if failure:
            print(failure)

    def do_insert(self, cursor, item):
        pid = item['ProductId']
        pname = item['ProductName']
        pdes = item['ProductDescription']
        purl = item['ProductUrl']
        pcate = item['ProductCategories']
        price = item['ProductPrice']
        sname = item['StoreName']
        params = item['ProductParameter']
        tablename = item['TableName']

        try:
            sql = """
            INSERT INTO {0}(ProductId, ProductName, ProductDescription, ProductUrl, ProductCategories, ProductPrice, StoreName, ProductParameter) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """.format(tablename)
            VALUES = (pid, pname, pdes, purl, str(pcate), price, sname, str(params))
            cursor.execute(sql, VALUES)
            # print(tablename, "导入数据库成功！")
        except pymysql.err.IntegrityError as e:
            # print(sql, VALUES)
            # print(e)
            pass

    def do_insert_review(self, cursor, item):
        pid = item['productId']
        rid = item['review_id']
        rer = item['reviewer']
        rcon = item['review_content']
        rating = item['review_rating']
        rhelp = item['review_helpful']
        rtime = item['review_time']
        tablename = item['TableName']
        sql = """
        INSERT INTO {0}(ProductId, ReviewId, Reviewer, ReviewContent, ReviewRating, ReviewHelpful, ReviewTime) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """.format(tablename)
        VALUES = (pid, rid, rer, rcon, rating, rhelp, rtime)
        # print(VALUES)
        try:
            cursor.execute(sql, VALUES)
            # print(tablename, "评论数据导入成功")
        except Exception as e:
            # print(sql)
            # print(e)
            pass
