from fake_useragent import UserAgent
import random

class UserAgentManager:
    """
    User-Agent管理器，用于生成随机User-Agent
    """
    
    def __init__(self):
        """
        初始化User-Agent管理器
        """
        self.ua = UserAgent()
        # 预定义一些常见的浏览器类型
        self.browser_types = ['chrome', 'firefox', 'safari', 'edge']
    
    def get_random_ua(self):
        """
        获取随机User-Agent
        
        Returns:
            str: 随机生成的User-Agent
        """
        try:
            # 随机选择浏览器类型
            browser = random.choice(self.browser_types)
            return getattr(self.ua, browser)
        except Exception as e:
            #  fallback to a default User-Agent if fake_useragent fails
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    def get_ua_for_platform(self, platform):
        """
        获取适合特定平台的User-Agent
        
        Args:
            platform (str): 平台名称
            
        Returns:
            str: 适合该平台的随机User-Agent
        """
        # 这里可以根据不同平台返回更适合的User-Agent
        # 目前简单实现，直接返回随机User-Agent
        return self.get_random_ua()