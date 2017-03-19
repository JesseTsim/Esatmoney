# -*- coding: utf-8 -*-

import re
import datetime
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from selenium import webdriver
from bs4 import BeautifulSoup

from eastmoney.items import UserItem, TweetItem, FenceItem

class Spider(scrapy.Spider):

    name = 'em_spider'

    host = 'http://guba.eastmoney.com/'
    start_urls =[
        'list,cjpl_1.html', 'list,gssz_1.html', 'list,szzs_1.html'
    ]
    allowed_domains = ['eastmoney.com']

    # scrawl_url = set(start_urls) # 记录待爬的链接
    finished_url = set() # 记录已爬的链接
    User_id = set() # 记录用户ID

    def start_requests(self):
        for url in self.start_urls[:1]:
            self.finished_url.add(url) # 加入已爬取的队列
            Count = 1 # 记录页面数

            Tweets_id = []
            FenceItems = FenceItem()
            FenceItems['Tweet_id'] = Tweets_id

            url_fence = self.host + url

            yield Request(url=url_fence, meta={"item": FenceItems, "Page_URL": url_fence, "Count": Count},
                callback=self.parse0) # 进入版块

    def parse0(self, response):
        ''' 爬取版块当前页面'''
        selector = Selector(response)
        tweets_url = selector.xpath(u'//div[@class="articleh" or class="articleh odd"]/span[@class="l3"]/a/@href').extract() # 爬取各贴链接

        FenceItems = response.meta["item"]
        FenceItems['Tweet_id'] += tweets_url
        starts_url = set(tweets_url)
        Count = response.meta["Count"] # 当前页码
        if Count == 1:
            FenceItems['Fence_Name'] = selector.xpath(u'//span[@id="stockif"]/span/a/text()')[0].extract() # 版块名


        # 爬取各贴
        while starts_url.__len__():
            url = starts_url.pop()
            if url not in self.finished_url:
                self.finished_url.add(url) # 加入已爬取的队列
                if url[0] == u'/':
                    url = self.host + url[1:]
                elif url.startswith('http'):
                    tweets_url.remove(url)
                    continue
                else:
                    url = self.host + url
                print('------ Start Crwaling Tweets ------')
                try:
                    yield Request(url=url, meta={'Url': url, "Fence_Name": FenceItems['Fence_Name'], "Count": Count},
                        callback=self.parse1)
                    pass
                except Exception:
                    print('------ Fail to Crawl %s ------' % url)

        # 翻页
        # next_pages = selector.xpath('//span[@class="sumpage"]/text()').extract()
        # next_pages = int(next_pages[0]) # 获取总页数
        # FenceItems['Num_page'] = next_pages
        # print('------- sum page %d -------' % next_pages)

        Page_URL = response.meta['Page_URL']

        if Count <= 1000: # 控制爬取页面数
            Count += 1
            url = Page_URL[:-7] + '_%d.html' % Count
            self.finished_url.add(url) # 加入已爬取的队列
            print('----- Start Crawling Next Page ------')
            yield Request(url=url, meta={"item": FenceItems, "Page_URL": url, "Count": Count},
                callback=self.parse0)
        else:
            print('------ Crawling End ------')
            yield FenceItems
            pass


    def parse1(self, response):
        ''' 爬取贴信息'''
        selector = Selector(response)

        UserItems = UserItem()
        _id = selector.xpath(u'//strong/a/@data-popper').extract()
        NickName = selector.xpath(u'//strong/a/text()').extract()
        if _id:
            UserItems['_id'] = _id[0]
        else:
            UserItems['_id'] = 'None'
        if NickName:
            UserItems['NickName'] = NickName[0]
        else:
            UserItems['NickName'] = 'None'

        # 爬取发帖用户
        # if UserItems['_id'] in self.User_id:
        #     pass
        # else:
        #     self.User_id.add(UserItems['_id'])
        #     User_url = selector.xpath(u'//strong/a/@href')[0].extract()
        #     print('------ Start Crawling User %s End ------' % UserItems['NickName'])
        #     try:
        #         yield Request(url=User_url, meta={'Item': UserItems}, callback=self.parse2)
        #     except Exception:
        #         pass

        # 爬取贴文
        TweetItems = TweetItem()
        TweetItems['User_id'] = UserItems['_id'] # 发帖人IDT

        TweetItems['Fence_Name'] = response.meta['Fence_Name'] # 记录所在版块

        Url = response.meta['Url']
        url = re.findall('[0-9]+', Url)[0]
        TweetItems['_id'] = url # 贴ID
        TweetItems['Page'] = response.meta['Count'] # 贴所在页码

        Topic = selector.xpath(u'//div[@id="zwconttbt"]/text()')[0].extract()
        TweetItems['Topic'] = Topic.strip() # 贴主题

        Content = selector.xpath(u'//div[@id="zw_body"]//p/text()').extract()
        if not Content:
            Content = selector.xpath(u'dic[@class="stockcodec"]/p/text()').extract()
        text = ''
        for i in Content:
            text += i
        TweetItems['Content'] = text # 贴文正文

        time = selector.xpath(u'//div[@class="zwfbtime"]/text()')[0].extract()
        time = re.findall('[0-9]+-[0-9]+-[0-9]+', time)[0]
        TweetItems['Date'] = time # 发帖时间

        # Num_read = selector.xpath(u'//span[@class="tc1"]/text()')[0].extract() # 阅读数
        # TweetItems['Num_read'] = int(Num_read)
        # Num_comment = selector.xpath(u'//span[@class="tc1"]/text()')[1].extract() # 评论数
        # TweetItems['Num_comment'] = int(Num_comment)

        print('------ Crawling Tweet End -------')
        yield TweetItems
        pass


    def parse2(self, response):
        ''' 爬取用户信息'''
        selector = Selector(response)
        UserItems = response.meta['Item']

        Num_tweets = selector.xpath(u'//div[@class="grtab5"]/ul/li[@class="on"]/a/text()')[0].extract()
        Num = re.findall('[0-9]+', Num_tweets)[0]
        UserItems['Num_tweets'] = int(Num) # 记录发帖数

        Num_folloer = selector.xpath(u'//td[@class="norb"]/a/em/text()')[0].extract()
        UserItems['Num_folloer'] = int(Num_folloer) # 记录粉丝数

        Date = selector.xpath(u'//div[@id="influence"]/span[3]/text()')[0].extract()
        date = re.findall('[0-9]+-[0-9]+-[0-9]+', Date)[0]
        UserItems['Age'] = date # 记录吧龄

        print('------ Crawling User %s End-------' % UserItems['NickName'])
        yield UserItems
        pass
