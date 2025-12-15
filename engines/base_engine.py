from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import random

class BaseClickEngine:
    """
    基础点击引擎类，定义所有平台点击引擎的共同接口和基础功能
    """
    
    def __init__(self, config, logger, user_agent_manager, proxy_manager=None, shared_driver=None, url_template=None):
        """
        初始化基础点击引擎
        
        Args:
            config (dict): 配置字典
            logger (logging.Logger): 日志记录器
            user_agent_manager (UserAgentManager): User-Agent管理器
            proxy_manager (ProxyManager, optional): 代理管理器，默认为None
            shared_driver (webdriver.Chrome, optional): 共享的浏览器驱动实例
            url_template (str, optional): 从配置文件加载的URL模板
        """
        self.config = config
        self.logger = logger
        self.user_agent_manager = user_agent_manager
        self.proxy_manager = proxy_manager
        self.driver = shared_driver
        self.platform_name = "base"
        self.url_template = url_template
    
    def _setup_browser(self):
        """
        设置浏览器选项和驱动
        """
        # Check if browser is already initialized
        if self.driver:
            self.logger.info("Reusing existing Chrome browser...")
            # 更新User-Agent为当前平台的User-Agent
            user_agent = self.user_agent_manager.get_ua_for_platform(self.platform_name)
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
            return
            
        # 如果没有共享驱动，则创建新驱动
        chrome_options = Options()
        
        # 设置无头模式
        if self.config.get("browser", {}).get("use_headless", True):
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
        
        # 设置窗口大小
        chrome_options.add_argument("--window-size=1920,1080")
        
        # 添加其他选项
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 设置随机User-Agent
        user_agent = self.user_agent_manager.get_ua_for_platform(self.platform_name)
        chrome_options.add_argument(f"--user-agent={user_agent}")
        
        # 设置代理（如果有）
        if self.proxy_manager:
            proxy = self.proxy_manager.get_random_proxy()
            if proxy:
                chrome_options.add_argument(f"--proxy-server={proxy}")
        
        # 初始化驱动
        try:
            self.logger.info("Installing ChromeDriver...")
            driver_path = ChromeDriverManager().install()
            self.logger.info(f"ChromeDriver installed at: {driver_path}")
                
            self.logger.info("Initializing Chrome browser...")
            self.driver = webdriver.Chrome(
                service=ChromeService(driver_path),
                options=chrome_options
            )
            # 设置页面加载超时
            self.driver.set_page_load_timeout(self.config.get("browser", {}).get("page_load_timeout", 30))
            self.logger.info("Browser setup completed successfully")
        except Exception as e:
            self.logger.error(f"Failed to setup browser: {e}")
            self.logger.error(f"Error type: {type(e).__name__}")
            # 提供调试信息
            self.logger.error("Please check:")
            self.logger.error("1. Chrome browser is installed")
            self.logger.error("2. Your network connection is stable")
            self.logger.error("3. No firewall is blocking the connection")
            raise
    
    def _teardown_browser(self):
        """
        关闭浏览器
        注意：如果使用的是共享浏览器实例，此方法不会关闭浏览器
        """
        # 不关闭共享浏览器实例，由调用者负责关闭
        pass
    
    def _wait_for_page_load(self, timeout=30):
        """
        等待页面加载完成
        
        Args:
            timeout (int): 超时时间，默认30秒
            
        Returns:
            bool: 页面是否成功加载
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(('tag name', 'body'))
            )
            return True
        except TimeoutException:
            self.logger.warning(f"Page load timeout on {self.platform_name}")
            return False
    
    def _simulate_user_behavior(self):
        """
        模拟真实用户的浏览行为
        """
        try:
            # 随机停留时间（1-5秒）
            stay_time = random.uniform(1, 5)
            time.sleep(stay_time)
            
            # 随机滚动页面
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            if scroll_height > 1000:
                scroll_steps = random.randint(2, 5)
                for _ in range(scroll_steps):
                    scroll_to = random.randint(0, scroll_height)
                    self.driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                    time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            self.logger.error(f"Failed to simulate user behavior: {e}")
    
    def click(self, article_id):
        """
        点击帖子的核心方法，需要在子类中实现
        
        Args:
            article_id (str): 帖子ID
            
        Returns:
            bool: 点击是否成功
        """
        raise NotImplementedError("click method must be implemented in subclass")
    
    def generate_url(self, article_id):
        """
        生成帖子URL，需要在子类中实现
        
        Args:
            article_id (str): 帖子ID
            
        Returns:
            str: 完整的帖子URL
        """
        raise NotImplementedError("generate_url method must be implemented in subclass")
    
    def run(self, article_id):
        """
        执行完整的点击流程
        
        Args:
            article_id (str): 帖子ID
            
        Returns:
            bool: 点击是否成功
        """
        success = False
        try:
            # 设置浏览器
            self._setup_browser()
            
            # 执行点击
            success = self.click(article_id)
            
            # 模拟用户行为
            if success:
                self._simulate_user_behavior()
        except Exception as e:
            self.logger.error(f"Failed to run click engine: {e}")
        
        return success