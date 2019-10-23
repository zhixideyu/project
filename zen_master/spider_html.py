"""
清词应用：https://www.chandashi.com/bang/clearlist/genre/0/date/2019-07-18.html  数据展示在html
清榜应用：https://www.chandashi.com/bang/clearbanglist/genre/0/date/2019-07-18.html  数据展示在html
"""
import re
import requests
import datetime
from lxml import etree
from multiprocessing import Pool
from fake_useragent import UserAgent
from zen_master.tool import MySQL


class SpiderHtml(object):
    def __init__(self, url_info):
        self.url_info = url_info
        self.headers = {
            'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        self.yesterday = str(datetime.date.today() + datetime.timedelta(-1))
        self.url = self.url_info[0].format(self.yesterday)
        self.parse_html(self.url)

    def parse_html(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            html = response.text
            self.parse_data(html)

    def parse_data(self, html):
        root = etree.HTML(html)
        clear_word_num = root.xpath('//div[@class="container"]/div/span/text()')[0]
        app_info = root.xpath('//div[@class="js-mobile-content"]/div')
        # 卖方名称
        seller_name = re.findall(re.compile('developer">(.*?)</p>', re.S), html)
        # 评论数
        user_comment = re.findall(re.compile('js-comments">(.*?)</span>', re.S), html)
        # 发布日期
        release_date = re.findall(re.compile('js-comments">.*?</span></td>.*?<td>(.*?)</td>', re.S), html)
        for index, info in enumerate(app_info):
            # App名称
            app_name = info.xpath('div/div[@class="desc"]/a/text()')[0]
            # App图片
            app_pic = info.xpath('div/a[@class="logo"]/img/@src')[0]
            app_info = info.xpath('div/div[@class="desc"]/div/span[1]/text()')[0]
            # 分类名称
            genre = app_info.split('(')[0]
            # 收费类型
            price_type = app_info.split('(')[1].strip(')')
            try:
                MySQL().insert("insert into zen_master (seller_name, app_name, genre, offline_rank, aso_index, price_type, user_comment, country, app_pic, release_date, offline_date, save_type) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(seller_name[index].replace("'", '/'), app_name.replace("'", '/'), genre, 0, 0, price_type, int(user_comment[index]), None, app_pic, release_date[index].split(' ')[0], self.yesterday, self.url_info[1]))
            except Exception as e:
                print(e)


def html_run():
    target_url_list = [('https://www.chandashi.com/bang/clearlist/genre/0/date/{0}.html', '清词'),
                       ('https://www.chandashi.com/bang/clearbanglist/genre/0/date/{0}.html', '清榜')]
    pool = Pool(len(target_url_list))
    for url in target_url_list:
        pool.apply_async(func=SpiderHtml, args=(url,))
    pool.close()
    pool.join()
    pool.terminate()