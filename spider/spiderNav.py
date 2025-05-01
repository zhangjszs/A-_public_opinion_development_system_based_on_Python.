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
        'Cookie': 'SINAGLOBAL=7212852614896.057.1722674779243; SCF=AuBnnYbv5UcU0Em9mzgayCIUin7u9gaSXe7Ioo3XKiTjesfDU7n5afCo3g09azYPzLTX9x6dK2qs4urCz3KBY5I.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5gY88XPngQwoKk7GKTwF4N5JpX5KzhUgL.FoM4SoM0eo.pS0.2dJLoI74u9PiNIg4kwJyydJM0eBtt; ULV=1745148345761:2:1:1:8580936394154.282.1745148345707:1722674779248; SUB=_2A25FAK7cDeRhGeFH7VUS8ifNzDWIHXVmf64UrDV8PUNbmtAYLWbAkW1NermJZDytnabRK03Lq9P5cWrT1OLtFZXJ; ALF=02_1747741580'
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