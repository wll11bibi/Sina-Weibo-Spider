# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
import traceback
import pymysql
from twisted.enterprise import adbapi
# from pymysql import cursors
from scrapy.conf import settings
# from scrapy import settings
from scrapy import log


class WeiboInfoPipeline(object):

    def process_item(self, item, spider):
        try:
            if spider.name == 'weibo_info_spider':
                info = dict(item)
                write_info = json.dumps(info)
                """暂时将爬取到的用户数据以json格式写入到文件之中"""
                """待数据库建立连接好之后会将数据直接存入数据库之中"""
                with open('C:\\Users\\86151\\Desktop\\WeiboSpider\\Weibo\\test_weibo_info.json', 'a', encoding='utf-8') \
                        as file:
                    file.write(write_info + '\n')
                    file.close()
        except IOError:
            print("write file error!")
        return item


class UserInfoPipeline(object):
    """
    该类实现的是一个MySQL数据库异步插入数据的功能
    PyMySQL实现的是同步的数据插入
    Scrapy框架为异步多线程数据处理操作
    使用异步插入数据库能够提高写入速度
    """

    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.__general_sql = settings.get('USER_INFO_GENERAL_SQL')
        self.__reason_sql = settings.get('USER_INFO_VERIFIED_REASON_SQL')
        self.__type_ext_sql = settings.get('USER_INFO_VERIFIED_TYPE_EXT_SQL')

    @classmethod
    def from_settings(cls, settings):
        # 设置数据库连接参数
        db_params = dict(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            port=settings['MYSQL_PORT'],
            database=settings['MYSQL_DBNAME'],
            charset=settings['MYSQL_CHARSET'],
            use_unicode=True,  # 使用Unicode编码
            cursorclass=pymysql.cursors.DictCursor,
        )

        # 初始化数据库连接池
        # 参数一：MySQL连接驱动
        # 参数二：MySQL配置信息
        db_pool = adbapi.ConnectionPool('pymysql', **db_params)
        return cls(db_pool)

    def process_item(self, item, spider):
        """
        在该函数内，利用连接池对象，开始操作数据，将数据写入到数据库中。
        pool.map(self.insert_db, [1,2,3])
        同步阻塞的方式： cursor.execute() commit()
        异步非阻塞的方式
        参数1：在异步任务中要执行的函数insert_db；
        参数2：给该函数insert_db传递的参数
        """

        if spider.name == 'user_info_spider':
            query = self.db_pool.runInteraction(self.insert_db, item)
            # 如果异步任务执行失败的话，可以通过ErrBack()进行监听, 给insert_db添加一个执行失败的回调事件
            query.addErrback(self.handle_error)

        return item

    def insert_db(self, cursors, item):
        # cursors与item参数的位置不能变换 巨坑
        # 猜测是因为twisted框架是直接C语言实现的
        # 所以没有办法自动识别参数类型？？？？？
        try:
            # 读插入语句中的文本使用了 escape_string 函数进行转义处理，避免了数据中的特殊符号闭合sql语句
            execute_sql = self.__general_sql % \
                          (item['verified'], item['screen_name'], item['icon'],
                           pymysql.escape_string(item['description']), item['gender'], item['urank'],
                           item['mbtype'], item['mbrank'], item['verified_type'], item['uid'])
            cursors.execute(execute_sql)
            if 'verified_type_ext' in item.keys():
                cursors.execute(self.__type_ext_sql % (item['verified_type_ext'], item['uid']))

            if 'verified_reason' in item.keys():
                cursors.execute(self.__reason_sql % (pymysql.escape_string(item['verified_reason']), item['uid']))

        except Exception as e:
            print(e)
            traceback.print_exc()
            print('uid:' + str(item['uid']) + ' update fail!')
            log.msg(level=log.INFO, message='uid:' + str(item['uid']) + ' update fail!')

        finally:
            print('uid:' + str(item['uid']) + '\n' + 'data insert success!')
            print()

    def handle_error(self, failure):
        # print(str(item['uid']) + ' update fail!')
        # log.msg(level=log.INFO, message='uid:' + str(item['uid']) + ' update fail!')
        print("commit error?")
        log.msg(message=failure, level=log.INFO)
        print(failure)


class UidPipeline(object):
    def __init__(self):
        # 建立连接
        self.db = pymysql.connect(**(self.get_db_login()))
        # 创建游标
        self.cursor = self.db.cursor()

    def get_db_login(self):
        db_login = {}
        with open(os.getcwd() + os.sep + 'Database.cnfg', 'r') as file:
            for line in file:
                split_line = line.split('=')
                db_login[split_line[0]] = split_line[1].strip()
            file.close()
        return db_login

    def process_item(self, item, spider):
        if spider.name == 'seed_uid_spider':
            # sql语句
            insert_sql = """
            insert into user_info(uid, followers_count, follow_count) VALUES (%s,%s,%s)
                            """
            # 执行插入数据到数据库操作
            try:
                self.cursor.execute(insert_sql, (item['uid'], item['followers_count'], item['follow_count']))
            except Exception:
                print("database insert error!")
                print("duplicate uid")
                # traceback.print_exc()
                self.db.rollback()
            else:
                print('uid: ' + str(item['uid']) + '   insert success!')
            # 提交，不进行提交无法保存到数据库
            finally:
                self.db.commit()
                print('\n\n\n')
        return item


    def close_spider(self, spider):
        # 关闭游标和连接
        self.cursor.close()
        self.db.close()








# class UidPipeline(object):
#     def __init__(self, dbpool):
#         self.dbpool = dbpool
#
#     @classmethod
#     def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
#         """
#         数据库建立连接
#         :param settings: 配置参数
#         :return: 实例化参数
#         """
#         adbparams = dict(
#             host=settings['127.0.0.1'],
#             db=settings['weibo'],
#             user=settings['root'],
#             password=settings['112798'],
#             cursorclass=pymysql.cursors.DictCursor  # 指定cursor类型
#         )
#         # 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
#         dbpool = adbapi.ConnectionPool('pymysql', **adbparams)
#         # 返回实例化参数
#         return cls(dbpool)
#
#     def process_item(self, item, spider):
#         """
#         使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
#         """
#         query = self.dbpool.runInteraction(self.do_insert, item)  # 指定操作方法和操作数据
#         # 添加异常处理
#         query.addCallback(self.handle_error)  # 处理异常
#
#     def do_insert(self, cursor, item):
#         # 对数据库进行插入操作，并不需要commit，twisted会自动commit
#         insert_sql = """
#         insert into user_uid(uid, followers_count, follow_count) VALUES(%s,%s,%s,%s,%s)
#                     """
#         cursor.execute(insert_sql, (item['uid'], item['followers_count'], item['follow_count']))
#
#     def handle_error(self, failure):
#         if failure:
#             # 打印错误信息
#             print(failure)
#
#     # def process_item(self, item, spider):
#     #     try:
#     #         if spider.name == 'seed_uid_spider':
#     #             uid_info = dict(item)
#     #
#     #     except:
#     #         pass

#
# class MysqlPipelineTwo(object):




