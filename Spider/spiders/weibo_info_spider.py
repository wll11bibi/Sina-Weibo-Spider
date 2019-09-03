import scrapy
import pymysql
import json
import os
from scrapy.conf import settings
from scrapy import log


class WeiboInfoSpider(scrapy.Spider):

    name = 'weibo_info_spider'
    allowed_domains = ['m.weibo.cn', 'weibo.com']
    handle_httpstatus_list = [418]

    def __init__(self, *args, **kwargs):
        super(WeiboInfoSpider, self).__init__(*args, **kwargs)
        # self.__uid = []  # 爬取用户的uid
        self.__db_login = {}  # 数据库配置信息
        self.__range_list = {} #  爬取用户微博的页数限制
        self.start_urls = ['https://m.weibo.cn/']

        self.__api_0 = 'api/container/getIndex?type=uid&value='
        self.__api_1 = '&containerid=107603'
        self.__api_2 = '&page='

        # 设置爬取到空网页、收到HTTP code 418重新生成request对象尝试获得数据的次数
        self.__repeat_times = scrapy.conf.settings.get('WEIBO_INFO_SPIDER_REPEAT_TIME')

        self.__set_db_login()
        self.__set_page_range()

        # self.__set_start_urls()

        #  api: api0 + uid + api1 + uid +  api2 + page_num
    def __set_db_login(self):
        self.__db_login = dict(
                host=settings['MYSQL_HOST'],
                user=settings['MYSQL_USER'],
                password=settings['MYSQL_PASSWORD'],
                port=settings['MYSQL_PORT'],
                database=settings['MYSQL_DBNAME'],
                charset=settings['MYSQL_CHARSET'],
                use_unicode=True,  # 使用Unicode编码
        )

    def __set_page_range(self):
        self.__range_list['start'] = settings.get('WEIBO_INFO_START_PAGE')
        self.__range_list['end'] = settings.get('WEIBO_INFO_END_PAGE')

    def parse(self, response):
        try:
            db = pymysql.connect(**self.__db_login)
            cursor = db.cursor()
            count = cursor.execute(scrapy.conf.settings.get('WEIBO_INFO_QUERY_SQL0'))
            for i in range(0, count):
                uid = (cursor.fetchone())[0]
                for j in range(self.__range_list['start'], self.__range_list['end']):
                    url = self.start_urls[0] + self.__api_0 + uid + self.__api_1 + uid + self.__api_2 + str(j)
                    repeat_times = 0
                    yield scrapy.Request(url=url, callback=self.parse_page, meta={'repeat_times': repeat_times})
            cursor.close()
            db.close()
        except Exception as e:
            print(e)
            scrapy.log.msg(level=scrapy.log.ERROR, message=repr(e))

    def parse_page(self, response):
        if response.status == 200:
            print("catch page success!")
            print("url now:" + response.url)
            parse_json = json.loads(response.text)
            if parse_json['ok'] != 0:
                # 返回的数据不为空
                pass
            else:
                # 返回的数据为空
                # 加入meta参数，对重复爬取的数据进行计数，如果在重复爬取一定次数之后还是无法成功抓取，则将该url写入本地
                # 存储在某一个文件之中，暂不爬取
                scrapy.log.msg(level=scrapy.log.INFO, message="catch empty json file! url:" + response.request.url)
                print("catch empty json file!")
                # 如果该url请求次数小于限制的次数，重新生成该url的request对象
                if response.meta['repeat_times'] < self.__repeat_times:
                    response.meta['repeat_times'] += 1
                    yield scrapy.Request(url=response.request.url, callback=self.parse_page,
                                         meta=response.meta, dont_filter=True)
                    print("Request has been generated again!")
                    scrapy.log.msg(level=scrapy.log.INFO, message="regenerating request object!")
                else:
                    print("can't get data from this url: %s !" % response.request.url)
                    scrapy.log.msg(level=scrapy.log.WARNING, message="fail to crawl! url: %s" % response.request.url)
        if response.status == 418:
            pass
        # pass

    # def __set_start_urls(self):
    #     # 设置爬取微博页数范围
    #     self.__range_list['start'] = settings.get('WEIBO_INFO_START_PAGE')
    #     self.__range_list['end'] = settings.get('WEIBO_INFO_END_PAGE')
    #     # 读取数据库配置信息
    #     self.__db_login = dict(
    #         host=settings['MYSQL_HOST'],
    #         user=settings['MYSQL_USER'],
    #         password=settings['MYSQL_PASSWORD'],
    #         port=settings['MYSQL_PORT'],
    #         database=settings['MYSQL_DBNAME'],
    #         charset=settings['MYSQL_CHARSET'],
    #         use_unicode=True,  # 使用Unicode编码
    #     )
    #
    #     try:
    #         db = pymysql.connect(**self.__db_login)
    #         cursor = db.cursor()
    #         query_sql = settings.get('WEIBO_INFO_QUERY_SQL')
    #         count = cursor.execute(query_sql)
    #         for i in range(0, count):
    #             uid = list(cursor.fetchone())[0]
    #             for j in range(int(self.__range_list['start']), int(self.__range_list['end'])):
    #                 self.start_urls.append(self.__api_0 + uid + self.__api_1 + uid + self.__api_2 + str(j))
    #         cursor.close()
    #         db.close()
    #
    #     except Exception as e:
    #         print('set start_urls fail!')
    #         print(e)
    #
    # def parse(self, response):
    #

    # def parse(self, response):
    #     if response.status == 200 and len(response.body) != 0:
    #         print("catch success!")
    #         print("url now:" + response.url)
    #         prase_json = json.loads(response.text)
    #         if prase_json['data'] == 1:
    #             cards = (prase_json['cards'])
    #             for card in cards:
    #                 pass
    #         else:
    #             print('catch empty file')
    #     else:
    #         pass

