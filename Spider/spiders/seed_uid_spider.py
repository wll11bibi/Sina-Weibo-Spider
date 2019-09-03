# 该爬虫能通过现已有的少量的用户uid对样本进行扩展
# 扩展之后会将获取到的uid存入mysql数据库中
# 之后其他几个爬虫可以根据扩展后的数据集进行更丰富的数据采集

import os
import traceback
import json
import scrapy
import pymysql
from Spider.items import SeedUidItem


class SeedUidSpider(scrapy.Spider):

    name = 'seed_uid_spider'
    allowed_domains = ['m.weibo.cn', 'weibo.com']

    def __init__(self, category=None, *args, **kwargs):
        super(SeedUidSpider, self).__init__(*args, **kwargs)
        self.start_urls = []
        self.__uid = []  # 用于读取现有的用户uid
        self.__range_list = {}  # 读取爬取页数范围
        self.__db_login = {}  # login database
        self.__BASE_DIR = os.getcwd()
        # self.__BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 当前项目的路径

        """粉丝列表API"""
        self.__api_0 = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_'
        self.__api_1 = '&luicode=10000011&lfid=100505'

        self.__get_super_uid()  # 读取大V信息
        self.__set_start_urls()  # 根据已有的uid生成将要采集的url

    def __get_super_uid(self):
        with open(self.__BASE_DIR + os.sep + 'Database.cnfg', 'r') as file:
            for line in file:
                split_line = line.split('=')
                self.__db_login[split_line[0]] = split_line[1].strip()
            file.close()

        try:
            """连接数据库，扩展样本集"""
            db = pymysql.connect(**self.__db_login)
            cursor = db.cursor()  # 建立游标
            select_sql = "select uid from super_uid"
            cursor.execute(select_sql)
            temp_uid = cursor.fetchall()
            cursor.close()
            # db.close()
            """
                将查询到的结果从元组形式转换为列表存入uid
                fetchall函数返回的为一个元组
                这个元组中的所有元素也都是元组
                每一个元素元组的第0个元素为检索的id
            """
            for item in temp_uid:
                item = list(item)
                self.__uid.append(item[0])

        except Exception:
            print("database error!!!")
            traceback.print_exc()
            db.rollback()
        finally:
            db.close()

    def __set_start_urls(self):
        """通过已有的uid构造要爬取的url"""
        """读取爬取网页的页数"""
        with open(self.__BASE_DIR + os.sep +'seed_uid_spider_range.info', 'r') as file:
            for line in file:
                spilt_line = line.split('=')
                self.__range_list[spilt_line[0]] = int(spilt_line[1].strip())
            file.close()
        for user_id in self.__uid:
            temp_url = self.__api_0 + user_id + self.__api_1 + user_id
            for i in range(self.__range_list['start_page'], self.__range_list['end_page']):
                self.start_urls.append(temp_url + '&since_id=' + str(i))

    def parse(self, response):
        if response.status == 200 and len(response.text) != 0:
            print("catch success!")
            print("url now:" + response.url)
            prase_json = json.loads(response.text)
            if prase_json['ok'] != 0:
                users = (((prase_json['data'])['cards'])[0])['card_group']
                for user in users:
                    item = SeedUidItem()
                    try:
                        user_info = user['user']
                        item['uid'] = user_info['id']
                        item['followers_count'] = user_info['followers_count']
                        item['follow_count'] = user_info['follow_count']
                        # item.db_login = self.__db_login
                        yield item
                    except KeyError:
                        print("unresolved json file! key error!")
            else:
                print("catch empty json file.")
        elif response.status == 418:
            print("catch fail! catch too fast!")
            print("url now:" + response.url)
        else:
            print("catch fail! unknown reason!")
            print("url now:" + response.url)

    # with open('C:\\Users\\86151\\Desktop\\WeiboSpider\\Weibo\\seed_uid.txt', 'r') as file:
    #     for line in file:
    #         uid.append(line)
    #     file.close()
    #
    # for line in uid:
    #     if len(line) == 11:
    #         start_urls.append(line[:len(line)-1])

# import sys
# sys.path.append('C:\\Users\\86151\\Desktop\\WeiboSpider\\Weibo\\Spider')


            # db = pymysql.connect(
            #     host=self.__db_login['host'],
            #     user=self.__db_login['user'],
            #     password=self.__db_login['password'],
            #     database=self.__db_login['database'],
            #     charset=self.__db_login['charset'],
            # )


# with open("C:\\Users\\86151\\Desktop\\WeiboSpider\\Weibo\\seed_uid_spider_range.info", 'r') as file:
#     """这里可以修改位当前文件目录下"""
#     for line in file:
#         split_line = line.split(":")
#         range_list[split_line[0]] = int(split_line[1])
#