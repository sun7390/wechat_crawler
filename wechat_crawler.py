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
    'cookie':'pgv_pvi=7033318400; pt2gguin=o0739014282; RK=JEgZbrswTP; ptcz=94d9e55cb78ad4b1309da5ecac909c30d35b131a77e9e3cbf7304f989204875e; pgv_pvid=9945695000; o_cookie=739014282; pac_uid=1_739014282; rewardsn=; wxtokenkey=777',
    'Host': 'weixin.sogou.com',
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
def test_url(url):
    md = hashlib.md5(url.encode(encoding='UTF-8')).hexdigest()
    with open('./md5.txt','r') as f:
        exist = False
        lines = f.readlines()
        for line in lines:
            if (line==md):
                exist =True
        if exist == False:
            with open('./md5.txt','a') as t:
                t.writelines(md+'\n')
        return exist
                
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
            'upload':'False'
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
    for page in range(8,101):
        html = get_index(keyword,page)
        if html:
            article_urls = parse_index(html)
            global article_url
            for article_url in article_urls:
                if test_url(article_url)==False:
                    article_html = get_detail(article_url)
                    if article_html:
                        article_data = parse_detail(article_html)
                        save_to_mongo(article_data)
                        time.sleep(5)
if __name__ == '__main__':
    main()
