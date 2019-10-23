import time
import requests
import datetime
from lxml import etree
from multiprocessing import Pool
from zen_master.tool import MySQL
from apscheduler.schedulers.blocking import BlockingScheduler


class HotSpider(object):

    def __init__(self, url_info):
        self.url = url_info
        self.base_url = 'https://s.weibo.com'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        self.parse_html(self.url)

    def parse_html(self, url):
        response = requests.get(url, headers=self.headers)
        if 'weibo.com' in url:
            html = response.text
            self.parse_weibo_data(html)
        elif 'baidu.com' in url:
            html = response.content.decode('gbk')
            self.parse_baidu_data(html)

    def parse_weibo_data(self, html):
        sql = "select key_word from weibo_hot"
        title_list = [x['key_word'] for x in MySQL().select(sql)]
        root = etree.HTML(html)
        info_list = root.xpath('//div[@class="data"]/table/tbody/tr')
        for info in info_list:
            title = info.xpath('td[@class="td-02"]/a/text()')[0]
            href = self.base_url + info.xpath('td[@class="td-02"]/a/@href')[0]
            grade = '无' if len(info.xpath('td[@class="td-03"]/i/text()')) == 0 else \
                info.xpath('td[@class="td-03"]/i/text()')[0]
            if title not in title_list:
                sql = "insert into weibo_hot(key_word, href, grade, date) values ('{}', '{}', '{}', '{}')".format(title, href, grade, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                MySQL().insert(sql)

    def parse_baidu_data(self, html):
        sql = "select key_word from baidu_hot"
        title_list = [x['key_word'] for x in MySQL().select(sql)]
        root = etree.HTML(html)
        info_list = root.xpath('//div[@class="mainBody"]/div[@class="grayborder"]/table/tr/td[@class="keyword"]')
        for info in info_list:
            title = info.xpath('a[1]/text()')[0]
            href = info.xpath('a[1]/@href')[0]
            if title not in title_list:
                sql = "insert into baidu_hot(key_word, href, date) values ('{}', '{}', '{}')".format(title, href, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                MySQL().insert(sql)


def run():
    mission_url = ['https://s.weibo.com/top/summary?cate=realtimeho', 'http://top.baidu.com/buzz?b=1&fr=topindex']
    pool = Pool(len(mission_url))
    for url in mission_url:
        pool.apply_async(func=HotSpider, args=(url,))
    pool.close()
    pool.join()
    pool.terminate()



