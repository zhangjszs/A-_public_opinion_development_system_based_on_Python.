from .getPublicData import getAllCommentsData, getAllData

allData = getAllData()
commentList = getAllCommentsData()
#
# def getHomeData():
#     allCiPingTotal = getAllCiPingTotal()
#     typeDic = {}
#     for i in allData:
#         if typeDic.get(i[8],-1) == -1:
#             typeDic[i[8]] = 1
#         else:
#             typeDic[i[8]] += 1
#     data = []
#     for key,value in typeDic.items():
#         data.append({
#             'name':key,
#             'value':value
#         })
#     xData = []
#     yData = []
#     for i in allCiPingTotal:
#         xData.append(i[0])
#         yData.append(int(i[1]))
#     return data,xData[:10],yData[:10],commentList[:30]
#
# def getTableData(defaultHotSearch):
#     allCiPingTotal = getAllCiPingTotal()
#     resultData = []
#     for i in allData:
#         for j in i[-1]:
#             if j[4].find(defaultHotSearch) != -1:
#                 resultData.append(i)
#     tempDataId = list(set([x[0] for x in resultData]))
#     lastResultData = []
#     for id in tempDataId:
#         for j in allData:
#             if id == j[0]:
#                 lastResultData.append(j)
#
#     return allCiPingTotal,lastResultData
#
# def getTotalHotSearchWordNum(defaultHotSearch):
#     allCiPingTotal = getAllCiPingTotal()
#     num = 0
#     for i in allCiPingTotal:
#         if i[0] == defaultHotSearch:
#             num = int(i[1])
#     xData = []
#     for i in allCiPingTotal:
#         for j in allData:
#             for k in j[-1]:
#                 if k[4].find(i[1]) != -1:
#                     xData.append(k[-2])
#     xData = list(set(xData))
#     yData = [0 for x in range(len(xData))]
#     for index,x in enumerate(xData):
#         for c in commentList:
#             if c[-2] == x:
#                 yData[index] += 1
#
#
#     return num,xData,yData
#
# def gethotWordCharData():
#     allCiPingTotal = getAllCiPingTotal()
#     barData = []
#     for i in allCiPingTotal:
#         barData.append({
#             'name':i[0],
#             'value':int(i[1])
#         })
#     xData = []
#     yData = []
#     for i in allCiPingTotal:
#         xData.append(i[0])
#         yData.append(int(i[1]))
#
#     return barData[:10],xData[:10],yData[:10]
#
# def comefromCharData():
#     comefromDic = {}
#     for i in allData:
#         if comefromDic.get(i[1],-1) == -1:
#             comefromDic[i[1]] = 1
#         else:
#             comefromDic[i[1]] += 1
#     resData = []
#     xData = []
#     yData = []
#     for key,value in comefromDic.items():
#         xData.append(key)
#         yData.append(value)
#         resData.append({
#             'name':key,
#             'value':value
#         })
#     resData[0]['name'] = '清华大学'
#     resData[1]['name'] = '南阳大学'
#     resData[2]['name'] = '北京大学'
#     xData = ['清华大学','南阳大学','北京大学']
#     return resData,xData,yData
#
# def getYuQingCharData():
#     xData = ['消极','积极']
#     yData = [0,0]
#
#     y1Data = [0,0]
#     y2Data = [0,0]
#     y3Data = [0,0]
#     for i in commentList:
#         try:
#             if SnowNLP(i[2]).sentiments < 0.5:
#                 yData[0] += 1
#                 if i[-1] == '知乎':
#                     y1Data[0] += 1
#                 elif i[-1] == '微博':
#                     y2Data[0] += 1
#                 else:
#                     y3Data[0] += 1
#             else:
#                 yData[1] += 1
#                 if i[-1] == '知乎':
#                     y1Data[1] += 1
#                 elif i[-1] == '微博':
#                     y2Data[1] += 1
#                 else:
#                     y3Data[1] += 1
#         except:
#             pass
#     treeData = [{
#         'name':"消极",
#         'value':yData[0]
#     },{
#         'name':"积极",
#         'value':yData[1]
#     }]
#
#     barData = [{
#         'name': "清华大学",
#         'value': y1Data[0]
#     }, {
#         'name': "南阳大学",
#         'value': y2Data[0]
#     },{
#         'name':"北京大学",
#         'value':y3Data[0]
#     }]
#
#     barData1 = [{
#         'name': "清华大学",
#         'value': y1Data[1]
#     }, {
#         'name': "南阳大学",
#         'value': y2Data[1]
#     }, {
#         'name': "北京大学",
#         'value': y3Data[1]
#     }]
#
#     return xData,yData,y1Data,y2Data,y3Data,treeData,barData,barData1
#
