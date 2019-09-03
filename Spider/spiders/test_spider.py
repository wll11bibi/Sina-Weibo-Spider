import scrapy
import json
import pymysql
import sys
from Spider.items import TestSpiderItem


class test_spider(scrapy.Spider):
    name = 'test_spider'
    allow_domains = ['m.weibo.cn']

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider, self).__init__(*args, **kwargs)
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
        self.__api_2 = '&page='

    def parse(self, response):
        try:
            db = pymysql.connect(**self.__db_params)
            cursor = db.cursor()
            sql = 'select uid from user_info order by followers_count desc'
            count = cursor.execute(sql)
            # print(sys.getsizeof(cursor))
            # print()
            for i in range(0, count):
                test_list = cursor.fetchone()
                # print(sys.getsizeof(test_list))
                uid = test_list[0]
                for j in range(1, 10):
                    # url = 'https://' + self.allow_domains[0] + self.__api_0 + uid + self.__api_1 + uid + self.__api_2 + str(j)
                    url = self.start_urls[0] + self.__api_0 + uid + self.__api_1 + uid + self.__api_2 + str(j)

                    yield scrapy.http.Request(url=url, callback=self.parse_page)

        except Exception as e:
            print(e)

    def parse_page(self, response):
        parse_json = json.loads(response.text)
        item = TestSpiderItem()
        cards = (parse_json['data'])['cards']
        for card in cards:
            item['uid'] = card['card_style']
            print(item['uid'])
# def __get_uid(self):
# db = pymysql.connect(**self.__db_params)
# cursor = db.cursor()






