## English

### 📋 Project Overview

Smart Financial Blog Platform is a comprehensive FastAPI-based system that integrates real-time financial data aggregation with intelligent content management. The platform provides AI-driven market analysis, multi-source data integration, and a robust publishing framework for financial content.

### 🌐 Online Experience

You can experience the platform at: **https://117.72.79.1/**

### ✨ Key Features

#### 🚀 Core Capabilities
- **Real-time Market Data**: Live stock indices, precious metals, and forex monitoring
- **AI-Powered Analysis**: Intelligent market sentiment analysis and financial insights
- **Multi-source Data Integration**: Aggregates data from multiple financial APIs and news sources
- **Automated Data Pipeline**: Scheduled data collection and processing with Redis caching

#### 📊 Financial Intelligence
- **Market Temperature Monitoring**: Real-time market activity and temperature indicators
- **VIX Fear Index**: Volatility tracking and market sentiment analysis
- **Multi-timeframe Analysis**: Support for various time periods (3D, 5D, 10D, 20D)
- **Sector Performance Tracking**: Industry and concept sector rankings

#### 📝 Content Management
- **Multi-role User System**: Admin, Editor, and User role management
- **Article Publishing**: Rich text editor with category and tag support
- **Comment System**: Interactive commenting with moderation features
- **Like & Favorite**: Social engagement features

#### 🛡️ Security & Performance
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: API rate limiting and DDoS protection
- **Redis Caching**: High-performance data caching layer
- **Database Migration**: Automated database schema management

### 🏗️ Architecture

```
├── app/
│   ├── core/              # Core configuration and templates
│   ├── middlewares/       # Custom middleware (error handling, rate limiting)
│   ├── routers/           # API route handlers
│   │   ├── internal/      # Internal services (stock, industry, concept data)
│   │   │   ├── concept_service.py    # Concept data service
│   │   │   ├── hot_service.py        # Hot stocks service
│   │   │   ├── hotsearch_service.py   # Hot search service
│   │   │   ├── hotup_service.py      # Rising stocks service
│   │   │   ├── industry_service.py   # Industry data service
│   │   │   ├── lhb_service.py        # Dragon and tiger list service
│   │   │   ├── stock_service.py      # Stock data service
│   │   │   └── zt_service.py         # Limit-up stocks service
│   │   ├── admin.py                  # Admin management APIs
│   │   ├── admin_messages.py         # Admin message management
│   │   ├── api_articles.py           # Article management APIs
│   │   ├── api_config.py             # Configuration management
│   │   ├── api_fetch_data.py         # Data fetching APIs
│   │   ├── api_index.py              # Index page APIs
│   │   ├── api_profile.py            # User profile APIs
│   │   ├── api_strategy.py           # Strategy management APIs
│   │   ├── api_users.py              # User management APIs
│   │   ├── articles.py               # Article page routes
│   │   ├── auth.py                   # Authentication endpoints
│   │   ├── board.py                  # Financial dashboard APIs
│   │   ├── comments.py               # Comment management
│   │   ├── error.py                  # Error handling
│   │   ├── financial.py              # Financial data APIs
│   │   ├── likes.py                  # Like/unlike functionality
│   │   ├── market.py                 # Market data endpoints
│   │   ├── messages.py               # Message management
│   │   ├── messages_page.py          # Message page routes
│   │   ├── roles.py                  # Role management
│   │   ├── root.py                   # Root page routes
│   │   ├── strategy.py               # Strategy page routes
│   │   ├── strategy_user.py          # User strategy routes
│   │   ├── upload.py                 # File upload functionality
│   │   ├── users.py                  # User page routes
│   │   └── websocket.py              # WebSocket connections
│   ├── services/          # Business logic services
│   │   ├── ai_insight_data.py        # AI insight data service
│   │   ├── logs/                     # Log services
│   │   ├── market_data_service.py    # Market data service
│   │   ├── market_service.py         # Market service
│   │   ├── scheduler.py              # Task scheduler
│   │   ├── scheduler_market_data.py # Market data scheduler
│   │   └── specific_stock_data.py    # Specific stock data service
│   ├── static/             # Static files
│   │   ├── css/                     # CSS stylesheets
│   │   ├── images/                  # Image files
│   │   └── js/                      # JavaScript files
│   ├── templates/          # HTML templates
│   │   ├── admin/                   # Admin templates
│   │   └── public/                  # Public templates
│   ├── utils/              # Utility functions and helpers
│   │   ├── ai_market.py             # AI market analysis
│   │   ├── code.py                  # Code utilities
│   │   ├── crawl_report.py          # Crawling report utilities
│   │   ├── email.py                 # Email services
│   │   ├── eventData.py             # Event data utilities
│   │   ├── logger.py                # Logging utilities
│   │   ├── markdown_process.py       # Markdown processing
│   │   ├── rate_limiter.py          # Rate limiting
│   │   ├── realtime_market_data.py  # Real-time market data
│   │   ├── redis_client.py          # Redis client
│   │   ├── security.py              # Security utilities
│   │   ├── status_decorator.py      # Status decorators
│   │   ├── user_utils.py            # User utilities
│   │   └── warm_up_tasks.py         # Warm-up tasks
│   ├── database.py         # Database configuration
│   ├── deps.py             # Dependencies
│   ├── exceptions.py       # Custom exceptions
│   ├── main.py             # Application entry point
│   ├── models.py           # Database models
│   └── schemas.py          # Pydantic data validation schemas
├── migrations/            # Database migrations
│   └── models/            # Model migrations
├── upload/                # Upload directory
│   └── images/            # Uploaded images
├── uploads/               # Additional uploads
│   └── avatars/           # User avatars
├── logs/                  # Application logs
├── crawlData/             # Crawled data
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── .env                   # Environment variables
├── nginx.conf             # Nginx configuration
├── deploy.sh              # Deployment script
├── quick_deploy.sh        # Quick deployment script
├── start_production.sh    # Production startup script
├── myblog.service         # Service configuration
└── myblog_production.service # Production service configuration
```

