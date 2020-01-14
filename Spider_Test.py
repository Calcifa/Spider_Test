import queue
import requests
from lxml import etree as et
import re
import random
import time
import os
import pymysql


#用户代理列表
USER_AGENT_LIST = [
        'MSIE (MSIE 6.0; X11; Linux; i686) Opera 7.23',
        'Opera/9.20 (Macintosh; Intel Mac OS X; U; en)',
        'Opera/9.0 (Macintosh; PPC Mac OS X; U; en)',
        'iTunes/9.0.3 (Macintosh; U; Intel Mac OS X 10_6_2; en-ca)',
        'Mozilla/4.76 [en_jp] (X11; U; SunOS 5.8 sun4u)',
        'iTunes/4.2 (Macintosh; U; PPC Mac OS X 10.2)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0) Gecko/20100101 Firefox/5.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0) Gecko/20100101 Firefox/9.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20120813 Firefox/16.0',
        'Mozilla/4.77 [en] (X11; I; IRIX;64 6.5 IP30)',
        'Mozilla/4.8 [en] (X11; U; SunOS; 5.7 sun4u)'
]

#检查已下载章节
def check_chapter():
        print('正在扫描已下载的章节，请稍后！')
        db = pymysql.connect(host = host, user = user, password = password, port = port, db = database)
        cursor = db.cursor()
        sql = 'SELECT * FROM novel.novel'
        global start_chapter
        start_chapter = 1
        try:
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                        start_chapter = start_chapter + 1
                print('正在从第%d章开始下载！' %start_chapter)
        except Exception as e:
                print('Error: '+ str(e))
        finally:
                cursor.close()
                db.close()

#插入数据库
def insert_data(chapter_num, title, content):
        db = pymysql.connect(host = host, user = user, password = password, port = port, db = database)
        cursor = db.cursor()
        try:
                cursor.execute('insert into novel (chapter_num, title, content) values (%s, %s, %s)', [chapter_num, title, content])
                db.commit()
        except Exception as e:
                print('Error: '+ str(e))
        finally:
                cursor.close()
                db.close()

def get_chapter_url(list_url, base_url, queue):
        # 获取页面信息
        headers = {
                # 从代理列表随机获取代理
                'User-Agent': random.choice(USER_AGENT_LIST)
        }
        response = requests.get(url = list_url, headers = headers)
        # 获取请求状态码
        code = response.status_code
        if code == 200:
                html = et.HTML(response.content)
                # 获取该小说章节list
                id_num = start_chapter +8
                current_chapter = start_chapter
                chapter_url = html.xpath('//*[@id="list"]/dl/dd/a/@href')[id_num:40]
                for i in chapter_url:
                        #组装小说章节url
                        page_url = base_url + i
                        #将小说章节url+章节编号入队
                        queue_element = page_url, str(current_chapter)
                        queue.put(queue_element)
                        current_chapter = current_chapter + 1

#获取章节内容，存入数据库
def get_detail_html(queue):
        while not queue.empty():
                #休息一下，太快会503.等待时长可根据实际情况调节，你可以在503的边缘疯狂试探
                time_num = 5
                time.sleep(time_num)
                # Queue队列的get方法用于从队列中提取元素
                queue_element = queue.get()
                queue.task_done()
                # 获取章节url
                page_url = queue_element[0]
                # 获取章节编号
                chapter_num = queue_element[1]
                headers = {
                        # 从代理列表随机获取代理
                        'User-Agent': random.choice(USER_AGENT_LIST)
                }
                response = requests.get(url = page_url, headers = headers)
                response.encoding = "utf-8"
                # 请求状态码
                code = response.status_code
                if code == 200:
                        html = et.HTML(response.content)
                        # 获取该章小说title
                        title = chapter_num + html.xpath('//h1/text()')[0]
                        # 获取该章小说内容
                        r = html.xpath('//*[@id="content"]/text()')
                        content = ''
                        for i in r:
                                content = content + i
                        #插入数据库
                        insert_data(chapter_num, title, content)
                else:
                        print(code)
                print(title)

# 主函数
if __name__ == "__main__":

        host = 'localhost'
        user = 'root'
        password = 'Password'
        port = 3306
        database = 'novel'

        # 小说章节基地址
        base_url = 'https://www.biqugecom.com'
        # 小说章节列表页地址
        list_url = 'https://www.biqugecom.com/0/15/'

        # 用Queue构造一个先进先出队列
        urls_queue = queue.Queue()
        #检查已下载章节
        check_chapter()
        #获取章节url列表
        get_chapter_url(list_url, base_url, urls_queue)
        #获取章节内容，存入数据库
        get_detail_html(urls_queue)

        print('the end!')

