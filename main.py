from scrapy.cmdline import execute
import sys
import os

# a = input('123')
# print(a)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# execute(['scrapy', 'crawl', 'weibo_info_spider'])
# 你需要将此处的spider_name替换为你自己的爬虫名称
# execute(['scrapy', 'crawl', 'weibo_info_spider'])
# execute(['scrapy', 'crawl', 'seed_uid_spider'])
# execute(['scrapy', 'crawl', 'user_info_spider'])

execute(['scrapy', 'crawl', 'weibo_info_spider'])