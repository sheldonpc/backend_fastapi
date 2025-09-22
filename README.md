# myBlog - 现代化异步博客系统

基于 FastAPI 构建的高性能异步博客后端服务，支持用户认证、内容管理和管理员后台。

## 技术栈

- **框架**: FastAPI (异步Web框架)
- **数据库**: MySQL (通过 Tortoise ORM + aiomysql)
- **缓存**: Redis
- **认证**: JWT + OAuth2
- **密码加密**: bcrypt
- **邮件服务**: SMTP (支持HTML模板)

## 项目结构

```
myBlog/
├── app/                          # 应用主目录
│   ├── admin_ui/templates/       # 管理员界面模板
│   │   ├── admin.html           # 管理后台主页
│   │   ├── articles.html        # 文章管理页面
│   │   ├── config.html          # 配置管理页面
│   │   ├── login.html           # 登录页面
│   │   ├── overview.html        # 概览页面
│   │   ├── roles.html           # 角色管理页面
│   │   └── users.html           # 用户管理页面
│   ├── middlewares/              # 中间件
│   │   └── error_handler.py     # 错误处理中间件
│   ├── routers/                  # 路由模块
│   │   ├── admin.py             # 管理员后台路由
│   │   ├── api_articles.py      # 文章管理API
│   │   ├── api_config.py        # 配置管理API
│   │   ├── api_users.py         # 用户管理API
│   │   ├── articles.py          # 文章相关路由
│   │   ├── auth.py              # 认证路由
│   │   ├── comments.py          # 评论路由
│   │   ├── likes.py             # 点赞/收藏路由
│   │   ├── roles.py             # 角色管理路由
│   │   └── users.py             # 用户路由
│   ├── utils/                    # 工具类
│   │   ├── code.py              # 验证码生成
│   │   ├── email.py             # 邮件发送
│   │   ├── email_changepwd.html # 修改密码邮件模板
│   │   ├── email_verification.html # 邮箱验证模板
│   │   ├── logger.py            # 日志配置
│   │   ├── rate_limiter.py      # 限流器
│   │   ├── redis_client.py      # Redis客户端
│   │   ├── security.py          # 安全工具(JWT,密码加密)
│   │   └── user_utils.py        # 用户工具函数
│   ├── config.py                 # 配置文件
│   ├── database.py               # 数据库连接
│   ├── deps.py                   # 依赖注入
│   ├── main.py                   # 应用入口
│   ├── models.py                 # 数据模型
│   └── schemas.py                # Pydantic模式
├── migrations/models/            # 数据库迁移文件
├── requirements.txt              # 项目依赖
├── pyproject.toml               # 项目配置
└── README.md                    # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 环境配置

创建 `.env` 文件：

```env
DATABASE_URL=mysql://username:password@localhost:3306/myblog
SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password
```

### 3. 启动服务

```bash
# 开发环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000/docs` 查看 API 文档

## API 端点列表

### 🔐 认证相关 (`/auth`)

| 方法 | 端点 | 描述 | 限流 |
|------|------|------|------|
| POST | `/auth/register` | 用户注册 | 3次/分钟 |
| POST | `/auth/login` | 用户登录 | - |
| POST | `/auth/reset-password` | 重置密码 | - |
| POST | `/auth/send-code` | 发送验证码 | - |

### 👤 用户管理 (`/users`)

| 方法 | 端点 | 描述 | 权限要求 |
|------|------|------|----------|
| GET | `/users/me` | 获取当前用户信息 | 登录用户 |
| PUT | `/users/me` | 更新用户信息 | 登录用户 |
| GET | `/users/me/avatar` | 上传头像 | 登录用户 |
| POST | `/users/change_password` | 修改密码 | 登录用户 (3次/分钟) |

### 📝 文章管理 (`/articles`)

| 方法 | 端点 | 描述 | 权限要求 |
|------|------|------|----------|
| POST | `/articles/` | 创建文章 | 登录用户 |
| PUT | `/articles/{article_id}` | 更新文章 | 文章作者 |
| DELETE | `/articles/{article_id}` | 删除文章 | 文章作者 |
| GET | `/articles/` | 文章列表(分页) | 公开 |
| GET | `/articles/{article_id}` | 文章详情 | 公开 |
| GET | `/articles/search` | 搜索文章 | 公开 |

### 💬 评论系统 (`/comments`)

