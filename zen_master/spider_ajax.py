"""
新品发现：https://www.chandashi.com/bang/week.html   数据以ajax加载
下架监控：https://www.chandashi.com/bang/week.html   数据以ajax加载
"""
import json
import time
import requests
import datetime
from lxml import etree
from multiprocessing import Pool
from fake_useragent import UserAgent
from zen_master.tool import MySQL


class SpiderAjax(object):

    def __init__(self, url_info):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        self.yesterday = str(datetime.date.today() + datetime.timedelta(-1))
        self.url = url_info
        self.parse_html(self.url[0].format(self.yesterday))

    def parse_html(self, url):
        """ 获取html """
        response = requests.get(url, headers=self.headers)
        status = response.status_code
        if status == 200:
            html = response.text
            if 'page' in url:
                self.parse_json(html)
            else:
                self.parse_data(html)

    def parse_data(self, html):
        """ 解析html """
        root = etree.HTML(html)
        # app数量
        release_num = root.xpath('//div[@class="container"]/div/span/text()')[0]
        page_num = int(int(release_num) / 200)
        for page in range(1, page_num + 2):
            self.parse_html(url=self.url[1].format(self.yesterday, page))

    def parse_json(self, html):
        """ 解析json """
        result = json.loads(html)
        for info in result['data']:
            try:
                seller_name = info.get('sellerName', None)
                app_name = info.get('trackName', None)
                genre = info.get('genre', None)
                if str(info.get('offlineRank')) == '-':
                    offline_rank = 0
                else:
                    offline_rank = int(info.get('offlineRank', 0))
                if str(info.get('aso')) == '-':
                    aso_index = 0
                else:
                    aso_index = int(info.get('aso', 0))
                price_type = info.get('price', None)
                user_comment = int(info.get('userRatingCount', 0))
                country = info.get('country', None)
                app_pic = info.get('artworkUrl60', None)
                release_date = info.get('releaseDate', self.yesterday)
                offline_date = info.get('offlineDate', self.yesterday)
                trackId = int(info.get('trackId', 0))
            except Exception as e:
                print(e)
            try:
                MySQL().insert("insert into zen_master (seller_name, app_name, genre, offline_rank, aso_index, price_type, user_comment, country, app_pic, release_date, offline_date, save_type, trackId) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(seller_name.replace("'", '/'), app_name.replace("'", '/'), genre, offline_rank, aso_index, price_type, user_comment, country, app_pic, release_date, offline_date, self.url[2], trackId))
            except Exception as e:
                print(e)


def ajax_run():
    target_url_list = [('https://www.chandashi.com/bang/week/genre/0/date/{0}.html',
                        'https://www.chandashi.com/bang/weekdata/genre/0/date/{0}.html?page={1}', '新品'),
                       ('https://www.chandashi.com/bang/delist/genre/0/date/{0}.html',
                        'https://www.chandashi.com/bang/delistdata/genre/0/date/{0}.html?page={1}&order=rank', '下架')]
    pool = Pool(2)
    for url in target_url_list:
        pool.apply_async(func=SpiderAjax, args=(url,))
    pool.close()
    pool.join()
    pool.terminate()