### 🚀 Quick Start

#### Prerequisites
- Python 3.9+
- MySQL/PostgreSQL
- Redis

#### Installation (Traditional)

1. **Clone the repository**
```bash
git clone <repository-url>
cd myBlog
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.bac.example .env.bac
# Edit .env.bac with your database and API configurations
```

4. **Run database migrations**
```bash
aerich upgrade
```

5. **Start the application**
```bash
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

#### Installation (Docker - Recommended)

For easier deployment and better environment consistency, you can use Docker:

1. **Clone the repository**
```bash
git clone <repository-url>
cd myBlog
```

2. **Build and start services**
```bash
docker-compose up -d
```

3. **Run database migrations**
```bash
docker-compose exec app aerich upgrade
```

The application will be available at `http://localhost:8000`

See [README.DOCKER.md](README.DOCKER.md) for detailed Docker deployment instructions.

### 📚 API Documentation

#### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | User login |
| POST | `/auth/register` | User registration |
| POST | `/auth/reset-password` | Password reset |

#### Market Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/main_market` | Main market data |
| GET | `/risedown` | Rise/fall statistics |
| GET | `/vix` | VIX fear index data |
| GET | `/market/stock/{stock_code}` | Get stock market data |
| GET | `/market/stock/{stock_code}/kline` | Get stock K-line data |
| GET | `/market/stock/{stock_code}/quote` | Get stock quote data |
| GET | `/market/stock/{stock_code}/trend` | Get stock trend data |
| GET | `/market/stock/{stock_code}/financial` | Get stock financial data |
| GET | `/market/stock/{stock_code}/holders` | Get stock holders data |
| GET | `/market/stock/{stock_code}/news` | Get stock related news |

#### Board Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/board/industry` | Industry board data |
| GET | `/api/board/stock` | Stock board data |
| GET | `/api/board/concept` | Concept board data |

#### User Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user-management/users` | Get user list |
| POST | `/api/user-management/users` | Create new user |
| PUT | `/api/user-management/users/{user_id}` | Update user |
| DELETE | `/api/user-management/users/{user_id}` | Delete user |
| PUT | `/api/user-management/users/{user_id}/status` | Update user status |
| GET | `/api/user-management/export` | Export users to Excel |

#### Article Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/articles` | Get articles list |
| POST | `/api/articles` | Create new article |
| GET | `/api/articles/{article_id}` | Get article details |
| PUT | `/api/articles/{article_id}` | Update article |
| DELETE | `/api/articles/{article_id}` | Delete article |
| POST | `/api/articles/{article_id}/like` | Like article |
| POST | `/api/articles/{article_id}/unlike` | Unlike article |

