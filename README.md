# 自动点击帖子提高曝光度程序

## 简介

这是一个用于自动点击帖子提高曝光度的Python程序，支持搜狐、头条等多个平台。程序采用模块化设计，易于扩展和维护，并包含了基本的反检测机制。

## 功能特性

- 支持多平台（搜狐、头条）
- 随机User-Agent生成
- 代理IP支持（可选）
- 模拟真实用户行为（随机停留时间、滚动页面）
- 详细的日志记录
- 点击结果统计和报告生成
- 支持无头浏览器模式

## 目录结构

```
auto_clicker/
├── config/                # 配置文件目录
│   ├── config.json        # 主配置文件
│   ├── platforms.json     # 平台配置文件
│   └── articles.json      # 文章ID配置文件
├── engines/               # 点击引擎目录
│   ├── __init__.py
│   ├── base_engine.py     # 基础引擎类
│   ├── sohu_engine.py     # 搜狐平台引擎
│   └── toutiao_engine.py  # 头条平台引擎
├── utils/                 # 工具模块目录
│   ├── __init__.py
│   ├── proxy_manager.py   # 代理管理
│   ├── useragent.py       # User-Agent生成
│   └── logger.py          # 日志工具
├── main.py                # 主程序入口
├── requirements.txt       # 依赖库列表
└── README.md              # 说明文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置文件

### config.json

主配置文件，包含程序的运行参数：

```json
{
    "general": {
        "total_clicks": 100,        # 总点击次数
        "min_interval": 5,           # 最小点击间隔（秒）
        "max_interval": 15,          # 最大点击间隔（秒）
        "use_proxy": false,          # 是否使用代理
        "proxy_type": "http"         # 代理类型
    },
    "logging": {
        "level": "INFO",            # 日志级别
        "log_file": "auto_clicker.log"  # 日志文件路径
    },
    "browser": {
        "use_headless": true,       # 是否使用无头模式
        "page_load_timeout": 30      # 页面加载超时（秒）
    }
}
```

### platforms.json

平台配置文件，定义支持的平台信息：

```json
{
    "platforms": [
        {
            "name": "sohu",         # 平台名称（用于代码标识）
            "display_name": "搜狐",   # 平台显示名称
            "url_template": "https://www.sohu.com/a/{article_id}",  # URL模板
            "active": true           # 是否启用该平台
        },
        {
            "name": "toutiao",      # 平台名称（用于代码标识）
            "display_name": "头条",   # 平台显示名称
            "url_template": "https://www.toutiao.com/a{article_id}/",  # URL模板
            "active": true           # 是否启用该平台
        },
        {
            "name": "netease",      # 平台名称（用于代码标识）
            "display_name": "网易",   # 平台显示名称
            "url_template": "https://www.163.com/dy/article/{article_id}.html",  # URL模板
            "active": true           # 是否启用该平台
        },
        {
            "name": "smzdm",        # 平台名称（用于代码标识）
            "display_name": "什么值得买",   # 平台显示名称
            "url_template": "https://post.smzdm.com/p/{article_id}/",  # URL模板
            "active": true           # 是否启用该平台
        }
    ]
}
```

### articles.json

文章ID配置文件，统一管理各平台的文章ID：

```json
{
  "articles": {
    "description": "各平台的文章ID配置",
    "format": "{平台名称: [文章ID列表]}",
    "default": {},
    "values": {
      "sohu": [
        "906003169_211762",
        "876963035_121312308",
        "876962930_120112238"
      ],
      "toutiao": [
        "1234567890123456789",
        "9876543210987654321"
      ],
      "netease": [
        "JT43DRKV0550S2L1",
        "K30FO5MK0550S2L1"
      ],
      "smzdm": []
    }
  }
}
```

## 使用方法

1. 编辑 `config/config.json` 文件，调整运行参数
2. 编辑 `config/platforms.json` 文件，添加或修改平台配置
3. 编辑 `config/articles.json` 文件，添加各平台的文章ID
4. 运行程序：

```bash
python main.py
```

## 示例帖子ID格式

### 搜狐平台

搜狐帖子ID格式为 `数字_数字`，例如：`123456789_12345`

### 头条平台

头条帖子ID格式为纯数字，例如：`1234567890123456789`

### 网易平台

网易帖子ID格式为字母数字组合，通常以字母开头，例如：`H1234567890ABCDEF`

## 可能遇到的问题及解决方案

### 1. ChromeDriver安装失败

**错误信息**：`Could not reach host. Are you offline?`

**解决方案**：
- 确保网络连接稳定
- 检查防火墙设置，确保允许连接到ChromeDriver下载服务器
- 手动下载ChromeDriver并指定路径：
  1. 访问 https://chromedriver.chromium.org/downloads 下载与Chrome浏览器版本匹配的ChromeDriver
  2. 解压并保存到本地目录
  3. 修改 `engines/base_engine.py` 文件，直接使用本地ChromeDriver路径：
     ```python
     from selenium.webdriver.chrome.service import Service as ChromeService
     
     # 将ChromeDriverManager().install()替换为本地路径
     driver_path = "C:/path/to/chromedriver.exe"
     self.driver = webdriver.Chrome(
         service=ChromeService(driver_path),
         options=chrome_options
     )
     ```

### 2. Chrome浏览器未安装

**解决方案**：
- 安装Chrome浏览器
- 或修改代码使用其他浏览器（如Firefox、Edge）

### 3. 点击成功率低

**解决方案**：
- 增加点击间隔时间
- 启用代理IP
- 调整浏览器设置，禁用无头模式进行调试

## 扩展说明

### 添加新平台

1. 在 `engines` 目录下创建新的引擎类，继承自 `BaseClickEngine`
2. 实现 `generate_url` 和 `click` 方法
3. 在 `engines/__init__.py` 中导出新的引擎类
4. 在 `main.py` 中添加新平台的初始化逻辑
5. 在 `platforms.json` 中添加新平台的配置

### 自定义用户行为

修改 `base_engine.py` 文件中的 `_simulate_user_behavior` 方法，添加更多真实用户行为模拟，如：
- 点击页面元素
- 停留更长时间
- 复制文本
- 打开新标签页

## 注意事项

1. 遵守平台规则，避免过度使用导致账号或IP被封禁
2. 建议使用合法代理IP，避免使用恶意IP
3. 定期更新User-Agent列表
4. 根据平台反爬策略调整点击频率和行为
5. 本程序仅用于学习和研究目的，请勿用于非法用途

## 许可证

MIT License
