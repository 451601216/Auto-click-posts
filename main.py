import json
import os
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from utils import setup_logger, UserAgentManager, ProxyManager
from engines import GenericClickEngine

class AutoClicker:
    """
    自动点击帖子主程序类
    """
    
    def __init__(self, config_path="config/config.json", platforms_path="config/platforms.json", articles_path="config/articles.json"):
        """
        初始化自动点击器
        
        Args:
            config_path (str): 配置文件路径
            platforms_path (str): 平台配置文件路径
            articles_path (str): 文章ID配置文件路径
        """
        # 加载配置文件
        self.config = self._load_config(config_path)
        self.platforms_config = self._load_config(platforms_path)
        self.articles_config = self._load_config(articles_path)
        
        # 初始化日志记录器
        self.logger = setup_logger(
            log_level=self.config.get("logging", {}).get("level", "INFO"),
            log_file=self.config.get("logging", {}).get("log_file")
        )
        
        # 初始化User-Agent管理器
        self.user_agent_manager = UserAgentManager()
        
        # 初始化代理管理器（如果配置了）
        self.proxy_manager = None
        if self.config.get("general", {}).get("use_proxy", False):
            self.proxy_manager = ProxyManager(
                proxy_type=self.config.get("general", {}).get("proxy_type", "http")
            )
            # 这里可以从文件或API加载代理列表
            # 目前仅作为示例，实际使用时需要添加代理IP
        
        # 移除特定平台引擎的初始化，现在使用通用引擎处理所有点击任务
        
        # 统计信息
        self.stats = {
            "total_clicks": 0,
            "successful_clicks": 0,
            "failed_clicks": 0,
            "platform_stats": {}
        }
    
    def _load_config(self, file_path):
        """
        加载配置文件
        
        Args:
            file_path (str): 配置文件路径
            
        Returns:
            dict: 配置字典
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load config file {file_path}: {e}")
    

    
    def run(self, urls=None):
        """
        运行自动点击任务
        
        Args:
            urls (list, optional): 需要点击的URL列表，如果未提供则从配置文件加载
        """
        self.logger.info("Starting auto clicker...")
        
        # 初始化统计信息
        self.stats["url_stats"] = {}
        
        # 如果未提供URL列表，则从配置文件加载
        if urls is None:
            urls = self.articles_config.get("clicks", {}).get("values", [])
        
        total_urls = len(urls)
        if total_urls == 0:
            self.logger.error("No URLs provided for clicking")
            return
        
        self.logger.info(f"Total URLs to click: {total_urls}")
        
        # 创建共享浏览器实例
        shared_driver = None
        browser_lock = threading.Lock()  # 保护对共享浏览器的访问
        
        try:
            # 初始化通用引擎来创建共享浏览器实例
            temp_engine = GenericClickEngine(
                self.config,
                self.logger,
                self.user_agent_manager,
                self.proxy_manager
            )
            temp_engine._setup_browser()
            shared_driver = temp_engine.driver
            self.logger.info("Created shared browser instance")
            
            # 使用线程锁保护统计信息的更新
            stats_lock = threading.Lock()
            click_count = 0
            click_count_lock = threading.Lock()
            
            def execute_click(url):
                """
                执行单个URL点击任务
                
                Args:
                    url (str): 需要点击的完整URL
                """
                nonlocal click_count
                
                # 创建通用引擎实例，复用共享浏览器
                engine = GenericClickEngine(
                    self.config,
                    self.logger,
                    self.user_agent_manager,
                    self.proxy_manager,
                    shared_driver=shared_driver  # 传递共享浏览器实例
                )
                
                try:
                    # 增加点击计数
                    with click_count_lock:
                        click_count += 1
                        current_count = click_count
                    
                    self.logger.info(f"Click {current_count}/{total_urls}: URL={url}")
                    
                    # 执行点击（使用浏览器锁保护）
                    with browser_lock:
                        success = engine.click(url)
                    
                    # 更新统计信息（线程安全）
                    with stats_lock:
                        self.stats["total_clicks"] += 1
                        
                        if success:
                            self.stats["successful_clicks"] += 1
                        else:
                            self.stats["failed_clicks"] += 1
                    
                    return success
                except Exception as e:
                    self.logger.error(f"Click task failed for URL {url}: {str(e)}")
                    with stats_lock:
                        self.stats["total_clicks"] += 1
                        self.stats["failed_clicks"] += 1
                    return False
            
            # 使用线程池执行并行点击
            max_workers = self.config.get("general", {}).get("max_workers", 3)  # 默认最多3个并行线程
            self.logger.info(f"Using {max_workers} threads for parallel clicking with shared browser")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有URL点击任务
                futures = [executor.submit(execute_click, url) for url in urls]
                
                # 等待所有任务完成
                for future in futures:
                    try:
                        future.result()  # 获取任务结果，会抛出异常如果任务失败
                    except Exception as e:
                        self.logger.error(f"Click task failed: {str(e)}")
        finally:
            # 关闭共享浏览器实例
            if shared_driver:
                self.logger.info("开始关闭共享浏览器实例")
                try:
                    shared_driver.quit()
                    self.logger.info("已成功关闭共享浏览器实例")
                except Exception as e:
                    self.logger.error(f"关闭共享浏览器实例时发生错误: {str(e)}")
        
        # 生成报告
        self._generate_report()
    
    def _generate_report(self):
        """
        生成点击报告
        """
        self.logger.info("==================== Click Report ====================")
        self.logger.info(f"Total clicks: {self.stats['total_clicks']}")
        self.logger.info(f"Successful clicks: {self.stats['successful_clicks']}")
        self.logger.info(f"Failed clicks: {self.stats['failed_clicks']}")
        self.logger.info(f"Success rate: {self.stats['successful_clicks']/self.stats['total_clicks']*100:.2f}%" if self.stats['total_clicks'] > 0 else "Success rate: 0%")
        
        self.logger.info("\nPlatform-wise stats:")
        for platform, stats in self.stats['platform_stats'].items():
            if stats['total'] > 0:
                success_rate = stats['successful']/stats['total']*100
            else:
                success_rate = 0
            self.logger.info(f"  {platform}: Total={stats['total']}, Successful={stats['successful']}, Failed={stats['failed']}, Success rate={success_rate:.2f}%")
        
        self.logger.info("======================================================")

def main():
    """主函数"""
    try:
        auto_clicker = AutoClicker()
        
        # 获取要点击的URL列表
        urls = auto_clicker.articles_config.get("clicks", {}).get("values", [])
        if not urls:
            auto_clicker.logger.warning("No URLs to click, exiting.")
            return
        
        auto_clicker.logger.info(f"Starting to click URLs: {len(urls)} total URLs")
        auto_clicker.run(urls)
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()