#### User Profile Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile` | Get user profile |
| PUT | `/api/profile` | Update user profile |
| GET | `/api/profile/articles` | Get user's articles |
| GET | `/api/profile/strategies` | Get user's strategies |
| GET | `/api/profile/comments` | Get user's comments |
| POST | `/api/profile/change-password` | Change password |
| POST | `/api/profile/upload-avatar` | Upload avatar |

#### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/overview` | Get system overview |
| GET | `/admin/users` | Get users list |
| GET | `/admin/articles` | Get articles list |
| GET | `/admin/comments` | Get comments list |
| GET | `/admin/system/status` | Get system status |
| GET | `/admin/system/logs` | Get system logs |

### Strategy Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/api/strategies` | Get strategies list |
| POST | `/admin/api/strategies` | Create new strategy |
| GET | `/admin/api/strategies/{strategy_id}` | Get strategy details |
| PUT | `/admin/api/strategies/{strategy_id}` | Update strategy |
| DELETE | `/admin/api/strategies/{strategy_id}` | Delete strategy |

### Comment Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/comments/` | Create comment |
| GET | `/comments/article/{article_id}` | Get article comments |

### Interaction Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/interactions/article/{article_id}/like` | Like/unlike article |
| POST | `/interactions/comment/{comment_id}/like` | Like/unlike comment |
| POST | `/interactions/article/{article_id}/favorite` | Favorite/unfavorite article |

### Message Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/messages/` | Get messages list |
| PUT | `/api/messages/{message_id}/read` | Mark message as read |
| PUT | `/api/messages/read-all` | Mark all messages as read |
| DELETE | `/api/messages/{message_id}` | Delete message |
| DELETE | `/api/messages/` | Delete all messages |
| POST | `/api/messages/broadcast` | Broadcast message (admin) |
| POST | `/api/messages/send` | Send message to user (admin) |

### File Upload Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/api/upload/image` | Upload single image |
| DELETE | `/admin/api/upload/image/{image_id}` | Delete image |
| GET | `/admin/api/upload/images` | Get images list |
| POST | `/admin/api/upload/images/batch` | Upload multiple images |

### Financial Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/financial/market/latest` | Get latest market data |
| GET | `/financial/market/overview` | Get market overview |
| POST | `/financial/market/crawl` | Trigger market data crawling |
| POST | `/financial/scheduler/start` | Start scheduler (admin) |
| POST | `/financial/scheduler/stop` | Stop scheduler (admin) |
| GET | `/financial/scheduler/status` | Get scheduler status |
| POST | `/financial/market/crawl-now` | Execute data crawling now (admin) |
| GET | `/financial/market/status` | Get crawler status |

### WebSocket Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| WebSocket | `/ws` | Real-time WebSocket connection |

### 🔧 Configuration

Key configuration options in `app/config.py`:

```python
DATABASE_URL = "mysql://user:password@localhost/dbname"
REDIS_URL = "redis://localhost:6379"
SECRET_KEY = "your-secret-key"
OPENAI_API_KEY = "your-openai-key"  # For AI analysis features
```

### 🌟 Highlights

1. **Real-time Performance**: Sub-second market data updates with Redis caching
2. **AI Integration**: OpenAI-powered market analysis and sentiment detection
3. **Scalable Architecture**: Microservice-ready design with clean separation of concerns
4. **Production Ready**: Comprehensive error handling, logging, and monitoring
5. **Multi-language Support**: Built-in internationalization framework

### 📄 License

This project is licensed under the MIT License.

---

## Chinese

### 中文

### 📋 项目概述

智能金融博客平台是基于FastAPI构建的综合性系统，集成了实时金融数据聚合与智能内容管理功能。该平台提供AI驱动的市场分析、多源数据整合以及面向金融内容的强大发布框架。

### 🌐 在线体验

您可以通过以下地址体验平台：**https://117.72.79.1/**

### ✨ 核心特性

#### 🚀 核心功能
- **实时市场数据**: 实时股指、贵金属和外汇监控
- **AI智能分析**: 智能市场情绪分析和金融洞察
- **多源数据整合**: 聚合多个金融API和新闻源数据
- **自动化数据管道**: 定时数据采集和处理，配合Redis缓存

#### 📊 金融智能
- **市场温度监控**: 实时市场活跃度和温度指标
- **VIX恐慌指数**: 波动率追踪和市场情绪分析
- **多时间框架分析**: 支持多种时间周期（3日、5日、10日、20日）
- **板块表现追踪**: 行业和概念板块排行榜

#### 📝 内容管理
- **多角色用户系统**: 管理员、编辑者和用户角色管理
- **文章发布**: 富文本编辑器，支持分类和标签
- **评论系统**: 交互式评论，带审核功能
- **点赞收藏**: 社交互动功能

#### 🛡️ 安全与性能
- **JWT认证**: 安全的基于令牌的身份验证
- **频率限制**: API速率限制和DDoS防护
- **Redis缓存**: 高性能数据缓存层
- **数据库迁移**: 自动化数据库架构管理

### 🏗️ 系统架构

```
├── app/
│   ├── core/              # 核心配置和模板
│   ├── middlewares/       # 自定义中间件（错误处理、限流）
│   ├── routers/           # API路由处理器
│   │   ├── internal/      # 内部服务（股票、行业、概念数据）
│   │   │   ├── concept_service.py    # 概念数据服务
│   │   │   ├── hot_service.py        # 热门股票服务
│   │   │   ├── hotsearch_service.py   # 热搜服务
│   │   │   ├── hotup_service.py      # 上涨股票服务
│   │   │   ├── industry_service.py   # 行业数据服务
│   │   │   ├── lhb_service.py        # 龙虎榜服务
│   │   │   ├── stock_service.py      # 股票数据服务
│   │   │   └── zt_service.py         # 涨停股票服务
│   │   ├── admin.py                  # 管理员管理API
│   │   ├── admin_messages.py         # 管理员消息管理
│   │   ├── api_articles.py           # 文章管理API
│   │   ├── api_config.py             # 配置管理
│   │   ├── api_fetch_data.py         # 数据获取API
│   │   ├── api_index.py              # 首页API
│   │   ├── api_profile.py            # 用户资料API
│   │   ├── api_strategy.py           # 策略管理API
│   │   ├── api_users.py              # 用户管理API
│   │   ├── articles.py               # 文章页面路由
│   │   ├── auth.py                   # 认证端点
│   │   ├── board.py                  # 金融看板API
│   │   ├── comments.py               # 评论管理
│   │   ├── error.py                  # 错误处理
│   │   ├── financial.py              # 财务数据API
│   │   ├── likes.py                  # 点赞/取消点赞功能
│   │   ├── market.py                 # 市场数据端点
│   │   ├── messages.py               # 消息管理
│   │   ├── messages_page.py          # 消息页面路由
│   │   ├── roles.py                  # 角色管理
│   │   ├── root.py                   # 根页面路由
│   │   ├── strategy.py               # 策略页面路由
│   │   ├── strategy_user.py          # 用户策略路由
│   │   ├── upload.py                 # 文件上传功能
│   │   ├── users.py                  # 用户页面路由
│   │   └── websocket.py              # WebSocket连接
│   ├── services/          # 业务逻辑服务
│   │   ├── ai_insight_data.py        # AI洞察数据服务
│   │   ├── logs/                     # 日志服务
│   │   ├── market_data_service.py    # 市场数据服务
│   │   ├── market_service.py         # 市场服务
│   │   ├── scheduler.py              # 任务调度器
│   │   ├── scheduler_market_data.py # 市场数据调度器
│   │   └── specific_stock_data.py    # 特定股票数据服务
│   ├── static/             # 静态文件
│   │   ├── css/                     # CSS样式表
│   │   ├── images/                  # 图片文件
│   │   └── js/                      # JavaScript文件
│   ├── templates/          # HTML模板
│   │   ├── admin/                   # 管理员模板
│   │   └── public/                  # 公共模板
│   ├── utils/              # 工具函数和助手
│   │   ├── ai_market.py             # AI市场分析
│   │   ├── code.py                  # 代码工具
│   │   ├── crawl_report.py          # 爬虫报告工具
│   │   ├── email.py                 # 邮件服务
│   │   ├── eventData.py             # 事件数据工具
│   │   ├── logger.py                # 日志工具
│   │   ├── markdown_process.py       # Markdown处理
│   │   ├── rate_limiter.py          # 限流
│   │   ├── realtime_market_data.py  # 实时市场数据
│   │   ├── redis_client.py          # Redis客户端
│   │   ├── security.py              # 安全工具
│   │   ├── status_decorator.py      # 状态装饰器
│   │   ├── user_utils.py            # 用户工具
│   │   └── warm_up_tasks.py         # 预热任务
│   ├── database.py         # 数据库配置
│   ├── deps.py             # 依赖项
│   ├── exceptions.py       # 自定义异常
│   ├── main.py             # 应用程序入口点
│   ├── models.py           # 数据库模型
│   └── schemas.py          # Pydantic数据验证架构
├── migrations/            # 数据库迁移
│   └── models/            # 模型迁移
├── upload/                # 上传目录
│   └── images/            # 上传的图片
├── uploads/               # 附加上传
│   └── avatars/           # 用户头像
├── logs/                  # 应用程序日志
├── crawlData/             # 爬取的数据
├── requirements.txt       # Python依赖
├── pyproject.toml         # 项目配置
├── .env                   # 环境变量
├── nginx.conf             # Nginx配置
├── deploy.sh              # 部署脚本
├── quick_deploy.sh        # 快速部署脚本
├── start_production.sh    # 生产环境启动脚本
├── myblog.service         # 服务配置
└── myblog_production.service # 生产环境服务配置
```

