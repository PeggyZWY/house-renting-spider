#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import time
import datetime
import os

import requests
from bs4 import BeautifulSoup

import Config



class Utils(object):
    @staticmethod
    def isInBalckList(blacklist, toSearch):
        if blacklist:
            return False
        for item in blacklist:
            if toSearch.find(item) != -1:
                return True
        return False

    @staticmethod
    def getTimeFromStr(timeStr):
        # 13:47:32或者2016-05-25或者2016-05-25 13:47:32
        # 都转成了datetime
        if '-' in timeStr and ':' in timeStr:
            return datetime.datetime.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
        elif '-' in timeStr:
            return datetime.datetime.strptime(timeStr, "%Y-%m-%d")
        elif ':' in timeStr:
            date_today = datetime.date.today();
            date = datetime.datetime.strptime(timeStr, "%H:%M:%S")
            # date.replace(year, month, day)：生成一个新的日期对象
            return date.replace(year=date_today.year, month=date_today.month, day=date_today.day)
        else:
            return datetime.date.today()



class Main(object):
    douban_black_list=(u'搬家')

    def __init__(self, config):
        self.config = config
        self.douban_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-GB;q=0.2,zh-TW;q=0.2',
            'Connection': 'keep-alive',
            'DNT': '1',
            'HOST': 'www.douban.com',
            'Cookie': self.config.douban_cookie
        }
        self.ok = True

    def run(self):
        result_file_name = 'results/result_' + str(spider.file_time)
        try:
            print '打开数据库...'
            # creat database
            conn = sqlite3.connect(result_file_name + '.sqlite')
            conn.text_factory = str
            cursor = conn.cursor()
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS rent(id INTEGER PRIMARY KEY, title TEXT, url TEXT UNIQUE, itemtime timestamp, crawtime timestamp, source TEXT, keyword TEXT, note TEXT)')
            cursor.close()
            cursor = conn.cursor()


            search_list = self.config.key_search_word_list
            custom_black_list = self.config.custom_black_list
            start_time = Utils.getTimeFromStr(self.config.start_time)

            def urlList(page_number):
                num_in_url = str(page_number * 50)
                douban_url = ['https://www.douban.com/group/search?start=' + num_in_url +'&group=146409&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=523355&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=557646&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=383972&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=283855&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=76231&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=196844&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=259227&cat=1013&sort=time&q=']
                return douban_url
            douban_url_name = [u'上海租房', u'上海招聘，租房', u'上海租房(2)', u'上海合租族_魔都租房', u'上海租房@浦东租房', \
                               u'上海租房---房子是租来的，生活不是', u'上海租房@长宁租房/徐汇/静安租房', u'上海租房（不良中介勿扰）']

            def crawl(i, douban_url, keyword, douban_headers):
                url_link = douban_url[i] + keyword
                print 'url_link: ', url_link
                r = requests.get(url_link, headers=douban_headers)
                if r.status_code == 200:
                    try:
                        if i == 0:
                            self.douban_headers['Cookie'] = r.cookies
                        soup = BeautifulSoup(r.text)
                        paginator = soup.find_all(attrs={'class': 'paginator'})[0]
                        # print "paginator: ", paginator
                        if (page_number != 0) and not paginator:
                            return False
                        else:
                            try:
                                table = soup.find_all(attrs={'class': 'olt'})[0]
                                tr_count_for_this_page = 0

                                for tr in table.find_all('tr'):
                                    td = tr.find_all('td')
                                    title_element = td[0].find_all('a')[0]
                                    title_text = title_element.get('title')
                                    # ignore items in blacklist
                                    if Utils.isInBalckList(custom_black_list, title_text):
                                        continue
                                    if Utils.isInBalckList(self.douban_black_list, title_text):
                                        continue
                                    time_text = td[1].get('title')

                                    if (page_number != 0) and (Utils.getTimeFromStr(time_text) < start_time):
                                        self.ok = False
                                        # return self.ok
                                        break
                                    # ignore data ahead of the specific date
                                    if Utils.getTimeFromStr(time_text) < start_time:
                                        continue
                                    link_text = title_element.get('href');

                                    reply_count = td[2].find_all('span')[0].text
                                    tr_count_for_this_page += 1

                                    try:
                                        cursor.execute(
                                            'INSERT INTO rent(id, title, url, itemtime, crawtime, source, keyword, note) VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)',
                                            [title_text, link_text, Utils.getTimeFromStr(time_text),
                                             datetime.datetime.now(), keyword,
                                             douban_url_name[i], reply_count])
                                        print 'add new data:', title_text, time_text, reply_count, link_text, keyword
                                    except sqlite3.Error, e:
                                        print 'data exists:', title_text, link_text, e # 之前添加过了而URL（设置了唯一）一样会报错

                            except Exception, e:
                                print 'error match table:', e
                    except Exception, e:
                        print 'error match paginator:', e
                        self.ok = False
                        return False
                else:
                    print 'request url error %s -status code: %s:' % (url_link, r.status_code)
                time.sleep(self.config.douban_sleep_time)
                

            print '爬虫开始运行...'

            douban_url = urlList(0)
            for i in range(len(douban_url)):
                page_number = 0

                print 'start i ->',i
                self.ok = True
                for j in range(len(search_list)):
                    keyword = search_list[j]
                    print 'start i->j %s -> %s %s' %(i, j, keyword)
                    print '>>>>>>>>>> Search %s  %s ...' % (douban_url_name[i].encode('utf-8'), keyword)
                    
                    while self.ok:
                        print 'i, j, page_number: ', i, j, page_number
                        
                        douban_url = urlList(page_number)
                        crawl(i, douban_url, keyword, self.douban_headers)
                        page_number += 1
                        if self.ok == False:
                            break

            cursor.close()

            cursor = conn.cursor()
            cursor.execute('SELECT * FROM rent ORDER BY itemtime DESC ,crawtime DESC')
            values = cursor.fetchall()

            # export to html file
            print '爬虫运行结束。开始写入结果文件'
            
            file = open(result_file_name + '.html', 'wb')
            with file:
                file.write('''<html>
                    <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
                    <title>上海租房信息 | 豆瓣</title>
                    <link rel="stylesheet" type="text/css" href="../lib/resultPage.css">
                    </head>
                    <body>''')
                file.write('<h1>上海租房信息 | </h1>')
                file.write('''
                    <a href="https://www.douban.com/" target="_black">
                    <img src="https://img3.doubanio.com/f/shire/8977fa054324c4c7f565447b003ebf75e9b4f9c6/pics/nav/lg_main@2x.png" alt="豆瓣icon"/>
                    </a>
                    ''')
                file.write('<table>')
                file.write(
                    '<tr><th>索引</th><th>标题</th><th>发帖时间</th><th>抓取时间</th><th>关键字</th><th>来源</th><th>回复数</th></tr>')

                for row in values:
                    file.writelines('<tr>')
                    for i in range(len(row)):
                        if i == 2:
                            i += 1
                            continue
                        file.write('<td class="column%s">' % str(i))
                        if i == 1:
                            file.write('<a href="' + str(row[2]) + '" target="_black">' + str(row[1]) + '</a>')
                            i += 1
                            continue
                        file.write(str(row[i]))
                        i += 1
                        file.write('</td>')
                    file.write('</tr>')
                file.write('</table>')
                file.write('<script type="text/javascript" src="../lib/resultPage.js"></script>')
                file.write('</body></html>')
            cursor.close()
        except Exception, e:
            print 'Error:', e.message
        finally:
            conn.commit()
            conn.close()
            print '========================================='
            print '''
            ##########     ##########
            #        #     #        #
            #        #     #        #
            #   ##   #     #   ##   #
            #        #     #        #
            #        #     #        #
            ##########     ##########

            苟利租房生死以，岂因祸福避趋之。
            '''
            print '========================================='
            print '结果文件写入完毕。请打开"' + result_file_name + '.html"查看结果。'



class Spider(object):
    def __init__(self):
        this_file_dir = os.path.split(os.path.realpath(__file__))[0]
        config_file_path = os.path.join(this_file_dir, 'config.ini')
        self.config = Config.Config(config_file_path)
        FILETIMEFORMAT = '%Y%m%d_%X'
        self.file_time = time.strftime(FILETIMEFORMAT, time.localtime()).replace(':', '')
        results_path = os.path.join(sys.path[0], 'results')
        if not os.path.isdir(results_path):
            os.makedirs(results_path)

    def run(self):
        main = Main(self.config)
        main.run()



if __name__ == '__main__':
    spider = Spider()
    spider.run()

