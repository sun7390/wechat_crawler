import pymongo
import pandas as pd
import requests
import json
headers={
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }
url = "http://47.94.132.150:8080/manage/news/save"
client = pymongo.MongoClient(host='localhost',port=27017)
db = client['sougou-article']
table = db['test']
data = pd.DataFrame(list(table.find()))
s1 = data['title'].items()
s2 = data['content'].items()
s3 = data['source'].items()
s4 = data['date'].items()
s5 = data['uploaded'].items()
for (i,j,k,l,p) in zip(s1,s2,s3,s4,s5):
    if p[1]==False:
        payload = {'title':i[1],'text':j[1],'tagId':19,'source':k[1],'createtime':l[1]}
        r=requests.post(url,data=payload)
        json_str=json.loads(r.text)
        print(json_str['data'])
        table.update_one({'title':i[1]},{'$set':{"return_id":json_str['data']}})
        table.update_one({'title':i[1]},{'$set':{"upload":'true'}})

    else:
        print("already uploaded!")
