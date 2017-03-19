# -*- coding: utf-8 -*-

from selenium import webdriver
from scrapy.http import HtmlResponse, Response
import time
import random
from eastmoney.middlewares.user_agent import USER_AGENTS as agents

class JsMiddlewares(object):

    def process_request(self, request, spider):
        if spider.name == 'em_spider':
            print('......PhantomJS is starting......')
            driver = webdriver.PhantomJS() # 指定浏览器
            driver.get(request.url)
            time.sleep(1)
            js = "var q=document.documentElement.scrollTop=10000"
            driver.execute_script(js)
            time.sleep(1)
            body = driver.page_source
            print(" .......访问" + request.url + ".......")
            return HtmlResponse(driver.current_url, body=body, encoding='utf-8',
                request=request)
        else:
            return

class UserAgentMiddleware(object):
    ''' 换Agent'''

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent
