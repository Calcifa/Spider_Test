import queue
import requests
from lxml import etree as et
import re
import random
import time
import os

# 请求头
headers = {
    # 用户代理
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}

USER_AGENT_LIST = [
    'MSIE (MSIE 6.0; X11; Linux; i686) Opera 7.23',
    'Opera/9.20 (Macintosh; Intel Mac OS X; U; en)',
    'Opera/9.0 (Macintosh; PPC Mac OS X; U; en)',
    'iTunes/9.0.3 (Macintosh; U; Intel Mac OS X 10_6_2; en-ca)',
    'Mozilla/4.76 [en_jp] (X11; U; SunOS 5.8 sun4u)',
    'iTunes/4.2 (Macintosh; U; PPC Mac OS X 10.2)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0) Gecko/20100101 Firefox/5.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0) Gecko/20100101 Firefox/9.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20120813 Firefox/16.0',
    'Mozilla/4.77 [en] (X11; I; IRIX;64 6.5 IP30)',
    'Mozilla/4.8 [en] (X11; U; SunOS; 5.7 sun4u)'
]

# 保存小说文件
def save_file(dir,filename,content):
    # 如果目录不存在，则新建
    if not os.path.exists(dir):
        os.makedirs(dir)
    save_dir = dir+'/'+filename+'.txt'
    #注意：win系统默认新文件编码格式gbk,这里需指定utf-8编码
    with open(save_dir, 'w',encoding='utf-8') as f:
        f.write(content)
    print('ok')

def get_chapter_url(list_url, base_url, queue):
    # 获取页面信息
    response = requests.get(url = list_url, headers = headers)
    #print(response.text)
    # 获取请求状态码
    code = response.status_code
    if code == 200:
        html = et.HTML(response.content)
        # 获取该小说章节list
        #print(html)
        chapter_url = html.xpath('//*[@id="list"]/dl/dd/a/@href')[9:75]
        #print(chapter_url)
        k = 1
        for i in chapter_url:
            #组装小说章节url
            page_url = base_url + i
            #print(page_url)
            #将小说章节url+章节编号入队
            queue_element = page_url, str(k)
            #print(queue_element)
            queue.put(queue_element)
            k = k + 1

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
        #print(page_url)
        # 获取章节编号
        chapter_num = queue_element[1]
        #print(chapter_num)
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
            title = html.xpath('//h1/text()')[0]
            #print(title)
            # 获取该章小说内容
            r = html.xpath('//*[@id="content"]/text()')
            #print(r)
            content = ''
            for i in r:
                ## 正则匹配，去除干扰字符，只保留汉字和数字
                #data = re.sub('[\u4e00-\u9fa5]\u0030-\u0039', "", i)
                content = content + i
            #print(content)
            # 去除两端空格
            title = title.strip()
            #content = content.strip()
            #保存文件
            save_file(save_dir, title, content)
        else:
            print(code)
        print(title)

# 主函数
if __name__ == "__main__":
    # 小说章节基地址
    base_url = 'https://www.biqugecom.com'
    # 小说章节列表页地址
    list_url = 'https://www.biqugecom.com/0/15/'
    #文件保存目录,自由设置，开心就好
    path = os.getcwd()
    save_dir = path + '\\全职法师\\'
    #save_dir = os.path.abspath('../全职法师/')

    # 用Queue构造一个先进先出队列
    urls_queue = queue.Queue()
    #获取章节url列表
    get_chapter_url(list_url, base_url, urls_queue)
    #获取章节内容，存入数据库
    get_detail_html(urls_queue)

    print('the end!')


