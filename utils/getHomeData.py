from utils import getPublicData
from utils.cache import cache_result
from datetime import datetime
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import numpy as np
import jieba
import os
import time

@cache_result(timeout=300)  # 缓存5分钟
def getHomeTopLikeCommentsData():
    """获取点赞最多的评论 - 优化版"""
    try:
        # 使用DataFrame直接处理，性能更好
        df = getPublicData.getCommentsDataFrame()
        if not df.empty:
            # 按点赞数排序并取前4条
            top_comments = df.nlargest(4, 'like_counts')
            return top_comments.values.tolist()
        else:
            # 降级到原始方法
            commentsList = getPublicData.getAllCommentsData()
            commentsListSorted = list(sorted(commentsList, key=lambda x: int(x[2]), reverse=True))[:4]
            return commentsListSorted
    except Exception as e:
        print(f"获取热门评论失败: {e}")
        return []

@cache_result(timeout=600)  # 缓存10分钟
def getTagData():
    """获取标签数据 - 优化版"""
    try:
        df = getPublicData.getArticleDataFrame()
        if df.empty:
            return 0, '', ''
        
        # 使用pandas操作，性能更好
        max_like_article = df.loc[df['likeNum'].idxmax()]
        maxLikeNum = max_like_article['likeNum']
        maxLikeAuthorName = max_like_article['authorName']
        
        # 统计城市分布（排除'无'）
        city_counts = df[df['region'] != '无']['region'].value_counts()
        maxCity = city_counts.index[0] if not city_counts.empty else ''
        
        return len(df), maxLikeAuthorName, maxCity
    except Exception as e:
        print(f"获取标签数据失败: {e}")
        # 降级到原始方法
        articleData = getPublicData.getAllData()
        maxLikeNum = 0
        maxLikeAuthorName = ''
        cityDic = {}
        for article in articleData:
            if int(article[1]) > maxLikeNum:
                maxLikeNum = int(article[1])
                maxLikeAuthorName = article[11]
            if article[4] == '无':
                continue
            if cityDic.get(article[4], -1) == -1:
                cityDic[article[4]] = 1
            else:
                cityDic[article[4]] += 1
        maxCity = list(sorted(cityDic.items(), key=lambda x: x[1], reverse=True))[0][0] if cityDic else ''
        return len(articleData), maxLikeAuthorName, maxCity

@cache_result(timeout=600)  # 缓存10分钟
def getCreatedNumEchartsData():
    """获取创建数量图表数据 - 优化版"""
    try:
        df = getPublicData.getArticleDataFrame()
        if df.empty:
            return [], []
        
        # 使用pandas groupby，性能更好
        date_counts = df.groupby('created_at').size().reset_index(name='count')
        date_counts = date_counts.sort_values('created_at', ascending=False)
        
        xData = date_counts['created_at'].tolist()
        yData = date_counts['count'].tolist()
        
        return xData, yData
    except Exception as e:
        print(f"获取时间数据失败: {e}")
        # 降级到原始方法
        articleData = getPublicData.getAllData()
        xData = list(set([x[7] for x in articleData]))
        xData = list(sorted(xData, key=lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp(), reverse=True))
        yData = [0 for x in range(len(xData))]
        for i in articleData:
            for index, j in enumerate(xData):
                if i[7] == j:
                    yData[index] += 1
        return xData, yData

@cache_result(timeout=600)  # 缓存10分钟
def getTypeCharData():
    """获取类型图表数据 - 优化版"""
    try:
        df = getPublicData.getArticleDataFrame()
        if df.empty:
            return []
        
        # 使用pandas value_counts，性能更好
        type_counts = df['type'].value_counts()
        resultData = [{'name': name, 'value': count} for name, count in type_counts.items()]
        return resultData
    except Exception as e:
        print(f"获取类型数据失败: {e}")
        # 降级到原始方法
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

@cache_result(timeout=300)  # 缓存5分钟
def getCommentsUserCratedNumEchartsData():
    """获取评论用户创建数量图表数据 - 优化版"""
    try:
        df = getPublicData.getCommentsDataFrame()
        if df.empty:
            return []
        
        # 使用pandas value_counts，性能更好
        date_counts = df['created_at'].value_counts()
        resultData = [{'name': name, 'value': count} for name, count in date_counts.items()]
        return resultData
    except Exception as e:
        print(f"获取评论时间数据失败: {e}")
        # 降级到原始方法
        userData = getPublicData.getAllCommentsData()
        createdDic = {}
        for i in userData:
            if createdDic.get(i[1], -1) == -1:
                createdDic[i[1]] = 1
            else:
                createdDic[i[1]] += 1
        resultData = []
        for key, value in createdDic.items():
            resultData.append({
                'name': key,
                'value': value,
            })
        return resultData

def stopwordslist():
    """获取停用词列表"""
    try:
        stopwords_path = './model/stopWords.txt'
        if os.path.exists(stopwords_path):
            stopwords = [line.strip() for line in open(stopwords_path, encoding='UTF-8').readlines()]
            return stopwords
        else:
            print(f"停用词文件不存在: {stopwords_path}")
            return []
    except Exception as e:
        print(f"读取停用词文件失败: {e}")
        return []

@cache_result(timeout=1800, use_file_cache=True)  # 缓存30分钟，词云生成较耗时
def getUserNameWordCloud():
    """生成用户名词云 - 优化版"""
    try:
        # 检查是否已有词云文件且较新
        output_path = './static/authorNameCloud.jpg'
        if os.path.exists(output_path):
            # 如果文件存在且在30分钟内，直接返回
            if time.time() - os.path.getmtime(output_path) < 1800:  # 30分钟
                return output_path
        
        text = ''
        stopwords = stopwordslist()
        
        # 使用优化的数据获取
        df = getPublicData.getCommentsDataFrame()
        if not df.empty:
            # 直接处理DataFrame，性能更好
            text = ' '.join(df['authorName'].dropna().astype(str))
        else:
            # 降级到原始方法
            commentsList = getPublicData.getAllCommentsData()
            for comment in commentsList:
                text += str(comment[5])
        
        if not text.strip():
            print("没有找到用户名数据")
            return None
        
        # 分词处理
        cut = jieba.cut(text)
        newCut = []
        for word in cut:
            if word not in stopwords and len(word.strip()) > 1:  # 过滤单字符
                newCut.append(word)
        
        if not newCut:
            print("分词后没有有效词汇")
            return None
        
        string = ' '.join(newCut)
        
        # 生成词云
        wc = WordCloud(
            width=1000, height=600,
            background_color='white',
            colormap='Blues',
            font_path='STHUPO.TTF',
            max_words=100,  # 限制词汇数量提升性能
            relative_scaling=0.5
        )
        wc.generate_from_text(string)
        
        # 绘制图片
        plt.figure(figsize=(10, 6))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        
        # 保存到文件
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()  # 释放内存
        
        print(f"词云已生成: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"生成词云失败: {e}")
        return None