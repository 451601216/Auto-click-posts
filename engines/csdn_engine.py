from .base_engine import BaseClickEngine
import re

class CSDNClickEngine(BaseClickEngine):
    """
    CSDN平台点击引擎
    """
    
    def __init__(self, config, logger, user_agent_manager, proxy_manager=None, shared_driver=None, url_template=None):
        """
        初始化CSDN点击引擎
        
        Args:
            config (dict): 配置字典
            logger (logging.Logger): 日志记录器
            user_agent_manager (UserAgentManager): User-Agent管理器
            proxy_manager (ProxyManager, optional): 代理管理器，默认为None
            shared_driver (webdriver.Chrome, optional): 共享的浏览器驱动实例
            url_template (str, optional): 从配置文件加载的URL模板
        """
        super().__init__(config, logger, user_agent_manager, proxy_manager, shared_driver, url_template)
        self.platform_name = "csdn"
        # 如果配置文件中没有提供url_template，则使用硬编码的默认值
        if not self.url_template:
            self.url_template = "https://blog.csdn.net/{user_id}/article/details/{article_id}"
    
    def _validate_parameters(self, user_id, article_id):
        """
        验证用户标识和文章ID的格式是否正确
        
        Args:
            user_id (str): 用户标识，格式为数字_数字，如"2501_94652164"
            article_id (str): 文章ID，格式为纯数字，如"155947200"
            
        Returns:
            bool: 参数是否有效
        """
        # 验证用户标识格式
        user_id_pattern = r'^\d+_\d+$'
        if not re.match(user_id_pattern, user_id):
            self.logger.error(f"Invalid CSDN user ID format: {user_id}. Expected format: number_number")
            return False
        
        # 验证文章ID格式
        article_id_pattern = r'^\d+$'
        if not re.match(article_id_pattern, article_id):
            self.logger.error(f"Invalid CSDN article ID format: {article_id}. Expected format: number")
            return False
        
        return True
    
    def generate_url(self, article_info):
        """
        生成CSDN文章URL
        
        Args:
            article_info (dict or str): 文章信息
                - 如果是字典，应包含"user_id"和"article_id"键
                - 如果是字符串，应格式为"user_id:article_id"
            
        Returns:
            str: 完整的CSDN文章URL
        """
        # 解析文章信息
        if isinstance(article_info, dict):
            user_id = article_info.get("user_id")
            article_id = article_info.get("article_id")
        else:
            # 字符串格式："user_id:article_id"
            try:
                user_id, article_id = article_info.split(":")
            except ValueError:
                self.logger.error(f"Invalid CSDN article info format: {article_info}. Expected format: user_id:article_id")
                return None
        
        # 验证参数
        if not self._validate_parameters(user_id, article_id):
            return None
        
        # 生成URL
        return self.url_template.format(user_id=user_id, article_id=article_id)
    
    def click(self, article_info):
        """
        点击CSDN文章
        
        Args:
            article_info (dict or str): 文章信息
                - 如果是字典，应包含"user_id"和"article_id"键
                - 如果是字符串，应格式为"user_id:article_id"
            
        Returns:
            bool: 点击是否成功
        """
        try:
            # 生成URL
            url = self.generate_url(article_info)
            if not url:
                return False
            
            self.logger.info(f"Clicking CSDN article: {url}")
            
            # 访问URL
            self.driver.get(url)
            
            # 等待页面加载
            if self._wait_for_page_load():
                # 验证是否成功访问到帖子页面
                if "csdn.net" in self.driver.current_url:
                    # 获取文章ID
                    if isinstance(article_info, dict):
                        article_id = article_info.get("article_id")
                    else:
                        article_id = article_info.split(":")[1]
                        
                    if article_id in self.driver.current_url:
                        self.logger.info(f"Successfully clicked CSDN article: {article_id}")
                        return True
                    else:
                        self.logger.warning(f"Failed to access CSDN article content: {article_id}")
                        return False
                else:
                    self.logger.warning(f"Redirected away from CSDN while accessing article: {article_id}")
                    return False
            else:
                self.logger.warning(f"Failed to load CSDN article: {article_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error clicking CSDN article {article_info}: {e}")
            return False