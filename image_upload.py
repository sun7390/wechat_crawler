import requests
from bs4 import BeautifulSoup
from urllib import request
import json
url ='https://mp.weixin.qq.com/s?src=3&timestamp=1537410228&ver=1&signature=en1f1jHlIl*zsjoyjRtNiXbTx-uwgx*XU1Dg6N5eK0FKYnBPqcO5A0fbioSH0fMf7i6J3A2tm9Aub9mKMJgPa-5nzoqTvRY6moD0CJc1NhFJexJOMLzcFFZ4t7lFoRHJf0zw3uDkXpQ3Rfry3vZKYgbeG3JcaqyxhkI-k1N4qtU='
server_url ='http://47.94.132.150:8080/manage/news/upload/'
response=requests.get(url)
soup = BeautifulSoup(response.text,'html5lib')
title = soup.select('.rich_media_title')
content = soup.select('.rich_media_content')
author = soup.select('#js_name')
img_list =soup.find_all('img',class_='')
x=0
for img in img_list:
    src = img.get('data-src')
    if src!=None:
        request.urlretrieve(src,'./image/%s.jpg' %x)
        file ={'file':open('C:/Users/Administrator/Desktop/image/{}.jpg'.format(x),'rb')
               }
        r=requests.post(server_url,files=file)
        json_str=json.loads(r.text)
        img_name=json_str['data']
        x+=1
        
        
        