### 🚀 快速开始

#### 环境要求
- Python 3.9+
- MySQL/PostgreSQL
- Redis

#### 安装步骤 (传统方式)

1. **克隆仓库**
```bash
git clone <repository-url>
cd myBlog
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境**
```bash
cp .env.bac.example .env.bac
# 编辑.env文件，配置数据库和API参数
```

4. **运行数据库迁移**
```bash
aerich upgrade
```

5. **启动应用**
```bash
uvicorn app.main:app --reload
```

应用将在 `http://localhost:8000` 可访问

#### 安装步骤 (Docker方式 - 推荐)

为了更简单的部署和更好的环境一致性，您可以使用Docker:

1. **克隆仓库**
```bash
git clone <repository-url>
cd myBlog
```

2. **构建并启动服务**
```bash
docker-compose up -d
```

3. **运行数据库迁移**
```bash
docker-compose exec app aerich upgrade
```

应用将在 `http://localhost:8000` 可访问

详细Docker部署说明请查看 [README.DOCKER.md](README.DOCKER.md)。

### 📚 API 文档

#### 认证接口

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/auth/login` | 用户登录 |
| POST | `/auth/register` | 用户注册 |
| POST | `/auth/reset-password` | 密码重置 |

#### 市场数据接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/main_market` | 主要市场数据 |
| GET | `/risedown` | 涨跌统计 |
| GET | `/vix` | VIX恐慌指数数据 |
| GET | `/market/stock/{stock_code}` | 获取股票市场数据 |
| GET | `/market/stock/{stock_code}/kline` | 获取股票K线数据 |
| GET | `/market/stock/{stock_code}/quote` | 获取股票报价数据 |
| GET | `/market/stock/{stock_code}/trend` | 获取股票趋势数据 |
| GET | `/market/stock/{stock_code}/financial` | 获取股票财务数据 |
| GET | `/market/stock/{stock_code}/holders` | 获取股票股东数据 |
| GET | `/market/stock/{stock_code}/news` | 获取股票相关新闻 |

#### 榜单数据接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/board/industry` | 行业榜单数据 |
| GET | `/api/board/stock` | 股票榜单数据 |
| GET | `/api/board/concept` | 概念榜单数据 |

#### 用户管理接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/user-management/users` | 获取用户列表 |
| POST | `/api/user-management/users` | 创建新用户 |
| PUT | `/api/user-management/users/{user_id}` | 更新用户 |
| DELETE | `/api/user-management/users/{user_id}` | 删除用户 |
| PUT | `/api/user-management/users/{user_id}/status` | 更新用户状态 |
| GET | `/api/user-management/export` | 导出用户到Excel |

