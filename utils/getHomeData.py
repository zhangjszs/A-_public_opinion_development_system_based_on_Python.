from utils import getPublicData
from datetime import datetime
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import numpy as np
import jieba

def getHomeTopLikeCommentsData():
    commentsList = getPublicData.getAllCommentsData()
    commentsListSorted = list(sorted(commentsList,key=lambda x:int(x[2]),reverse=True))[:4]
    return commentsListSorted

def getTagData():
    articleData = getPublicData.getAllData()
    maxLikeNum = 0
    maxLikeAuthorName = ''
    cityDic = {}
    for article in articleData:
        if int(article[1]) > maxLikeNum:
            maxLikeNum = int(article[1])
            maxLikeAuthorName = article[11]
        if article[4] == '无':continue
        if cityDic.get(article[4],-1) == -1:
            cityDic[article[4]] = 1
        else:
            cityDic[article[4]] += 1
    maxCity = list(sorted(cityDic.items(),key=lambda x:x[1],reverse=True))[0][0]


    return len(articleData),maxLikeAuthorName,maxCity

def getCreatedNumEchartsData():
    articleData = getPublicData.getAllData()
    xData = list(set([x[7] for x in articleData]))
    xData = list(sorted(xData,key=lambda x:datetime.strptime(x,'%Y-%m-%d').timestamp(),reverse=True))
    yData = [0 for x in range(len(xData))]
    for i in articleData:
        for index,j in enumerate(xData):
            if i[7] == j:
                yData[index] += 1

    return xData,yData

def getTypeCharData():
    allData = getPublicData.getAllData()
    typeDic = {}
    for i in allData:
        if typeDic.get(i[8], -1) == -1:
            typeDic[i[8]] = 1
        else:
            typeDic[i[8]] += 1
    resultData = []
    for key, value in typeDic.items():
        resultData.append({
            'name': key,
            'value': value,
        })
    return resultData

def getCommentsUserCratedNumEchartsData():
    userData = getPublicData.getAllCommentsData()
    createdDic = {}
    for i in userData:
        if createdDic.get(i[1],-1) == -1:
            createdDic[i[1]] =1
        else:
            createdDic[i[1]] +=1
    resultData = []
    for key,value in createdDic.items():
        resultData.append({
            'name':key,
            'value':value,
        })
    return resultData

def stopwordslist():
    stopwords = [line.strip() for line in open('./model/stopWords.txt',encoding='UTF-8').readlines()]
    return stopwords

def getUserNameWordCloud():
    text = ''
    stopwords = stopwordslist()
    commentsList = getPublicData.getAllCommentsData()
    for comment in commentsList:
        text += comment[5]
    cut = jieba.cut(text)
    newCut = []
    for word in cut:
        if word not in stopwords:newCut.append(word)
    string = ' '.join(newCut)
    wc = WordCloud(
        width=1000, height=600,
        background_color='white',
        colormap='Blues',
        font_path='STHUPO.TTF'
    )
    wc.generate_from_text(string)

    # 绘制图片
    fig = plt.figure(1)
    plt.imshow(wc)
    plt.axis('off')  # 不显示坐标轴

    # 显示生成的词语图片
    # plt.show()

    # 输入词语图片到文件

    plt.savefig('./static/authorNameCloud.jpg', dpi=500)