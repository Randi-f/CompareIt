'''
Author: shihan
Date: 2023-11-07 21:00:43
version: 1.0
description: 
'''
import math
from flask import Flask, render_template, jsonify, request
from lxml import html
import requests

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("compare.html")
    # return "Hello , my new app!"

@app.route("/keywordsubmit", methods=['POST'])
def keywordsubmit():
    keyword = request.form.get("keyword")
    
    # return keyword




    products_list = send_resuest(keyword)
    return products_list
    # return "Hello , my new app!"

def send_resuest(keyword):
    products_list=[]
    """ 爬取京东的商品数据 """
    # url = 'https://search.jd.com/Search?keyword={0}&enc=utf-8'.format(word)
    url = 'https://search.jd.com/Search?keyword='+keyword+'&enc=utf-8'


    # get html file
    respons = requests.get(url)
    respons.encoding = 'utf-8'
    html_doc = respons.text

    # print(html_doc)
    # 打开文件，如果文件不存在则创建，如果文件已存在则覆盖其内容
    #open the file and create one if it does not exist. if it exists, overwrite it
    with open('test.html', 'w') as file:
        # 写入数据到文件 write the data into the file
        file.write(html_doc)
        # 文件写入完成后，自动关闭文件，不需要再调用 file.close()
        # after the file is written, it is auto closed

    # 获取xpath对象 get element fot xpath
    selector = html.fromstring(html_doc)

    # 找到列表的集合, find the set of the list
    ul_list = selector.xpath('//div[@id="J_goodsList"]/ul/li')

    # 解析对应的标题,价格,链接,店铺 analyze the title, price, market
    for li in ul_list:
        # 标题 title
        title = li.xpath('div/div[@class="p-name p-name-type-2"]/a/em/text() | '
                         'div/div[@class="p-name"]/a/@title')
        # 购买链接 link to buy it
        link = li.xpath('div/div[@class="p-name p-name-type-2"]/a/@href | '
                        'div/div[@class="p-name"]/a/@href')
        # 价格 price
        price = li.xpath('div/div[@class="p-price"]/strong/i/text() | '
                         'div/div[@class="p-price"]/strong/i/text()')
        # 店铺 manufacturer
        store = li.xpath('div/div[@class="p-shop"]//a/text() | '
                         'div//a[@class="curr-shop"]/@title')
        products_list.append({
                'title': title[0],
                'price': price[0],
                'link': 'https:' + link[0],
                'store': store[0],
                'referer': '京东'
            })
    return products_list



