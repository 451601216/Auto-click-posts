from .base_engine import BaseClickEngine
from urllib.parse import urlparse
import os
import json

class GenericClickEngine(BaseClickEngine):
    """
    通用点击引擎，直接使用配置的articles作为完整URL进行点击
    """
    
    def __init__(self, config, logger, user_agent_manager, proxy_manager=None, shared_driver=None, url_template=None):
        """
        初始化通用点击引擎
        
        Args:
            config (dict): 配置字典
            logger (logging.Logger): 日志记录器
            user_agent_manager (UserAgentManager): User-Agent管理器
            proxy_manager (ProxyManager, optional): 代理管理器，默认为None
            shared_driver (webdriver.Chrome, optional): 共享的浏览器驱动实例
            url_template (str, optional): 从配置文件加载的URL模板（通用引擎不使用）
        """
        super().__init__(config, logger, user_agent_manager, proxy_manager, shared_driver, url_template)
        self.platform_name = "generic"
        # 通用引擎不使用URL模板，直接使用完整URL
        self.url_template = None
        
        # 加载平台配置
        self.platforms = self._load_platforms_config()
    
    def _validate_parameters(self, url):
        """
        验证URL格式是否正确
        
        Args:
            url (str): 完整的URL字符串
            
        Returns:
            bool: URL是否有效
        """
        # 简单验证URL格式，检查是否以http://或https://开头
        if not url.startswith(('http://', 'https://')):
            self.logger.warning(f"Invalid URL for generic engine: {url}. Must start with http:// or https://")
            return False
            
        return True
    
    def generate_url(self, article_id):
        """
        生成URL - 对于通用引擎，直接返回article_id作为URL
        
        Args:
            article_id (str): 完整的URL字符串
            
        Returns:
            str: 完整的URL
        """
        # 验证URL格式
        if self._validate_parameters(article_id):
            return article_id
        else:
            return None
    
    def _load_platforms_config(self):
        """
        加载平台配置文件
        
        Returns:
            list: 平台配置列表
        """
        platforms_config_path = os.path.join(os.path.dirname(__file__), '../config/platforms.json')
        try:
            with open(platforms_config_path, 'r', encoding='utf-8') as f:
                platforms_data = json.load(f)
                return platforms_data.get('platforms', [])
        except Exception as e:
            self.logger.error(f"Failed to load platforms config: {e}")
            return []
    
    def _detect_platform(self, url):
        """
        根据URL检测平台
        
        Args:
            url (str): 完整的URL字符串
            
        Returns:
            dict or None: 匹配的平台配置，如果没有匹配则返回None
        """
        try:
            parsed_url = urlparse(url)
            netloc = parsed_url.netloc.lower()
            
            # 遍历所有平台，查找匹配的域名
            for platform in self.platforms:
                domain = platform.get('domain', '').lower()
                if domain and domain in netloc:
                    return platform
            
            return None
        except Exception as e:
            self.logger.error(f"Error detecting platform for URL {url}: {e}")
            return None
    
    def click(self, url):
        """
        点击URL - 对于通用引擎，直接访问完整URL，并根据URL自动检测平台设置User-Agent
        
        Args:
            url (str): 完整的URL字符串
            
        Returns:
            bool: 点击是否成功
        """
        try:
            # 验证URL格式
            if not self._validate_parameters(url):
                return False
                
            self.logger.info(f"Clicking URL: {url}")
            
            # 根据URL检测平台
            platform = self._detect_platform(url)
            if platform:
                self.platform_name = platform['name']
                self.logger.info(f"Detected platform: {self.platform_name} for URL: {url}")
                # 设置检测到的平台对应的User-Agent
                self.user_agent = self.user_agent_manager.get_ua_for_platform(self.platform_name)
                self.logger.info(f"Set User-Agent for {self.platform_name}: {self.user_agent}")
                # 更新浏览器的User-Agent
                if hasattr(self.driver, 'execute_cdp_cmd'):
                    self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                        "userAgent": self.user_agent
                    })
            
            # 访问URL
            self.driver.get(url)
            
            # 等待页面加载
            if self._wait_for_page_load():
                self.logger.info(f"Successfully clicked URL: {url}")
                return True
            else:
                self.logger.warning(f"Failed to load URL: {url}")
                return False
        except Exception as e:
            self.logger.error(f"Error clicking URL {url}: {e}")
            return False