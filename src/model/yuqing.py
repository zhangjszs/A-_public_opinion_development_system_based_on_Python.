import csv
import os

from ciPingTotal import main as ciPingTotalMain
from index import getCommentList
from index import main as indexMain
from snownlp import SnowNLP


def targetFile():
    targetFile = 'target.csv'
    commentList = getCommentList()

    rateData = []
    good = 0
    bad = 0
    midlle = 0
    for index, i in enumerate(commentList):
        try:
            value = SnowNLP(i[4]).sentiments
            if value > 0.5:
                good += 1
                rateData.append([i[4], '正面'])
            elif value == 0.5:
                midlle += 1
                rateData.append([i[4], '中性'])
            elif value < 0.5:
                bad += 1
                rateData.append([i[4], '负面'])
        except Exception:
            continue
        with open(targetFile, 'a+', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(i)

def main():
    try:
        os.remove('./target.csv')
        os.remove("./comment_1_fenci.txt")
        os.remove("./comment_1_fenci_qutingyongci_cipin.csv")
    except Exception:
        pass
    ciPingTotalMain()
    targetFile()


if __name__ == '__main__':
    main()


# 总结:
#
# 这个脚本是一个数据处理流水线 (pipeline) 的主控制器：
#
# 清理环境: 删除之前运行可能产生的三个输出文件 (target.csv, comment_1_fenci.txt, comment_1_fenci_qutingyongci_cipin.csv)。
# 执行依赖任务: 运行 index.py 和 ciPingTotal.py 中的主函数 (indexMain, ciPingTotalMain)，推测这些是数据获取、预处理或词频分析等步骤。
# 情感分析: 调用 getCommentList (来自 index 模块) 获取评论数据。
# 分类与保存: 使用 SnowNLP 对每条评论进行情感打分，将其分类为 '正面'、'中性' 或 '负面'。
# 输出结果: 将原始评论文本和对应的情感标签逐行追加写入 target.csv 文件。
# 总的来说，这个脚本整合了多个模块的功能，最终目标是生成一个包含评论及其情感分类的 CSV 文件 (target.csv)。它依赖于 index.py 和 ciPingTotal.py 两个外部模块来完成部分前置工作。