import threading
import time
import random
import logging
import os
from threading import Lock
from spiderContent import start as start_content
from spiderComments import start as start_comments
from spiderUserInfo import start_user_spider

# 全局控制参数
MAX_REQUESTS = 3  # 每个模块最多请求次数
REQUEST_INTERVAL = random.uniform(1.5, 3.0)  # 请求间隔

# 线程控制锁
lock_content = Lock()
lock_comments = Lock() 
lock_user = Lock()

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'weibo_spider.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from main import save_to_sql

class WeiboSpiderController:
    """微博爬虫控制器 - 基于博客多线程优化"""
    
    def __init__(self, delay=2.0):
        self.delay = delay
        self.content_completed = False
        self.comments_completed = False
        self.user_completed = False
        self.search_mode = False
        self.search_keyword = None
        
    def content_spider_thread(self):
        """文章爬取线程"""
        try:
            with lock_content:
                logger.info("开始执行文章爬取任务")
                # 调用文章爬取函数
                if self.search_mode and self.search_keyword:
                    logger.info(f"执行关键词搜索: {self.search_keyword}")
                    start_content(typeNum=1, pageNum=3, mode='search', keyword=self.search_keyword)
                else:
                    logger.info("执行分类爬取")
                    start_content(typeNum=2, pageNum=3, mode='category')
                
                self.content_completed = True
                logger.info("文章爬取任务完成")
                
                # 释放评论爬取锁
                if lock_comments.locked():
                    lock_comments.release()
                    
        except Exception as e:
            logger.error(f"文章爬取线程异常: {e}")
            self.content_completed = True
            if lock_comments.locked():
                lock_comments.release()
    
    # ... comments_spider_thread and user_spider_thread remain same ...
    def comments_spider_thread(self):
        """评论爬取线程 - 等待文章爬取完成后执行"""
        try:
            # 等待文章爬取完成
            while not self.content_completed:
                time.sleep(1)
                
            with lock_comments:
                logger.info("开始执行评论爬取任务")
                # 调用评论爬取函数
                start_comments()
                self.comments_completed = True
                logger.info("评论爬取任务完成")
                
                # 释放用户信息爬取锁
                if lock_user.locked():
                    lock_user.release()
                    
        except Exception as e:
            logger.error(f"评论爬取线程异常: {e}")
            self.comments_completed = True
            if lock_user.locked():
                lock_user.release()
    
    def user_spider_thread(self):
        """用户信息爬取线程 - 等待评论爬取完成后执行"""
        try:
            # 等待评论爬取完成
            while not self.comments_completed:
                time.sleep(1)
                
            with lock_user:
                logger.info("开始执行用户信息爬取任务")
                # 调用用户信息爬取函数
                start_user_spider(max_users=50)  # 爬取50个用户的信息
                self.user_completed = True
                logger.info("用户信息爬取任务完成")
                
        except Exception as e:
            logger.error(f"用户信息爬取线程异常: {e}")
            self.user_completed = True

    def concurrent_spider_mode(self, keyword=None):
        """并发爬取模式 - 根据博客优化的线程控制"""
        logger.info("启动并发爬取模式")
        
        if keyword:
            self.search_mode = True
            self.search_keyword = keyword
        
        # 初始化锁状态 - 让文章爬取先执行
        lock_comments.acquire()
        lock_user.acquire()
        
        # 创建线程
        content_thread = threading.Thread(
            target=self.content_spider_thread, 
            name="ContentSpider"
        )
        comments_thread = threading.Thread(
            target=self.comments_spider_thread, 
            name="CommentsSpider"
        )
        user_thread = threading.Thread(
            target=self.user_spider_thread, 
            name="UserSpider"
        )
        
        # 启动线程
        content_thread.start()
        time.sleep(2)  # 给文章爬取一点启动时间
        
        comments_thread.start()
        time.sleep(1)  # 给评论爬取一点启动时间
        
        user_thread.start()
        
        # 等待所有线程完成
        content_thread.join()
        logger.info("文章爬取线程已结束")
        
        comments_thread.join()
        logger.info("评论爬取线程已结束")
        
        user_thread.join()
        logger.info("用户信息爬取线程已结束")
        
        logger.info("所有爬取任务完成！")
        self._save_data()

    def sequential_spider_mode(self, keyword=None):
        """顺序爬取模式 - 确保数据依赖关系"""
        logger.info("启动顺序爬取模式")
        
        try:
            # 1. 文章爬取
            logger.info("第一阶段：开始爬取文章数据")
            if keyword:
                start_content(typeNum=1, pageNum=3, mode='search', keyword=keyword)
            else:
                start_content(typeNum=2, pageNum=3)
            logger.info("第一阶段：文章爬取完成")
            
            # 延时
            time.sleep(self.delay)
            
            # 2. 评论爬取
            logger.info("第二阶段：开始爬取评论数据")
            start_comments()
            logger.info("第二阶段：评论爬取完成")
            
            # 延时
            time.sleep(self.delay)
            
            # 3. 用户信息爬取
            logger.info("第三阶段：开始爬取用户信息")
            start_user_spider(max_users=50)
            logger.info("第三阶段：用户信息爬取完成")
            
            logger.info("所有爬取任务顺序完成！")
            self._save_data()
            
        except Exception as e:
            logger.error(f"顺序爬取模式异常: {e}")

    def smart_spider_mode(self):
        """智能爬取模式 - 结合并发和顺序的优势"""
        # 暂不实现搜索支持，专注于默认推荐
        logger.info("启动智能爬取模式")
        
        try:
            # 第一阶段：文章爬取
            logger.info("智能模式第一阶段：爬取文章数据")
            start_content(typeNum=2, pageNum=2)
            
            # 第二阶段：并发爬取评论和用户信息
            logger.info("智能模式第二阶段：并发爬取评论和用户信息")
            
            comments_thread = threading.Thread(
                target=start_comments,
                name="CommentsSpiderSmart"
            )
            user_thread = threading.Thread(
                target=lambda: start_user_spider(max_users=30),
                name="UserSpiderSmart"
            )
            
            # 启动并发线程
            comments_thread.start()
            time.sleep(1)  # 错开启动时间
            user_thread.start()
            
            # 等待完成
            comments_thread.join()
            user_thread.join()
            
            logger.info("智能爬取模式完成！")
            self._save_data()
            
        except Exception as e:
            logger.error(f"智能爬取模式异常: {e}")

    def _save_data(self):
        """保存数据到数据库"""
        try:
            logger.info("开始将数据保存到数据库...")
            save_to_sql()
            logger.info("数据入库完成")
        except Exception as e:
            logger.error(f"数据入库失败: {e}")

