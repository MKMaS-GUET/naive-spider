import sys, os
import subprocess
import time
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
import pymysql
from sanchuang_spider.settings import MYSQL_HOST, MYSQL_DBNAME, MYSQL_USER, MYSQL_PASSWD, MYSQL_CHARSET


class RunningSpiderProject():

    dbparms = dict(
        host=MYSQL_HOST,
        db=MYSQL_DBNAME,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWD,
        charset=MYSQL_CHARSET,
        cursorclass=pymysql.cursors.DictCursor,
        use_unicode=True,
    )
    count_num = dict(
        JD_Product_info=0,
        # Gome_Product_info=0,
        Suning_Product_info=0,
        Vip_Product_info=0,
        JD_Product_Review=0,
        # Gome_Product_Review=0,
        Suning_Product_Review=0,
        Vip_Product_Review=0,
    )


    def get_count_stat(self):
        # 指定数据库模块名和数据库参数
        conn = pymysql.connect(**self.dbparms)
        cursor = conn.cursor()
        for key in self.count_num:
            sql = "SELECT COUNT(*) AS ITEM_NUM FROM {}".format(key)
            cursor.execute(sql)
            self.count_num[key] = cursor.fetchone()['ITEM_NUM']
        cursor.close()
        conn.close()
        return self.count_num


    def save_static_message(self, StaticInfo):
        # 指定数据库模块名和数据库参数
        conn = pymysql.connect(**self.dbparms)
        cursor = conn.cursor()
        sql = "INSERT INTO SpiderStatic VALUES({0},{1})".format(StaticInfo, time.ctime())
        cursor.execute(sql)
        cursor.close()
        conn.close()


    def my_job(self, keywords, sort_type, spiderName,running_time):
        RUNNING_TIME = running_time
        platform_name = dict(
            JD_Product_info='新增京东商城商品数据{0}项，至今共有{1}条数据',
            # Gome_Product_info="新增国美商城商品数据{0}项，至今共有{1}条数据",
            Suning_Product_info="新增苏宁商城商品数据{0}项，至今共有{1}条数据",
            Vip_Product_info="新增唯品会商城商品数据{0}项，至今共有{1}条数据",
            JD_Product_Review = "新增京东商城评论数据{0}条，至今共有{1}条数据",
            # Gome_Product_Review="新增国美商城评论数据{0}条，至今共有{1}条数据",
            Suning_Product_Review="新增苏宁商城评论数据{0}条，至今共有{1}条数据",
            Vip_Product_Review='新增唯品会商城评论数据{0}条，至今共有{1}条数据',
        )
        start_count = self.get_count_stat()
        print('my_job,{}'.format(time.ctime()))
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        proc = subprocess.Popen("scrapy crawlopt -s {0} -a keywords={1} -a sort_type={2}".format(spiderName, keywords, sort_type), shell=True)
        while proc.poll() is None:
            pass
        end_count = self.get_count_stat()
        result_count = dict()
        StaticInfo = ""
        StaticInfo +="本次爬取结束时间为:{}\n".format(time.ctime())
        for key in end_count:
            result_count[key] = end_count[key] - start_count[key]
            StaticInfo += platform_name[key].format(result_count[key], end_count[key])+"\n"
        # print(StaticInfo)
        self.save_static_message(StaticInfo)


def crawl_with_cycle(keywords, sort_type, spiderName, day_of_week, hour, minute, second, running_time):
    executors = {
        'default': ThreadPoolExecutor(10)
    }
    scheduler = BlockingScheduler(executors=executors)

    intervalTrigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute, second=second)
    try:
        scheduler.remove_job(job_id='my_job_id')
    except:
        TimedCrawl = RunningSpiderProject()
        scheduler.add_job(TimedCrawl.my_job, intervalTrigger, id='my_job_id',
                          kwargs={'keywords': keywords, 'sort_type': sort_type, 'spiderName': spiderName, 'running_time': running_time})
        scheduler.start()
        scheduler.shutdown()


def imme_crawl(keywords, sort_type, spiderName, running_time):
    # scheduler.shutdown(wait=False)
    ImmeCrawl = RunningSpiderProject()
    ImmeCrawl.my_job(keywords, sort_type, spiderName, running_time)

