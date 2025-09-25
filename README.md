# 金融投资数据平台 / Financial Investment Data Platform

[中文](#中文文档) | [English](#english-documentation)

---

## 中文文档

### 项目简介

基于FastAPI构建的现代化金融投资数据平台，集成AI市场分析和实时数据爬取功能。项目采用RESTful API设计风格，提供完整的金融数据服务。

### 技术栈

- **后端框架**: FastAPI (Python 3.8+)
- **数据库**: SQLite with Tortoise ORM
- **认证**: JWT Token
- **数据爬取**: Selenium WebDriver
- **AI分析**: LangChain集成
- **异步处理**: asyncio
- **API文档**: Swagger UI / ReDoc

### 核心功能

- ✅ 实时金融数据爬取（A股指数、美股指数、贵金属）
- ✅ 智能定时调度器（交易时间自动执行）
- ✅ RESTful API设计
- ✅ JWT用户认证和权限管理
- ✅ 市场情绪AI分析
- ✅ 数据可视化接口
- ✅ 多数据源配置管理

### RESTful API设计规范

#### API设计原则

本项目严格遵循RESTful设计风格：

1. **资源导向**: 每个URL代表一种资源
2. **HTTP动词**: 使用标准HTTP方法（GET、POST、PUT、DELETE）
3. **状态码**: 合理使用HTTP状态码
4. **统一响应格式**: 标准化的JSON响应结构
5. **版本控制**: 通过URL路径进行版本管理

#### API端点总览

##### 用户认证模块 (`/auth`)

| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| `POST` | `/auth/register` | 用户注册 | 公开 |
| `POST` | `/auth/login` | 用户登录 | 公开 |
| `GET` | `/auth/me` | 获取用户信息 | 登录用户 |
| `PUT` | `/auth/profile` | 更新用户资料 | 登录用户 |

##### 金融数据模块 (`/financial`)

| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| `GET` | `/financial/market/latest` | 获取最新市场数据 | 公开 |
| `GET` | `/financial/market/overview` | 获取市场概览 | 公开 |
| `GET` | `/financial/market/status` | 获取数据状态 | 公开 |
| `POST` | `/financial/market/crawl` | 手动触发爬取 | 登录用户 |
| `POST` | `/financial/market/crawl-now` | 立即执行爬取 | 管理员 |

##### 调度器控制模块 (`/financial/scheduler`)

| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| `GET` | `/financial/scheduler/status` | 获取调度器状态 | 公开 |
| `POST` | `/financial/scheduler/start` | 启动调度器 | 管理员 |
| `POST` | `/financial/scheduler/stop` | 停止调度器 | 管理员 |

##### 内容管理模块 (`/articles`, `/categories`, `/tags`)

| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| `GET` | `/articles` | 获取文章列表 | 公开 |
| `GET` | `/articles/{id}` | 获取文章详情 | 公开 |
| `POST` | `/articles` | 创建文章 | 登录用户 |
| `PUT` | `/articles/{id}` | 更新文章 | 作者/管理员 |
| `DELETE` | `/articles/{id}` | 删除文章 | 作者/管理员 |

#### 响应格式规范

##### 成功响应格式
```json
{
  "success": true,
  "data": {
    // 具体数据内容
  },
  "message": "操作成功描述"
}
```

##### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "错误描述",
    "details": "详细错误信息"
  }
}
```

##### 分页响应格式
```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

### 项目结构

```
myBlog/
├── app/
│   ├── main.py              # 应用入口
│   ├── models.py            # 数据模型
│   ├── schemas.py           # Pydantic模式
│   ├── deps.py              # 依赖注入
│   ├── config.py            # 配置管理
│   ├── routers/             # 路由模块
│   │   ├── auth.py          # 认证路由
│   │   ├── users.py         # 用户路由
│   │   ├── articles.py      # 文章路由
│   │   ├── comments.py      # 评论路由
│   │   └── financial.py     # 金融数据路由
│   └── services/            # 业务服务
│       ├── market_service.py # 市场数据服务
│       └── scheduler.py     # 定时调度器
├── requirements.txt         # 依赖包
├── .env.example            # 环境变量模板
└── README.md               # 项目说明
```

### 快速开始

#### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd myBlog

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 环境配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
# 配置数据库连接、JWT密钥、数据源URL等
```

#### 3. 运行项目
```bash
# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问API文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### 数据源配置

在`.env`文件中配置数据源：

```env
# 中国指数数据源
CHINA_SHANGHAI_URL=http://quote.eastmoney.com/sh000001.html
CHINA_SHENZHEN_URL=http://quote.eastmoney.com/sz399001.html
CHINA_CHINEXT_URL=http://quote.eastmoney.com/sz399006.html

# 美股指数数据源
US_DOW_URL=http://quote.eastmoney.com/gb/DJIA.html
US_NASDAQ_URL=http://quote.eastmoney.com/gb/IXIC.html
US_SP500_URL=http://quote.eastmoney.com/gb/SPX.html

# 贵金属数据源
GOLD_URL=http://quote.eastmoney.com/qh/AU0.html
SILVER_URL=http://quote.eastmoney.com/qh/AG0.html
```

### 部署说明

#### Docker部署
```bash
# 构建镜像
docker build -t financial-platform .

# 运行容器
docker run -d -p 8000:8000 --name financial-app financial-platform
```

