# 🌟 Smart Financial Blog Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

[English](#english) | [中文](#chinese)

</div>

---

## English

### 📋 Project Overview

Smart Financial Blog Platform is a modern, AI-powered financial information aggregation and blog management system built with FastAPI. It combines real-time market data monitoring, intelligent financial analysis, and comprehensive content management capabilities.

### ✨ Key Features

#### 🚀 Core Capabilities
- **Real-time Market Data**: Live stock indices, precious metals, and forex data monitoring
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
│   │   ├── admin.py       # Admin management APIs
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── articles.py    # Article management
│   │   ├── board.py       # Financial dashboard APIs
│   │   └── market.py      # Market data endpoints
│   ├── services/          # Business logic services
│   ├── utils/             # Utility functions and helpers
│   ├── models.py          # Database models
│   └── schemas.py         # Pydantic data validation schemas
├── migrations/            # Database migrations
└── requirements.txt       # Python dependencies
```

### 🚀 Quick Start

#### Prerequisites
- Python 3.9+
- MySQL/PostgreSQL
- Redis

#### Installation

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
cp .env.example .env
# Edit .env with your database and API configurations
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

### 📚 API Documentation

#### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh

#### Market Data APIs
- `GET /api/index/` - Real-time market indices
- `GET /api/index/risedown` - Market rise/fall statistics  
- `GET /api/index/vix` - VIX fear index data
- `GET /api/board/{board_type}/{period}` - Financial ranking boards

#### Content Management
- `GET /api/articles/` - Article listing with pagination
- `POST /api/articles/` - Create new article
- `PUT /api/articles/{id}` - Update article
- `DELETE /api/articles/{id}` - Delete article

#### Admin Panel
- `GET /admin/api/stats` - Dashboard statistics
- `GET /admin/api/users` - User management
- `GET /admin/api/roles` - Role management

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

### 📋 项目概述

智能金融博客平台是一个基于FastAPI构建的现代化、AI驱动的金融信息聚合和博客管理系统。它融合了实时市场数据监控、智能金融分析和全面的内容管理功能。

### ✨ 核心特性

#### 🚀 核心功能
- **实时市场数据**: 实时股指、贵金属和外汇数据监控
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
│   │   ├── admin.py       # 管理员管理API
│   │   ├── auth.py        # 认证端点
│   │   ├── articles.py    # 文章管理
│   │   ├── board.py       # 金融看板API
│   │   └── market.py      # 市场数据端点
│   ├── services/          # 业务逻辑服务
│   ├── utils/             # 工具函数和助手
│   ├── models.py          # 数据库模型
│   └── schemas.py         # Pydantic数据验证架构
├── migrations/            # 数据库迁移
└── requirements.txt       # Python依赖
```

### 🚀 快速开始

#### 环境要求
- Python 3.9+
- MySQL/PostgreSQL
- Redis

#### 安装步骤

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
cp .env.example .env
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

应用将在 `http://localhost:8000` 可用

### 📚 API文档

#### 认证接口
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 令牌刷新

#### 市场数据API
- `GET /api/index/` - 实时市场指数
- `GET /api/index/risedown` - 市场涨跌统计
- `GET /api/index/vix` - VIX恐慌指数数据
- `GET /api/board/{board_type}/{period}` - 金融排行榜

#### 内容管理
- `GET /api/articles/` - 文章列表，支持分页
- `POST /api/articles/` - 创建新文章
- `PUT /api/articles/{id}` - 更新文章
- `DELETE /api/articles/{id}` - 删除文章

#### 管理面板
- `GET /admin/api/stats` - 仪表板统计
- `GET /admin/api/users` - 用户管理
- `GET /admin/api/roles` - 角色管理

### 🔧 配置

`app/config.py`中的关键配置选项：

```python
DATABASE_URL = "mysql://user:password@localhost/dbname"
REDIS_URL = "redis://localhost:6379"
SECRET_KEY = "your-secret-key"
OPENAI_API_KEY = "your-openai-key"  # AI分析功能所需
```

### 🌟 项目亮点

1. **实时性能**: 亚秒级市场数据更新，配合Redis缓存
2. **AI集成**: OpenAI驱动的市场分析和情绪检测
3. **可扩展架构**: 面向微服务的设计，关注点清晰分离
4. **生产就绪**: 全面的错误处理、日志记录和监控
5. **多语言支持**: 内置国际化框架

### 📄 许可证

本项目采用MIT许可证。

---

<div align="center">

**[⬆ Back to top](#-smart-financial-blog-platform)**

</div>
```