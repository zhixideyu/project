# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import urllib3
import random
import requests
from tool import MySQL, Email


sys.setrecursionlimit(1000000)
urllib3.disable_warnings()


class Douyin(object):
    def __init__(self):
        self.user_page_url = 'https://www.douyin.com/share/user/{}'
        self.base_url = "https://www.iesdouyin.com/web/api/v2/aweme/post/?" \
                        "user_id={}" \
                        "&sec_uid=" \
                        "&count=21" \
                        "&max_cursor={}" \
                        "&aid=1128" \
                        "&_signature={}" \
                        "&dytk=b689678d536d64e14d2ee9e294de2605"
        self.ids = ['72075125018', '104722236524', '104423231197', '3812716197721332', '1763235740517720', '69970607492', '3328972857809912', '6807107055', '71841131267', '3276186316973452', '66615900141', '102744294192', '59174715782', '93189025747', '62100530690', '59220767995', '945170971374151', '58078054954', '92924207628', '81939158402', '59236021525', '111360067396', '110541851171', '105822411951', '111424174425', '12246432093', '62839305427', '95788634804', '104990007925', '98187566200', '84931730372', '100878185674', '58546460081']
        # 该参数决定页数
        self.max_cursor = 0
        self.headers = {
            'User-Agent': random.choice(['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36', 'Win7:Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'])
        }
        self.count = 0
        # self.proxy_info = eval(requests.get('http://123.56.169.139/proxypool_adsl/api/api.php?code=1002&num=1&proxy_source=adsl').text)[0]
        # self.http_proxy = {'http': '{}:{}'.format(self.proxy_info['host'], self.proxy_info['port'])}

    def get_url(self):
        # 遍历构造url
        for id in self.ids:
            while True:
                try:
                    # signature = os.popen('node /home/project/zen_master/douyin_fuck.js %s' % id)
                    signature = os.popen('node douyin_fuck.js %s' % id)
                    self.s = signature.read()
                    self.url = self.base_url.format(id, 0, self.s)
                    self.get_request(id, self.url)
                except Exception as e:
                    print(e)
                    time.sleep(2)
                else:
                    break

    def get_request(self, id, url):
        response = requests.get(url, headers=self.headers, verify=False)
        self.content = response.json()

        if str(self.content['has_more']) == '0' or len(self.content['aweme_list']) == 0:
            self.count += 1
            self.get_request(id, url)
        else:
            print('请求成功')
            self.count = 0
            self.get_aweme(id, self.content)

    def get_aweme(self, id, content):
        info_list = content['aweme_list'][:5]
        result_list = list()
        for info in info_list:
            desc = info['desc']
            aweme_id = info['aweme_id']
            result_list.append({aweme_id: desc})
        spider_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        response = requests.get(self.user_page_url.format(id), headers=self.headers, verify=False)
        pattern = re.compile(r'<p class="nickname">(.*?)</p>', re.S)
        nick_name = re.findall(pattern, response.text)[0]
        sql = 'select aweme_id from user_info where user_id="%s"' % (id)
        user_info = MySQL('tiktok').select(sql)
        aweme_id_list = [list(result.keys())[0] for result in result_list]
        desc_list = [list(result.values())[0] for result in result_list]
        if len(user_info) == 0:
            sql = 'insert into user_info(user_id, aweme_id) VALUES ("{}", "{}")'.format(id, aweme_id_list)
            MySQL('tiktok').insert(sql)
            print('添加成功')
        else:
            user_info = user_info[0]
        if aweme_id_list[0] in user_info['aweme_id']:
            print('未更新')
        else:
            try:
                sql = 'update user_info set aweme_id="%s" where user_id="%s"' % (aweme_id_list, id)
                MySQL('tiktok').update(sql)
                print('修改成功')
            except Exception as e:
                print(e)
            else:
                e = Email(title='抖音更新提醒',
                          message='{} {} {} {} {}'.format(spider_time, id, nick_name, desc_list[0], 'https://www.douyin.com/share/video/{}'.format(aweme_id_list[0])),
                          receiver='837497936@qq.com;',
                          server='smtp.exmail.qq.com',
                          sender='business@xianhow.com',
                          password='Xianhou123',
                          )
                e.send()
                print('邮件发送成功')


def run():
    Douyin().get_url()

