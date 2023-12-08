'''
Author: shihan
Date: 2023-12-08 22:43:02
version: 1.0
description: 
'''
import requests
from lxml import html





def send_request_JD(keyword):
    # print("sending")
    products_list = []
    """ 爬取京东的商品数据 """
    # cookies = dict(thor="A7943E8CDECC88D3F6714286FE2134796C45A5955EA9670F972DBCCBA5D7C0B9F604D0E0CD44219B79DFE31968B2A0D39401BB4812F5E98528728F86ECF2909DB71307217CAE6D4BA887B7206D2CC6850736D97252419EE6DF53B7CD3230A2E6529F3A04E30F5A9EBCBF16FEDE1827759DA5D2C3B8FFA0F955EC9F8161A487DFD66370DF24315D2A853FC04CFA2158C398B378AADC1B28AC199AD9EAA65E602F")

    cookies = {'thor':'A7943E8CDECC88D3F6714286FE2134796C45A5955EA9670F972DBCCBA5D7C0B9F604D0E0CD44219B79DFE31968B2A0D39401BB4812F5E98528728F86ECF2909DB71307217CAE6D4BA887B7206D2CC6850736D97252419EE6DF53B7CD3230A2E6529F3A04E30F5A9EBCBF16FEDE1827759DA5D2C3B8FFA0F955EC9F8161A487DFD66370DF24315D2A853FC04CFA2158C398B378AADC1B28AC199AD9EAA65E602F'}
    # url = "https://search.jd.com/Search?keyword=" + keyword + "&enc=utf-8"
    url = "https://search.jd.com/Search?keyword=" + keyword

    response = requests.get(url, cookies=cookies)
    # Check the status code
    if response.status_code == 200:
        print("Request was successful!")
        print("Status code:", response.status_code)
    else:
        print("Request failed!")
        print("Status code:", response.status_code)

    response.encoding = "utf-8"
    html_doc = response.text
    # print(html_doc)
    selector = html.fromstring(html_doc)

    # 所有的商品数据都是通过ul标签进行渲染, 每单个数据，则是用li标签渲染
    ul_list = selector.xpath('//div[@id="J_goodsList"]/ul/li')
    if len(ul_list) == 0:
        products_list.append(
            {
                "title": "network error",
                "price": "-",
                "link": "try later for JD goods",
                "store": "-",
                "referer": "JD",
            }
        )
        return products_list
    for li in ul_list:
        title = li.xpath(
            'div/div[@class="p-name p-name-type-2"]/a/em/text() | '
            'div/div[@class="p-name"]/a/@title'
        )

        link = li.xpath(
            'div/div[@class="p-name p-name-type-2"]/a/@href | '
            'div/div[@class="p-name"]/a/@href'
        )

        price = li.xpath(
            'div/div[@class="p-price"]/strong/i/text() | '
            'div/div[@class="p-price"]/strong/i/text()'
        )

        store = li.xpath(
            'div/div[@class="p-shop"]//a/text() | ' 'div//a[@class="curr-shop"]/@title'
        )
        products_list.append(
            {
                "title": title[0],
                "price": price[0],
                "link": "https:" + link[0],
                "store": store[0],
                "referer": "JD",
            }
        )
        # print()

    return products_list

print(send_request_JD("bottle"))