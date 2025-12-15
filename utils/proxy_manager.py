import requests
import random
import time

class ProxyManager:
    """
    代理管理器，用于管理和验证代理IP
    """
    
    def __init__(self, proxy_type="http"):
        """
        初始化代理管理器
        
        Args:
            proxy_type (str): 代理类型，默认http
        """
        self.proxy_type = proxy_type
        self.proxies = []
        self.valid_proxies = []
        self.current_proxy = None
    
    def add_proxy(self, proxy):
        """
        添加代理IP
        
        Args:
            proxy (str): 代理IP，格式为ip:port
        """
        self.proxies.append(proxy)
    
    def add_proxies(self, proxies):
        """
        批量添加代理IP
        
        Args:
            proxies (list): 代理IP列表，每个元素格式为ip:port
        """
        self.proxies.extend(proxies)
    
    def validate_proxy(self, proxy, timeout=5):
        """
        验证代理IP是否有效
        
        Args:
            proxy (str): 代理IP，格式为ip:port
            timeout (int): 超时时间，默认5秒
            
        Returns:
            bool: 代理是否有效
        """
        try:
            proxies = {
                self.proxy_type: f"{self.proxy_type}://{proxy}"
            }
            response = requests.get(
                "http://www.baidu.com",
                proxies=proxies,
                timeout=timeout
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def validate_all_proxies(self):
        """
        验证所有代理IP
        """
        self.valid_proxies = []
        for proxy in self.proxies:
            if self.validate_proxy(proxy):
                self.valid_proxies.append(proxy)
    
    def get_random_proxy(self):
        """
        获取随机代理IP
        
        Returns:
            str: 随机代理IP，格式为ip:port
        """
        if not self.valid_proxies:
            self.validate_all_proxies()
        
        if self.valid_proxies:
            self.current_proxy = random.choice(self.valid_proxies)
            return self.current_proxy
        return None
    
    def get_next_proxy(self):
        """
        获取下一个代理IP
        
        Returns:
            str: 下一个代理IP，格式为ip:port
        """
        if not self.valid_proxies:
            self.validate_all_proxies()
        
        if self.valid_proxies:
            if self.current_proxy in self.valid_proxies:
                current_index = self.valid_proxies.index(self.current_proxy)
                next_index = (current_index + 1) % len(self.valid_proxies)
                self.current_proxy = self.valid_proxies[next_index]
            else:
                self.current_proxy = self.valid_proxies[0]
            return self.current_proxy
        return None
    
    def get_proxy_dict(self):
        """
        获取代理字典，用于requests库
        
        Returns:
            dict: 代理字典，格式为{proxy_type: proxy_url}
        """
        proxy = self.get_random_proxy()
        if proxy:
            return {
                self.proxy_type: f"{self.proxy_type}://{proxy}"
            }
        return None
    
    def refresh_proxies(self):
        """
        刷新代理列表
        这里可以扩展为从代理池API获取新的代理IP
        """
        # 这里只是简单实现，实际项目中可以从代理池API获取新的代理
        pass