| 方法 | 端点 | 描述 | 权限要求 |
|------|------|------|----------|
| POST | `/comments/` | 发表评论 | 登录用户 |
| GET | `/comments/article/{article_id}` | 获取文章评论 | 公开 |

### ❤️ 互动功能 (`/interactions`)

| 方法 | 端点 | 描述 | 权限要求 |
|------|------|------|----------|
| POST | `/interactions/article/{article_id}/like` | 点赞/取消点赞文章 | 登录用户 |
| POST | `/interactions/comment/{comment_id}/like` | 点赞/取消点赞评论 | 登录用户 |
| POST | `/interactions/article/{article_id}/favorite` | 收藏/取消收藏文章 | 登录用户 |

### 🛠️ 管理员功能 (`/admin`)

#### 后台页面
| 方法 | 端点 | 描述 | 权限要求 |
|------|------|------|----------|
| GET | `/admin/` | 管理后台首页 | 管理员 |
| GET | `/admin/verify` | 验证管理员权限 | 管理员 |
| GET | `/admin/users_page` | 用户管理页面 | 管理员 |
| GET | `/admin/articles_page` | 文章管理页面 | 管理员 |

#### 数据统计
| 方法 | 端点 | 描述 | 权限要求 |
|------|------|------|----------|
| GET | `/admin/api/stats` | 后台统计数据 | 管理员 |
| GET | `/admin/api/recent-logs` | 最近操作日志 | 管理员 |

#### 用户管理API (`/admin/api/users`)
| 方法 | 端点 | 描述 | 权限要求 |
|------|------|------|----------|
| GET | `/admin/api/users/` | 用户列表(分页/搜索) | 管理员 |
| POST | `/admin/api/users/` | 创建用户 | 管理员 |
| PUT | `/admin/api/users/{user_id}` | 更新用户 | 管理员 |
| PATCH | `/admin/api/users/{user_id}/status` | 更新用户状态 | 管理员 |
| DELETE | `/admin/api/users/{user_id}` | 删除用户 | 管理员 |
| GET | `/admin/api/users/export` | 导出用户Excel | 管理员 |

#### 文章管理API (`/admin/api/articles`)
| 方法 | 端点 | 描述 | 权限要求 |
|------|------|------|----------|
| GET | `/admin/api/articles/` | 文章列表 | 管理员 |
| POST | `/admin/api/articles/` | 创建文章 | 管理员 |
| PUT | `/admin/api/articles/{article_id}` | 更新文章 | 管理员 |
| DELETE | `/admin/api/articles/{article_id}` | 删除文章 | 管理员 |

#### 角色管理API (`/admin/api/roles`)
| 方法 | 端点 | 描述 | 权限要求 |
|------|------|------|----------|
| GET | `/admin/api/roles/` | 角色列表 | 管理员 |
| POST | `/admin/api/roles/` | 创建角色 | 管理员 |
| PUT | `/admin/api/roles/{role_id}` | 更新角色 | 管理员 |
| DELETE | `/admin/api/roles/{role_id}` | 删除角色 | 管理员 |

#### 配置管理API (`/admin/api/config`)
| 方法 | 端点 | 描述 | 权限要求 |
|------|------|------|----------|
| GET | `/admin/api/config/` | 配置列表 | 管理员 |
| POST | `/admin/api/config/` | 创建配置 | 管理员 |
| PUT | `/admin/api/config/{config_id}` | 更新配置 | 管理员 |

### 🌐 其他端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | API根路径 |
| GET | `/login` | 登录页面 |
| GET | `/hello/{name}` | 问候接口 |
| GET | `/docs` | Swagger API文档 |

## 特性

- ✅ **异步架构**: 基于FastAPI的完全异步操作
- ✅ **JWT认证**: 安全的用户身份验证
- ✅ **邮箱验证**: 注册和密码重置邮箱验证
- ✅ **限流保护**: 防止接口滥用
- ✅ **管理后台**: 完整的Web管理界面
- ✅ **文件上传**: 支持头像上传
- ✅ **数据导出**: Excel格式数据导出
- ✅ **搜索功能**: 文章内容搜索
- ✅ **评论系统**: 多级评论支持
- ✅ **互动功能**: 点赞、收藏系统
- ✅ **角色管理**: 灵活的权限控制

## 开发说明

- 数据库迁移位于 `migrations/models/` 目录
- 静态文件上传至 `uploads/` 目录
- 管理后台访问: `/admin/`
- API文档地址: `/docs` 或 `/redoc`

## 许可证

MIT License