from urllib.parse import urlencode
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
from urllib import request
import pandas as pd
import requests
import pymongo
import hashlib
import json
import time
headers = {
    'Host': 'weixin.sogou.com',
    'cookie':'IPLOC=CN1100; SUID=71D5EC7C2320940A000000005B6963B3; SUV=1533633626827777; sct=62; SNUID=30EC2D566D6B1BC139300D4B6E6D840D; ad=fZllllllll2bzQnilllllVmkrDDlllllKn8qtyllllGlllll9klll5@@@@@@@@@@; LSTMV=0%2C0; LCLKINT=156; weixinIndexVisited=1; usid=OWeS46kBjSFOpc2D; CXID=76FDA8A09C522EF2C946B00505127623; wuid=AAH4RlxpIgAAAAqGGWy/QgIAGwY=; ABTEST=7|1536655011|v1; ppinf=5|1537063845|1538273445|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTUlODUlOUMlRTUlOUMlODh8Y3J0OjEwOjE1MzcwNjM4NDV8cmVmbmljazoxODolRTUlODUlOUMlRTUlOUMlODh8dXNlcmlkOjQ0Om85dDJsdUZmcXBLSHFZWnE0MXhWN0RVSm5iSXNAd2VpeGluLnNvaHUuY29tfA; pprdig=GSlkoGOQMPMDI-Ri7wpit9RfKve2e4hSAwUjjgzqC5MEoeCoi5vXYT_SOJlahV4iY8oW6jgB29okcTj_61zkDO7euhkIDNgixXGaGPKZZioxmzbZ6mXDo2H25VLsSGLU_ozH0NzdrzYoX6J76MvdaAzyg2uRtFJAKL6MfjaAM2k; sgid=08-36489917-AVudu6Xibcua0P4xyVeOkiaeY; ppmdig=1537857405000000be17c35cf560b735c204b4f34f13ec0a; JSESSIONID=aaaJeIF4unfgAgUH74Bvw',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
}
base_url = 'http://weixin.sogou.com/weixin?'
save_url = 'http://47.94.132.150:8080/manage/news/save'
server_url ='http://47.94.132.150:8080/front/news/third/party?filename='
keyword = '服务型制造'
def get_html(url):
    print('crawling',url)
    response=requests.get(url,headers=headers)
    if response.status_code ==200:
        return response.text
    if response.status_code ==302:
        print('302')
        return None
def get_index(keyword,page):
    data={
        'query':keyword,
        'type':2,
        'page':page
        }
    query = urlencode(data)
    url = base_url + query
    html = get_html(url)
    return html
def parse_index(html):
    soup = BeautifulSoup(html,'html5lib')
    doc = pq(html)
    links = doc('.news-box .news-list li .txt-box h3 a').items()
    global publish_times
    publish_times = soup.find_all('span',attrs={'class':'s2'})
    #links = soup.find_all('a',attrs={'target':'_blank'})
    for link in links:
        yield link.attr('href')
def get_detail(url):
     response = requests.get(url)
     if response.status_code == 200:
         return response.text
         return None
def parse_detail(html):
    soup = BeautifulSoup(html,'html5lib')
    titles = soup.select('.rich_media_title')
    title = titles[0].string
    content = soup.select('.rich_media_content')
    author = soup.select('#js_name')
    img_list =soup.find_all('img',class_='')
    for img in img_list:
        srcs = img.get('data-src')
        if srcs!=None:
            src = server_url+ srcs
            del img['data-src']
            img['src']= src
    for publish_time in publish_times:
        s = publish_time.string
        return{
            'title':title.strip(),
            'content':content[0].prettify(),
            'author':author[0].get_text().strip(),
            'date':s[28:-3],
            'url':article_url,
            'source':'wechat',
            'url_md5':hashlib.md5(article_url.encode(encoding='UTF-8')).hexdigest(),
            'uploaded':false
            }
import pymongo
client = pymongo.MongoClient('localhost')
db = client['sougou-article']
def save_to_mongo(data):
    if db['test'].update_one({'title':data['title']},{'$set': data},True):
        print('Save to Mongo successfully', data['title'])
    else:
        print('Save to Mongo failed', data['title'])
def main():
    for page in range(23,101):
        html = get_index(keyword,page)
        if html:
            article_urls = parse_index(html)
            global article_url
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    global url_md5
                    url_md5 = hashlib.md5(article_url.encode(encoding='UTF-8')).hexdigest()
                    client = pymongo.MongoClient(host='localhost',port=27017)
                    db = client['sougou-article']
                    table = db['test']
                    if table.find_one({'url_md5':url_md5})==None:
                        save_to_mongo(article_data)
                        time.sleep(5)
if __name__ == '__main__':
    main()
