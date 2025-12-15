from .base_engine import BaseClickEngine

class XueqiuClickEngine(BaseClickEngine):
    """
    雪球网平台点击引擎
    """
    
    def __init__(self, config, logger, user_agent_manager, proxy_manager=None, shared_driver=None, url_template=None):
        """
        初始化雪球网点击引擎
        
        Args:
            config (dict): 配置字典
            logger (logging.Logger): 日志记录器
            user_agent_manager (UserAgentManager): User-Agent管理器
            proxy_manager (ProxyManager, optional): 代理管理器，默认为None
            shared_driver (webdriver.Chrome, optional): 共享的浏览器驱动实例
            url_template (str, optional): 从配置文件加载的URL模板
        """
        super().__init__(config, logger, user_agent_manager, proxy_manager, shared_driver, url_template)
        self.platform_name = "xueqiu"
        # 如果配置文件中没有提供url_template，则使用硬编码的默认值
        if not self.url_template:
            self.url_template = "https://xueqiu.com/{user_id}/{article_id}"
    
    def _validate_parameters(self, user_id, article_id):
        """
        验证雪球网文章的用户标识和文章ID格式是否正确
        
        Args:
            user_id (str): 用户标识，应该是数字字符串
            article_id (str): 文章ID，应该是数字字符串
            
        Returns:
            bool: 参数是否有效
        """
        # 验证用户标识是否为数字字符串
        if not user_id.isdigit():
            self.logger.warning(f"Invalid user_id for xueqiu article: {user_id}. Must be a numeric string.")
            return False
        
        # 验证文章ID是否为数字字符串
        if not article_id.isdigit():
            self.logger.warning(f"Invalid article_id for xueqiu article: {article_id}. Must be a numeric string.")
            return False
            
        return True
    
    def generate_url(self, article_id):
        """
        生成雪球网文章URL
        
        Args:
            article_id (str): 文章ID，格式为"user_id:article_id"，例如"6484614528:366086769"
            
        Returns:
            str: 完整的雪球网文章URL
        """
        try:
            # 解析user_id和article_id
            user_id, article_id = article_id.split(":")
            
            # 验证参数格式
            if self._validate_parameters(user_id, article_id):
                return self.url_template.format(user_id=user_id, article_id=article_id)
            else:
                return None
        except ValueError:
            self.logger.warning(f"Invalid xueqiu article ID format: {article_id}. Expected format: user_id:article_id")
            return None
    
    def click(self, article_id):
        """
        点击雪球网文章
        
        Args:
            article_id (str): 文章ID，格式为"user_id:article_id"，例如"6484614528:366086769"
            
        Returns:
            bool: 点击是否成功
        """
        try:
            # 生成URL
            url = self.generate_url(article_id)
            if not url:
                return False
                
            self.logger.info(f"Clicking xueqiu article: {url}")
            
            # 访问URL
            self.driver.get(url)
            
            # 等待页面加载
            if self._wait_for_page_load():
                # 解析user_id和article_id
                user_id, article_id_num = article_id.split(":")
                
                # 验证是否成功访问到文章页面，检查当前URL是否包含预期的user_id和article_id
                current_url = self.driver.current_url
                if user_id in current_url and article_id_num in current_url:
                    self.logger.info(f"Successfully clicked xueqiu article: {article_id}")
                    return True
                else:
                    # 检查是否被重定向到雪球网主页
                    if "xueqiu.com" in current_url:
                        if "index" in current_url or "home" in current_url:
                            self.logger.warning(f"Redirected to xueqiu homepage, article may not exist: {article_id}")
                        else:
                            self.logger.warning(f"Successfully loaded xueqiu page but URL doesn't match expected pattern: {current_url}")
                            # 即使URL不匹配，页面可能已经加载成功，我们仍然认为点击成功
                            return True
                    else:
                        self.logger.warning(f"Redirected to unexpected URL: {current_url}")
                    return False
            else:
                self.logger.warning(f"Failed to load xueqiu article: {article_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error clicking xueqiu article {article_id}: {e}")
            return False