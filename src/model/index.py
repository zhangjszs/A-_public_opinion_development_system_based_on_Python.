import jieba
import jieba.analyse as analyse

from utils.getPublicData import getAllCommentsData

targetTxt = 'comment_1_fenci.txt'

def stopwordslist():
    stopwords = [line.strip() for line in open('./stopWords.txt',encoding='UTF-8').readlines()]
    return stopwords

def getCommentList():
    return getAllCommentsData()

def seg_depart(sentence):
    sentence_depart = jieba.cut(" ".join([x[4] for x in sentence]).strip())
    stopwords = stopwordslist()
    outstr = ''
    # 去停用词
    for word in sentence_depart:
        if word not in stopwords:
            if word != '\t':
                outstr += word
    return outstr

def writer_comment_fenci():
    with open(targetTxt, 'a+', encoding='utf-8') as targetFile:
        seg = jieba.cut(seg_depart(getCommentList()), cut_all=False)
        # 分好词之后之间用空格隔断
        output = ' '.join(seg)
        targetFile.write(output)
        targetFile.write('\n')
        print('写入成功！')

# 提取关键词
def main():
    writer_comment_fenci()

if __name__ == '__main__':
    main()

# 总结:
#
# 该脚本执行一次完整的流程如下：
#
# 从 utils.getPublicData.getAllCommentsData 获取一批评论数据。
# 提取每条评论的文本（假设在数据的第5个位置）。
# 将所有评论文本合并，进行初步分词，并移除 stopWords.txt 文件中定义的停用词和制表符。
# 将过滤后的词语连接成一个没有分隔符的长字符串。
# 对这个长字符串进行第二次精确模式分词。
# 将第二次分词的结果用空格连接。
# 将这个最终的、用空格分隔的词语字符串，作为新的一行追加写入到 comment_1_fenci.txt 文件中。
# 在控制台输出 "写入成功！"。