#### 文章管理接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/articles` | 获取文章列表 |
| POST | `/api/articles` | 创建新文章 |
| GET | `/api/articles/{article_id}` | 获取文章详情 |
| PUT | `/api/articles/{article_id}` | 更新文章 |
| DELETE | `/api/articles/{article_id}` | 删除文章 |
| POST | `/api/articles/{article_id}/like` | 点赞文章 |
| POST | `/api/articles/{article_id}/unlike` | 取消点赞文章 |

#### 用户资料接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/profile` | 获取用户资料 |
| PUT | `/api/profile` | 更新用户资料 |
| GET | `/api/profile/articles` | 获取用户文章 |
| GET | `/api/profile/strategies` | 获取用户策略 |
| GET | `/api/profile/comments` | 获取用户评论 |
| POST | `/api/profile/change-password` | 修改密码 |
| POST | `/api/profile/upload-avatar` | 上传头像 |

#### 管理员接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/admin/overview` | 获取系统概览 |
| GET | `/admin/users` | 获取用户列表 |
| GET | `/admin/articles` | 获取文章列表 |
| GET | `/admin/comments` | 获取评论列表 |
| GET | `/admin/system/status` | 获取系统状态 |
| GET | `/admin/system/logs` | 获取系统日志 |

#### 策略管理接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/admin/api/strategies` | 获取策略列表 |
| POST | `/admin/api/strategies` | 创建新策略 |
| GET | `/admin/api/strategies/{strategy_id}` | 获取策略详情 |
| PUT | `/admin/api/strategies/{strategy_id}` | 更新策略 |
| DELETE | `/admin/api/strategies/{strategy_id}` | 删除策略 |

#### 评论管理接口

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/comments/` | 创建评论 |
| GET | `/comments/article/{article_id}` | 获取文章评论 |

#### 交互接口

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/interactions/article/{article_id}/like` | 点赞/取消点赞文章 |
| POST | `/interactions/comment/{comment_id}/like` | 点赞/取消点赞评论 |
| POST | `/interactions/article/{article_id}/favorite` | 收藏/取消收藏文章 |

#### 消息管理接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/messages/` | 获取消息列表 |
| PUT | `/api/messages/{message_id}/read` | 标记消息为已读 |
| PUT | `/api/messages/read-all` | 标记所有消息为已读 |
| DELETE | `/api/messages/{message_id}` | 删除消息 |
| DELETE | `/api/messages/` | 删除所有消息 |
| POST | `/api/messages/broadcast` | 广播消息（管理员） |
| POST | `/api/messages/send` | 发送消息给用户（管理员） |

#### 文件上传接口

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/admin/api/upload/image` | 上传单个图片 |
| DELETE | `/admin/api/upload/image/{image_id}` | 删除图片 |
| GET | `/admin/api/upload/images` | 获取图片列表 |
| POST | `/admin/api/upload/images/batch` | 批量上传图片 |

#### 财务数据接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/financial/market/latest` | 获取最新市场数据 |
| GET | `/financial/market/overview` | 获取市场概览 |
| POST | `/financial/market/crawl` | 触发市场数据爬取 |
| POST | `/financial/scheduler/start` | 启动调度器（管理员） |
| POST | `/financial/scheduler/stop` | 停止调度器（管理员） |
| GET | `/financial/scheduler/status` | 获取调度器状态 |
| POST | `/financial/market/crawl-now` | 立即执行数据爬取（管理员） |
| GET | `/financial/market/status` | 获取爬虫状态 |

#### WebSocket接口

| 方法 | 端点 | 描述 |
|------|------|------|
| WebSocket | `/ws` | 实时WebSocket连接 |

### 🔧 配置说明

`app/config.py` 中的关键配置选项:

```python
DATABASE_URL = "mysql://user:password@localhost/dbname"
REDIS_URL = "redis://localhost:6379"
SECRET_KEY = "your-secret-key"
OPENAI_API_KEY = "your-openai-key"  # 用于AI分析功能
```

### 🌟 亮点特性

1. **实时性能**: 基于Redis缓存的亚秒级市场数据更新
2. **AI集成**: 基于OpenAI的市场分析和情绪检测
3. **可扩展架构**: 微服务就绪的设计，关注点清晰分离
4. **生产就绪**: 全面的错误处理、日志记录和监控
5. **多语言支持**: 内置国际化框架

### 📄 许可证

该项目基于MIT许可证开源。
