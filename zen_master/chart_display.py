import logging
from zen_master import hot_spider
from zen_master import tiktok
from apscheduler.schedulers.blocking import BlockingScheduler


def run():
    import datetime
    from zen_master.tool import Email
    from zen_master.drawing import Draw
    from zen_master.spider_ajax import ajax_run
    from zen_master.spider_html import html_run
    # ajax_run()
    # html_run()
    Draw().creation()
    e = Email(title='禅大师',
              message='这是今天的统计报告，请查收！http://47.93.186.125:9701/bai_du/master/date={}\n禅大师http://47.93.186.125:9701/bai_du/zen_master/'.format(datetime.date.today() + datetime.timedelta(-1)),
              receiver='837497936@qq.com',
              server='smtp.exmail.qq.com',
              sender='business@xianhow.com',
              password='Xianhou123',
              path='./html/{}.html'.format(datetime.date.today() + datetime.timedelta(-1))
              )
    e.send()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename='master_log.txt',
        filemode='a'
    )
    scheduler = BlockingScheduler()
    # scheduler.add_job(func=run, trigger='cron', hour=14, minute=27)
    # scheduler.add_job(func=hot_spider.run, trigger='interval', seconds=1800)
    scheduler.add_job(func=tiktok.run, trigger='interval', seconds=3)
    scheduler._logger = logging
    scheduler.start()
    scheduler.start()





