import scrapy
import pymysql
import json
import time
from scrapy import log
from Spider.items import UserInfoItem
from scrapy.conf import settings


class UserInfoSpider(scrapy.Spider):

    name = 'user_info_spider'
    allowed_domains = ['m.weibo.cn', 'weibo.com']
    handle_httpstatus_list = [418]

    def __init__(self, *args, **kwargs):
        super(UserInfoSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://m.weibo.cn/']
        self.__db_login = {}  # 数据库配置信息
        self.__api_0 = 'api/container/getIndex?type=uid&value='
        self.__api_1 = '&containerid=100505'
        self.__sleep_time = int(scrapy.conf.settings.get('USER_INFO_SPIDER_SLEEP_TIME'))  # 设置爬虫暂停时延
        self.__repeat_times = scrapy.conf.settings.get('WEIBO_INFO_SPIDER_REPEAT_TIME')  # 设置爬虫爬取失败时重复爬取次数
        self.__set_db_login()  # 设置数据库配置信息

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

    def parse(self, response):
        try:
            db = pymysql.connect(**self.__db_login)
            cursor = db.cursor()
            count = cursor.execute(scrapy.conf.settings.get('USER_INFO_QUERY_SQL'))
            for i in range(0, count):
                uid = (cursor.fetchone())[0]
                url = self.start_urls[0] + self.__api_0 + uid + self.__api_1 + uid
                # repeat_times = 0
                yield scrapy.Request(url=url, callback=self.parse_page, meta={'repeat_times': 0})
            cursor.close()
            db.close()
        except Exception as e:
            print(e)
            scrapy.log.msg(message=repr(e), level=scrapy.log.ERROR)

    # parse_page 函数用于处理每一个返回的页面具体页面，并将相应的纸赋予item
    def parse_page(self, response):
        # if response.status == 200 and len(response.body) != 0:
        if response.status == 200:
            print("catch page success!")
            print("url now:" + response.url)
            parse_json = json.loads(response.text)
            if parse_json['ok'] != 0:
                try:
                    item = UserInfoItem()
                    # 从parse_json中提取出user_info
                    user_info = (parse_json['data'])['userInfo']
                    # 给item的字段赋值
                    item['uid'] = user_info['id']
                    item['screen_name'] = user_info['screen_name']
                    item['verified_type'] = user_info['verified_type']
                    item['description'] = user_info['description']
                    item['gender'] = user_info['gender']
                    item['mbtype'] = user_info['mbtype']
                    item['urank'] = user_info['urank']
                    item['mbrank'] = user_info['mbrank']
                    # 判断一些特殊字段是否存在于user_info List中
                    # 黄色大V或者金色大V
                    if 'verified_type_ext' in user_info.keys():
                        item['verified_type_ext'] = user_info['verified_type_ext']
                    # 认证原因
                    if 'verified_reason' in user_info.keys():
                        item['verified_reason'] = user_info['verified_reason']
                    # 是否认证
                    if user_info['verified']:
                        item['verified'] = 1
                    else:
                        item['verified'] = 0
                    # 判断该用户的头像是否为默认头像
                    if user_info['avatar_hd'] == 'https://ss1.sinaimg.cn/orj480/default_avatar_male_180&690':
                        item['icon'] = 1
                    else:
                        item['icon'] = 0
                    yield item
                except KeyError:
                    scrapy.log.msg(level=scrapy.log.INFO, message='json file key error! url:' + response.request.url)
                    print("item key error!")
            else:
                # 如果爬取到为空的data json file，则重新生成该网页的Request对象并进行重新爬取
                if response.meta['repeat_times'] < self.__repeat_times:
                    scrapy.log.msg(level=scrapy.log.INFO, message="catch empty json file! url:" + response.request.url)
                    print("catch empty json file!")
                    response.meta['repeat_times'] += 1
                    yield scrapy.Request(url=response.request.url, callback=self.parse_page, priority=1,
                                         dont_filter=True, meta=response.meta)
                    print("Request has been generated again!")
                    scrapy.log.msg(level=scrapy.log.INFO, message="regenerating request object!")
                    print()
                else:
                    # 如果重复爬取多次仍然无法获取数据，停止爬取，向日志中添加信息
                    print("can't get data from this url: %s !" % response.request.url)
                    scrapy.log.msg(level=scrapy.log.WARNING, message="fail to crawl! url: %s" % response.request.url)

        if response.status == 418:
            # 没有引入代理IP池的情况下出现若又去爬取速度过快收到HTTP code 418，暂停爬取一分钟后重新进行爬取
            scrapy.log.msg(message="http status 418! url:" + response.request.url + "catch fail!",
                           level=scrapy.log.INFO)
            print("too fast! http code 418")
            if response.meta['repeat_times'] < self.__repeat_times:
                print("stop working!")
                time.sleep(60)
                print("restart working!")
                response.meta['repeat_times'] += 1
                yield scrapy.Request(url=response.request.url, callback=self.parse_page,
                                     meta=response.meta['repeat_times'], dont_filter=True, priority=0)
            else:
                print("can't catch this page! url:%s" % response.request.url)
                scrapy.log.msg(level=scrapy.log.WARNING, message="having repeating %d times! url:%s. stop catch " %
                                                                 (self.__repeat_times, response.request.url))