#### 生产环境
```bash
# 使用Gunicorn部署
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## English Documentation

### Project Overview

A modern financial investment data platform built with FastAPI, integrating AI market analysis and real-time data crawling capabilities. The project follows RESTful API design principles to provide comprehensive financial data services.

### Tech Stack

- **Backend Framework**: FastAPI (Python 3.8+)
- **Database**: SQLite with Tortoise ORM
- **Authentication**: JWT Token
- **Data Crawling**: Selenium WebDriver
- **AI Analysis**: LangChain Integration
- **Async Processing**: asyncio
- **API Documentation**: Swagger UI / ReDoc

### Core Features

- ✅ Real-time financial data crawling (A-shares, US stocks, precious metals)
- ✅ Intelligent scheduled tasks (auto-execution during trading hours)
- ✅ RESTful API design
- ✅ JWT user authentication and authorization
- ✅ AI-powered market sentiment analysis
- ✅ Data visualization interfaces
- ✅ Multi-source configuration management

### RESTful API Design Standards

#### API Design Principles

This project strictly follows RESTful design patterns:

1. **Resource-Oriented**: Each URL represents a resource
2. **HTTP Verbs**: Standard HTTP methods (GET, POST, PUT, DELETE)
3. **Status Codes**: Proper use of HTTP status codes
4. **Uniform Response Format**: Standardized JSON response structure
5. **Versioning**: Version control through URL paths

#### API Endpoints Overview

##### Authentication Module (`/auth`)

| Method | Endpoint | Function | Permission |
|--------|----------|----------|------------|
| `POST` | `/auth/register` | User registration | Public |
| `POST` | `/auth/login` | User login | Public |
| `GET` | `/auth/me` | Get user info | Authenticated |
| `PUT` | `/auth/profile` | Update profile | Authenticated |

##### Financial Data Module (`/financial`)

| Method | Endpoint | Function | Permission |
|--------|----------|----------|------------|
| `GET` | `/financial/market/latest` | Get latest market data | Public |
| `GET` | `/financial/market/overview` | Get market overview | Public |
| `GET` | `/financial/market/status` | Get data status | Public |
| `POST` | `/financial/market/crawl` | Manual crawl trigger | Authenticated |
| `POST` | `/financial/market/crawl-now` | Execute crawl now | Admin |

##### Scheduler Control Module (`/financial/scheduler`)

| Method | Endpoint | Function | Permission |
|--------|----------|----------|------------|
| `GET` | `/financial/scheduler/status` | Get scheduler status | Public |
| `POST` | `/financial/scheduler/start` | Start scheduler | Admin |
| `POST` | `/financial/scheduler/stop` | Stop scheduler | Admin |

##### Content Management Module (`/articles`, `/categories`, `/tags`)

| Method | Endpoint | Function | Permission |
|--------|----------|----------|------------|
| `GET` | `/articles` | Get article list | Public |
| `GET` | `/articles/{id}` | Get article details | Public |
| `POST` | `/articles` | Create article | Authenticated |
| `PUT` | `/articles/{id}` | Update article | Author/Admin |
| `DELETE` | `/articles/{id}` | Delete article | Author/Admin |

#### Response Format Standards

##### Success Response Format
```json
{
  "success": true,
  "data": {
    // Specific data content
  },
  "message": "Success message"
}
```

##### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Error description",
    "details": "Detailed error information"
  }
}
```

##### Paginated Response Format
```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

### Project Structure

```
myBlog/
├── app/
│   ├── main.py              # Application entry
│   ├── models.py            # Data models
│   ├── schemas.py           # Pydantic schemas
│   ├── deps.py              # Dependency injection
│   ├── config.py            # Configuration management
│   ├── routers/             # Router modules
│   │   ├── auth.py          # Authentication routes
│   │   ├── users.py         # User routes
│   │   ├── articles.py      # Article routes
│   │   ├── comments.py      # Comment routes
│   │   └── financial.py     # Financial data routes
│   └── services/            # Business services
│       ├── market_service.py # Market data service
│       └── scheduler.py     # Task scheduler
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
└── README.md               # Project documentation
```

### Quick Start

#### 1. Environment Setup
```bash
# Clone the project
git clone <repository-url>
cd myBlog

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration file
# Configure database connection, JWT secret, data source URLs, etc.
```

#### 3. Run the Project
```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Data Source Configuration

Configure data sources in `.env` file:

```env
# Chinese Index Data Sources
CHINA_SHANGHAI_URL=http://quote.eastmoney.com/sh000001.html
CHINA_SHENZHEN_URL=http://quote.eastmoney.com/sz399001.html
CHINA_CHINEXT_URL=http://quote.eastmoney.com/sz399006.html

# US Stock Index Data Sources
US_DOW_URL=http://quote.eastmoney.com/gb/DJIA.html
US_NASDAQ_URL=http://quote.eastmoney.com/gb/IXIC.html
US_SP500_URL=http://quote.eastmoney.com/gb/SPX.html

# Precious Metals Data Sources
GOLD_URL=http://quote.eastmoney.com/qh/AU0.html
SILVER_URL=http://quote.eastmoney.com/qh/AG0.html
```

### Deployment

#### Docker Deployment
```bash
# Build image
docker build -t financial-platform .

# Run container
docker run -d -p 8000:8000 --name financial-app financial-platform
```

#### Production Environment
```bash
# Deploy with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 贡献指南 / Contributing

欢迎提交Issue和Pull Request！ / Issues and Pull Requests are welcome!

## 许可证 / License

MIT License