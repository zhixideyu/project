import re
import smtplib
import pymysql
from socket import gaierror, error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Email(object):
    def __init__(self, server, sender, password, receiver, title, message=None, path=None):
        """
        初始化Email
        :param server: smtp服务器
        :param sender: 发件人
        :param password: 发件人密码
        :param receiver: 收件人
        :param title: 邮件标题
        :param message: 邮件正文
        :param path: 附件路径
        """
        self.title = title
        self.message = message
        self.files = path
        self.msg = MIMEMultipart('related')
        self.server = server
        self.sender = sender
        self.receiver = receiver
        self.password = password

    def _attach_file(self, att_file):
        """ 将单个文件添加到附件列表中 """
        att = MIMEText(open('%s' % att_file, 'rb').read(), 'plain', 'utf-8')
        att['Content-Type'] = 'application/octet-stream'
        file_name = re.split(r'[\\|/]', att_file)
        att['Content-Disposition'] = 'attachment;filename="%s"' % file_name[-1]
        self.msg.attach(att)

    def send(self):
        self.msg['Subject'] = self.title
        self.msg['From'] = self.sender
        self.msg['To'] = self.receiver

        # 邮件正文
        if self.message:
            self.msg.attach(MIMEText(self.message))

        # 添加(多个)附件
        if self.files:
            if isinstance(self.files, list):
                for f in self.files:
                    self._attach_file(f)
            elif isinstance(self.files, str):
                self._attach_file(self.files)

        # 链接服务器并发送
        try:
            smtp_server = smtplib.SMTP_SSL()
            smtp_server.connect(self.server, 465)
        except Exception as e:
            print(e)
        else:
            try:
                smtp_server.login(self.sender, self.password)
            except Exception as e:
                print(e)
            else:
                smtp_server.sendmail(self.sender, self.receiver.split(';'), self.msg.as_string())
            finally:
                smtp_server.quit()


class MySQL(object):
    """
    数据库池
    """
    host = '47.93.186.125'
    user = 'root'
    port = 3306
    pasword = '123456'
    charset = 'utf8mb4'

    def __init__(self, db='xianhou'):
        self.db = pymysql.connect(host=self.host, user=self.user, passwd=self.pasword, db=db, port=self.port, charset=self.charset, use_unicode=True)
        self.db.ping(reconnect=True)

    def select(self, sql):
        cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql)
        self.db.commit()
        result = cursor.fetchall()
        cursor.close()
        self.db.close()
        return result

    def update(self, sql):
        cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql)
        self.db.commit()
        cursor.close()
        self.db.close()

    def insert(self, sql):
        cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql)
        self.db.commit()
        cursor.close()
        self.db.close()

    def delete(self, sql):
        cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql)
        self.db.commit()
        cursor.close()
        self.db.close()


