import scrapy
import json
import pymysql

class test_spider(scrapy.spiders):
    name = 'test_spider'
    allow_domains = ['m.weibo.cn']

    def __init__(self, *args, **kwargs):
        super(scrapy.spiders, self).__init__(*args, **kwargs)
        self.start_urls = ['https://m.weibo.cn/']
        self.__db_params = dict(
            host='127.0.0.1',
            user='root',
            password='112798',
            port=3306,
            database='weibo',
            charset='utf8mb4',
            use_unicode=True,
        )

        self.__api_0 = 'api/container/getIndex?containerid=231051_-_fans_-_'
        self.__api_1 = '&luicode=10000011&lfid=100505'

    def parse(self, response):
        try:
            db = pymysql.connect(**self.__db_params)
            cursor = db.cursor()
        except:
            pass

# def __get_uid(self):
# db = pymysql.connect(**self.__db_params)
# cursor = db.cursor()






