from .base_engine import BaseClickEngine

class SohuClickEngine(BaseClickEngine):
    """
    搜狐平台点击引擎
    """
    
    def __init__(self, config, logger, user_agent_manager, proxy_manager=None, shared_driver=None, url_template=None):
        """
        初始化搜狐点击引擎
        
        Args:
            config (dict): 配置字典
            logger (logging.Logger): 日志记录器
            user_agent_manager (UserAgentManager): User-Agent管理器
            proxy_manager (ProxyManager, optional): 代理管理器，默认为None
            shared_driver (webdriver.Chrome, optional): 共享的浏览器驱动实例
            url_template (str, optional): 从配置文件加载的URL模板
        """
        super().__init__(config, logger, user_agent_manager, proxy_manager, shared_driver, url_template)
        self.platform_name = "sohu"
        # 如果配置文件中没有提供url_template，则使用硬编码的默认值
        if not self.url_template:
            self.url_template = "https://www.sohu.com/a/{article_id}"
    
    def generate_url(self, article_id):
        """
        生成搜狐帖子URL
        
        Args:
            article_id (str): 帖子ID，格式为数字_数字，如"123456789_12345"
            
        Returns:
            str: 完整的搜狐帖子URL
        """
        return self.url_template.format(article_id=article_id)
    
    def click(self, article_id):
        """
        点击搜狐帖子
        
        Args:
            article_id (str): 帖子ID，格式为数字_数字，如"123456789_12345"
            
        Returns:
            bool: 点击是否成功
        """
        try:
            # 生成URL
            url = self.generate_url(article_id)
            self.logger.info(f"Clicking Sohu article: {url}")
            
            # 访问URL
            self.driver.get(url)
            
            # 等待页面加载
            if self._wait_for_page_load():
                # 验证是否成功访问到帖子页面
                if "sohu.com" in self.driver.current_url and article_id.split('_')[0] in self.driver.page_source:
                    self.logger.info(f"Successfully clicked Sohu article: {article_id}")
                    return True
                else:
                    self.logger.warning(f"Failed to access Sohu article content: {article_id}")
                    return False
            else:
                self.logger.warning(f"Failed to load Sohu article: {article_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error clicking Sohu article {article_id}: {e}")
            return False