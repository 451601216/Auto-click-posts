from .base_engine import BaseClickEngine

class NeteaseClickEngine(BaseClickEngine):
    """
    网易平台点击引擎
    """
    
    def __init__(self, config, logger, user_agent_manager, proxy_manager=None, shared_driver=None, url_template=None):
        """
        初始化网易点击引擎
        
        Args:
            config (dict): 配置字典
            logger (logging.Logger): 日志记录器
            user_agent_manager (UserAgentManager): User-Agent管理器
            proxy_manager (ProxyManager, optional): 代理管理器，默认为None
            shared_driver (webdriver.Chrome, optional): 共享的浏览器驱动实例
            url_template (str, optional): 从配置文件加载的URL模板
        """
        super().__init__(config, logger, user_agent_manager, proxy_manager, shared_driver, url_template)
        self.platform_name = "netease"
        # 如果配置文件中没有提供url_template，则使用硬编码的默认值
        if not self.url_template:
            self.url_template = "https://www.163.com/dy/article/{article_id}.html"
    
    def generate_url(self, article_id):
        """
        生成网易帖子URL
        
        Args:
            article_id (str): 帖子ID，格式为字母数字组合，如"H1234567890ABCDEF"
            
        Returns:
            str: 完整的网易帖子URL
        """
        return self.url_template.format(article_id=article_id)
    
    def click(self, article_id):
        """
        点击网易帖子
        
        Args:
            article_id (str): 帖子ID，格式为字母数字组合，如"H1234567890ABCDEF"
            
        Returns:
            bool: 点击是否成功
        """
        try:
            # 生成URL
            url = self.generate_url(article_id)
            self.logger.info(f"Clicking Netease article: {url}")
            
            # 访问URL
            self.driver.get(url)
            
            # 等待页面加载
            if self._wait_for_page_load():
                # 验证是否成功访问到帖子页面
                if article_id in self.driver.page_source:
                    self.logger.info(f"Successfully clicked Netease article: {article_id}")
                    return True
                else:
                    # 检查是否被重定向到网易主页
                    if "163.com" in self.driver.current_url and "www.163.com" == self.driver.current_url:
                        self.logger.warning(f"Redirected to Netease homepage, article may not exist: {article_id}")
                    else:
                        self.logger.warning(f"Failed to access Netease article content: {article_id}")
                    return False
            else:
                self.logger.warning(f"Failed to load Netease article: {article_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error clicking Netease article {article_id}: {e}")
            return False