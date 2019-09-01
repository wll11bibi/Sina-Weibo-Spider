# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class TestSpiderItem(scrapy.Item):
    uid = scrapy.Field()


class UserInfoItem(scrapy.Item):
    """保存用户信息的各种属性，最后将item对象转换为dict，写入数据库"""
    uid = scrapy.Field()  # uid
    icon = scrapy.Field()
    gender = scrapy.Field()
    description = scrapy.Field()
    screen_name = scrapy.Field()  # 用户昵称
    mbtype = scrapy.Field()
    mbrank = scrapy.Field()
    urank = scrapy.Field()
    verified = scrapy.Field()
    verified_type = scrapy.Field()
    verified_reason = scrapy.Field()
    verified_type_ext = scrapy.Field()



    # followers_count = scrapy.Field()  # 粉丝数
    # follow_count = scrapy.Field()  # 关注数


class SeedUidItem(scrapy.Item):

    # def __init__(self):
    #     super(SeedUidItem, self).__init__()
    #     self.db_login = {}
    """用于保存种子用户uid"""
    uid = scrapy.Field()
    followers_count = scrapy.Field()  # 粉丝数
    follow_count = scrapy.Field()  # 关注数


