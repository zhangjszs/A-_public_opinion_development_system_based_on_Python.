import requests
import csv
import os
import numpy as np
def init():
    if not os.path.exists('navData.csv'):
        with open('navData.csv','w',encoding='utf8',newline='') as csvfile:
            wirter = csv.writer(csvfile)
            wirter.writerow([
                'typeName',
                'gid',
                'containerid'
            ])

def wirterRow(row):
        with open('navData.csv','a',encoding='utf8',newline='') as csvfile:
            wirter = csv.writer(csvfile)
            wirter.writerow(row)

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        # !!! 注意：这里的 Cookie 仍然是硬编码的，它会过期 !!!
        'Cookie': 'SINAGLOBAL=7212852614896.057.1722674779243; SCF=AuBnnYbv5UcU0Em9mzgayCIUin7u9gaSXe7Ioo3XKiTjesfDU7n5afCo3g09azYPzLTX9x6dK2qs4urCz3KBY5I.; ULV=1745148345761:2:1:1:8580936394154.282.1745148345707:1722674779248; ALF=1748825965; SUB=_2A25FERo9DeRhGeFH7VUS8ifNzDWIHXVmbxP1rDV8PUJbkNAbLXXxkW1NermJZJ4oG_qYcot386edQQEqXeartDJB; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5gY88XPngQwoKk7GKTwF4N5JpX5KMhUgL.FoM4SoM0eo.pS0.2dJLoI74u9PiNIg4kwJyydJM0eBtt; XSRF-TOKEN=4IduUp1z6lRefdbAuQyhC3RY; WBPSESS=8G8AF24XAkAMrmj4hJ1fCQvT1QD_5RQLPq1djskul-iggxBxpl5AZwMnh13peZyNequrw75T8HrnT0OflTyTplk5PfP9ZCxYZ1BJcD65eYugkVLCh1e4xHaLtlyG3cDtJQhUX3Ors_3-bzKDforO2g=='
    }
    params = {
        'is_new_segment':1,
        'fetch_hot':1
    }
    response = requests.get(url,headers=headers,params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def parse_json(response):
    navList = np.append(response['groups'][3]['group'],response['groups'][4]['group'])
    for nav in navList:
        navName = nav['title']
        gid = nav['gid']
        containerid = nav['containerid']
        wirterRow([
            navName,
            gid,
            containerid,
        ])

if __name__ == '__main__':
    url = 'https://weibo.com/ajax/feed/allGroups'
    init()
    response = get_html(url)
    parse_json(response)