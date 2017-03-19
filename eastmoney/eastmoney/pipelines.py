# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from eastmoney.items import FenceItem, TweetItem, UserItem

class EastmoneyPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['Easrmoney']
        self.Fence = db['Fence']
        self.Tweet = db['Tweet']
        self.User = db['User']

    def process_item(self, item, spider):
        ''' 判读Item类型，作出相应的处理，再倒入数据库'''
        if isinstance(item, FenceItem):
            try:
                self.Fence.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, TweetItem):
            try:
                self.Tweet.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, UserItem):
            try:
                self.User.insert(dict(item))
            except Exception:
                pass
                
        return item
