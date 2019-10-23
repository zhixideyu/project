import datetime
from zen_master.tool import MySQL
from pyecharts import Bar, Page, Style


class Draw(object):
    def __init__(self):
        self.page = Page()
        self.style = Style(width=1100, height=600)
        self.yesterday = datetime.date.today() + datetime.timedelta(-1)

    def one_pic(self):
        """ 新品与下架数据示例 """
        new_app_list = list()
        download_app_list = list()
        app_genre_info = MySQL().select(
            "select genre from zen_master where offline_date='{}' and (save_type='{}' or save_type='{}')".format(
                self.yesterday, '新品', '下架'))
        app_genre_list = list(set(info['genre'] for info in app_genre_info))
        for genre in app_genre_list:
            new_app_list.append(MySQL().select(
                "select count(*) from zen_master where offline_date='{}' and genre='{}' and save_type='{}'".format(
                    self.yesterday, genre, '新品')))
            download_app_list.append(MySQL().select(
                "select count(*) from zen_master where offline_date='{}' and genre='{}' and save_type='{}'".format(
                    self.yesterday, genre, '下架')))
        bar = Bar('新品与下架数据示例', **self.style.init_style)
        bar.add('新品发现', app_genre_list, [info[0]['count(*)'] for info in new_app_list], is_stack=False,
                is_more_utils=True, xaxis_interval=0, xaxis_rotate=30, yaxis_rotate=30, is_label_show=True)
        bar.add('下架监控', app_genre_list, [info[0]['count(*)'] for info in download_app_list], is_stack=False,
                is_more_utils=True, xaxis_interval=0, xaxis_rotate=30, yaxis_rotate=30, is_label_show=True)
        self.page.add(bar)

    def two_pic(self):
        """ 新品发现、下架监控近30天示例 """
        data_list = list()
        new_app_total_list = list()
        download_app_total_list = list()
        begin = datetime.date(2019, 7, 21)
        end = datetime.date(2019, 8, 22)
        d = begin
        delta = datetime.timedelta(days=1)
        while d <= end:
            data_list.append(d.strftime("%Y-%m-%d"))
            d += delta
        for data in data_list:
            new_app_total_list.append(MySQL().select(
                "select count(*) from zen_master where offline_date='{}' and save_type='{}'".format(data, '新品')))
            download_app_total_list.append(MySQL().select(
                "select count(*) from zen_master where offline_date='{}' and save_type='{}'".format(data, '下架')))
        bar2 = Bar('新品发现、下架监控近30天示例', **self.style.init_style)
        bar2.add('新品发现', data_list, [info[0]['count(*)'] for info in new_app_total_list], is_stack=False,
                 is_more_utils=True, xaxis_interval=0, xaxis_rotate=30, yaxis_rotate=30, is_label_show=True)
        bar2.add('下架监控', data_list, [info[0]['count(*)'] for info in download_app_total_list], is_stack=False,
                 is_more_utils=True, xaxis_interval=0, xaxis_rotate=30, yaxis_rotate=30, is_label_show=True)
        self.page.add(bar2)

    def three_pic(self):
        """ 清词与清榜数据示例 """
        word_list = list()
        top_list = list()
        app_genre_info = MySQL().select(
            "select genre from zen_master where offline_date='{}' and (save_type='{}' or save_type='{}')".format(
                self.yesterday, '清词', '清榜'))
        app_genre_list = list(set(info['genre'] for info in app_genre_info))
        for genre in app_genre_list:
            word_list.append(MySQL().select(
                "select count(*) from zen_master where offline_date='{}' and genre='{}' and save_type='{}'".format(
                    self.yesterday, genre, '清词')))
            top_list.append(MySQL().select(
                "select count(*) from zen_master where offline_date='{}' and genre='{}' and save_type='{}'".format(
                    self.yesterday, genre, '清榜')))
        bar3 = Bar('清词与清榜数据示例', **self.style.init_style)
        bar3.add('清词应用', app_genre_list, [info[0]['count(*)'] for info in word_list], is_stack=False,
                 is_more_utils=True,
                 xaxis_interval=0, xaxis_rotate=30, yaxis_rotate=30, is_label_show=True)
        bar3.add('清榜应用', app_genre_list, [info[0]['count(*)'] for info in top_list], is_stack=False, is_more_utils=True,
                 xaxis_interval=0, xaxis_rotate=30, yaxis_rotate=30, is_label_show=True)
        self.page.add(bar3)

    def creation(self):
        """ 开始画图，并修改文件 """
        self.one_pic()
        self.two_pic()
        self.three_pic()
        self.page.render('./html/{}.html'.format(self.yesterday))
        download_app_info = [(x['app_name'], x['offline_rank'], x['trackId']) for x in MySQL().select(
            "select app_name, offline_rank, trackId from zen_master where offline_rank <= %d and save_type='%s' and offline_rank != %d and offline_date='%s'" % (
                150, '下架', 0, self.yesterday))]
        html_str = ''
        for index, info in enumerate(download_app_info):
            html_str += """          
   <tr>
   <td>{}</td>
   <td>{}</td>
   <td>{}</td>
   <td>{}</td>
   </tr>
                       """.format(index + 1, info[0], info[2], info[1])
        clear_app_info = [(x['app_name'], x['offline_rank']) for x in MySQL().select(
            "select app_name, offline_rank from zen_master where offline_rank <= %d and save_type='%s' and offline_rank != %d and offline_date='%s'" % (
                150, '清榜', 0, self.yesterday))]
        if len(clear_app_info) == 0:
            clear_app_info = [('无', '无')]
        html2_str = ""
        for index2, info2 in enumerate(clear_app_info):
            html2_str += """          
        <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
                        """.format(index2 + 1, info2[0], info2[1])
        num_result_list = list()
        for price_type in ['免费', '付费']:
            for save_type in ['新品', '下架', '清词', '清榜']:
                info = MySQL().select(
                    "select count(*) from zen_master where offline_date='{}' and save_type='{}' and price_type='{}'".format(self.yesterday, save_type, price_type))
                for x in info:
                    number = x['count(*)']
                num_result_list.append((save_type, price_type, number))
        html3_str = ''
        result = list()
        for index1, x in enumerate(num_result_list[:len(num_result_list)//2]):
            for index2, y in enumerate(num_result_list[len(num_result_list)//2:]):
                if index1 == index2:
                    result.append([x[0], y[2], x[2]])
                    html3_str += """
                            <tr>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            </tr>
                                            """.format(x[0], y[2], x[2])

        num_result_list2 = list()
        for price_type in ['免费', '付费']:
            for save_type in ['新品', '下架', '清词', '清榜']:
                info = MySQL().select(
                    "select count(*) from zen_master where offline_date='{}' and save_type='{}' and price_type='{}'".format(datetime.date.today() + datetime.timedelta(-2), save_type, price_type))
                for x in info:
                    number = x['count(*)']
                num_result_list2.append((save_type, price_type, number))
        html4_str = ''
        for index1, x in enumerate(num_result_list2[:len(num_result_list2) // 2]):
            for index2, y in enumerate(num_result_list2[len(num_result_list2) // 2:]):
                if index1 == index2:
                    html4_str += """
                            <tr>
                            <td>{}</td>
                            <td>{}</td>
                            </tr>
                                            """.format(y[2], x[2])
        file = open("./html/{}.html".format(self.yesterday), 'r', encoding='utf8')
        content = file.read()
        keyword = '</head>'
        post = content.find(keyword)
        if post != -1:
            content = content[:post + len(keyword)] + """
<h1>各类型产品收费类型数据</h1>
<table border="1" style="float:left; width:300px;">
<tr>
<td rowspan="1" width="72">产品类别</td>
<td rowspan="1">付费(昨天)</td>
<td rowspan="1">免费(昨天)</td>
</tr>
{2}
</table>
<table border="1" style="float:left; width:300px;";>
<tr>
<td rowspan="1">付费(前天)</td>
<td rowspan="1">免费(前天)</td>
</tr>
{3}
</table> 
<div style="float:left">
<table>
<h1>下架产品近期最高排名150名以内</h1>
<tbody>
<tr>
<td rowspan="1" width="72">序号</td>
<td rowspan="1">App名称</td>
<td rowspan="1" width="72">AppID</td>
<td rowspan="1">排名</td>
</tr>
{0}
</tbody>
</table> 
<table>
</div>
<h1>清榜产品前排名150名以内</h1>
<tbody>
<tr>
<td rowspan="1" width="72">序号</td>
<td rowspan="1">App名称</td>
<td rowspan="1">排名</td>
</tr>
{1}
</tbody>
</table>
        """.format(html_str, html2_str, html3_str, html4_str) + content[post + len(keyword):]
        file = open("./html/{}.html".format(self.yesterday), 'w', encoding='utf8')
        file.write(content)
        file.close()
