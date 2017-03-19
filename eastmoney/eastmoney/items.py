# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EastmoneyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class UserItem(scrapy.Item):
    ''' 用户信息'''
    _id = scrapy.Field() # 用户ID
    NickName = scrapy.Field() # 用户名
    Num_tweets = scrapy.Field() # 发帖数
    Num_folloer = scrapy.Field() # 粉丝数
    Age = scrapy.Field() # 注册日期
    pass

class TweetItem(scrapy.Item):
    ''' 贴信息'''
    User_id = scrapy.Field() # 用户ID
    _id = scrapy.Field() # 贴ID
    Topic = scrapy.Field() # 贴主题
    Content = scrapy.Field() # 贴内容
    Date = scrapy.Field() # 发帖时间
    Num_read = scrapy.Field() # 阅读数
    Num_comment = scrapy.Field() # 评论数
    Fence_Name = scrapy.Field() # 所在版块
    Page = scrapy.Field() # 所在页码
    pass

class FenceItem(scrapy.Item):
    ''' 板块信息'''
    Fence_Name = scrapy.Field() # 版块名
    Tweet_id = scrapy.Field() # 贴ID
    Num_page = scrapy.Field() # 版块页数
    pass