def main():
    """主函数 - 根据用户选择执行不同的爬取模式"""
    controller = WeiboSpiderController(delay=2.0)
    
    print("=== 微博舆情分析爬虫系统 ===")
    print("基于博客技术优化的多模块爬虫")
    print("1. 顺序爬取模式（推荐-稳定）")
    print("2. 并发爬取模式（高效）") 
    print("3. 智能爬取模式（平衡）")
    print("4. 仅爬取文章")
    print("5. 仅爬取评论")
    print("6. 仅爬取用户信息")
    print("7. 关键词搜索爬取（新功能）")
    
    choice = input("请选择爬取模式 (1-7): ").strip()
    
    if choice == '1':
        controller.sequential_spider_mode()
    elif choice == '2':
        controller.concurrent_spider_mode()
    elif choice == '3':
        controller.smart_spider_mode()
    elif choice == '4':
        logger.info("仅执行文章爬取")
        start_content(typeNum=2, pageNum=3)
        # 仅爬取文章时不强制入库，或询问
    elif choice == '5':
        logger.info("仅执行评论爬取")
        start_comments()
    elif choice == '6':
        logger.info("仅执行用户信息爬取")
        start_user_spider(max_users=50)
    elif choice == '7':
        keyword = input("请输入搜索关键词: ").strip()
        if keyword:
            print(f"开始搜索爬取: {keyword}")
            controller.sequential_spider_mode(keyword=keyword)
        else:
            print("未输入关键词，退出")
    else:
        print("无效选择，默认使用顺序爬取模式")
        controller.sequential_spider_mode()

if __name__ == '__main__':
    main()