# SoulStation 后端服务

## 快速开始

### 1. 配置数据库

确保 MySQL 服务正在运行，然后使用 Docker Compose 启动数据库：

```bash
docker-compose up -d mysql
```

或手动创建数据库：

```sql
CREATE DATABASE soulstation DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后运行初始化脚本：

```bash
mysql -u root -p soulstation < sql/init.sql
```

### 2. 配置环境变量

项目根目录已包含 `.env` 环境变量文件，直接修改其中的配置：

主要配置项：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/soulstation

# JWT 密钥（生产环境请修改）
SECRET_KEY=your-secret-key-here-change-in-production

# 邮件配置（QQ邮箱）
MAIL_USERNAME=1748618129@qq.com
MAIL_PASSWORD=buxydgasahfwdfgj
MAIL_FROM=1748618129@qq.com
MAIL_FROM_NAME=SoulStation心理咨询平台
MAIL_PORT=587
MAIL_SERVER=smtp.qq.com
MAIL_TLS=True
MAIL_SSL=False

# 前端 URL
FRONTEND_URL=http://localhost:5173
```

**邮件配置说明**：
- QQ邮箱需要使用"授权码"而不是QQ密码
- 获取授权码：QQ邮箱 → 设置 → 账户 → SMTP服务
- 其他邮箱配置请参考 `.env` 文件中的注释

### 3. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 启动服务

**方式一：使用启动脚本**

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

**方式二：手动启动**

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务将在 http://localhost:8000 启动

## API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 认证接口

### 1. 用户登录

```
POST /api/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "123456"
}
```

**响应：**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "nickname": "测试用户",
    "role": "user",
    "is_active": true,
    "created_at": "2026-02-26T12:00:00"
  }
}
```

### 2. 用户注册

```
POST /api/auth/register
Content-Type: application/json

{
  "email": "newuser@example.com",
  "code": "123456",
  "password": "123456"
}
```

### 3. 发送验证码

```
POST /api/auth/send-code
Content-Type: application/json

{
  "email": "newuser@example.com"
}
```

### 4. 获取当前用户信息

```
GET /api/auth/user-info
Authorization: Bearer <access_token>
```

### 5. 退出登录

```
POST /api/auth/logout
Authorization: Bearer <access_token>
```

## 测试账户

开发环境提供了测试账户：

- **邮箱**: test@example.com
- **密码**: 123456

创建测试用户：

```bash
python -m app.core.init_db
```

## 邮件功能测试

### 测试邮件发送

运行邮件测试脚本：

```bash
python test_email.py
```

测试选项：
1. 发送验证码 - 测试发送验证码功能
2. 验证验证码 - 测试验证验证码功能
3. 发送欢迎邮件 - 测试发送欢迎邮件
4. 检查验证码剩余时间 - 查看验证码是否还有效

**功能特性**：
- ✅ 自动发送验证码到用户邮箱
- ✅ 验证码5分钟有效期
- ✅ 防止频繁发送（60秒冷却时间）
- ✅ 注册成功后自动发送欢迎邮件
- ✅ 开发环境在控制台打印验证码


## 项目结构

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   ├── auth/         # 认证相关接口
│   │   ├── chat/         # 聊天相关接口
│   │   ├── test/         # 测试相关接口
│   │   └── ...
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置文件
│   │   ├── database.py   # 数据库连接
│   │   ├── security.py   # 安全相关（JWT, 密码加密）
│   │   └── init_db.py    # 数据库初始化
│   ├── models/           # 数据库模型
│   │   └── user.py       # 用户模型
│   ├── schemas/          # Pydantic Schemas
│   │   ├── user.py       # 用户相关 Schema
│   │   └── auth.py       # 认证相关 Schema
│   ├── services/         # 业务逻辑层
│   │   ├── auth_service.py        # 认证服务
│   │   ├── email_service.py       # 邮件服务
│   │   └── verification_service.py # 验证码服务
│   └── main.py           # 应用入口
├── sql/                  # 数据库脚本
│   ├── init.sql          # 初始化脚本
│   └── insert_data.sql   # 测试数据
├── requirements.txt      # Python 依赖
├── .env                  # 环境变量
├── start.bat             # 启动脚本（Windows）
├── start.sh              # 启动脚本（Linux/Mac）
├── test_login.py         # 登录功能测试
├── test_email.py         # 邮件功能测试
├── README.md             # 项目说明
```

## 开发说明

### 添加新的 API 接口

1. 在 `app/api/` 下创建对应的模块
2. 在 `app/schemas/` 下定义请求/响应模型
3. 在 `app/services/` 下实现业务逻辑
4. 在 `app/main.py` 中注册路由

### 数据库迁移

```bash
# 创建新的迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 常见问题

### 1. 数据库连接失败

检查 `DATABASE_URL` 配置是否正确，确保 MySQL 服务正在运行。

### 2. JWT 验证失败

确保前后端的 `SECRET_KEY` 一致。

### 3. CORS 错误

检查 `.env` 中的 `FRONTEND_URL` 是否正确。

## 技术栈

- **框架**: FastAPI
- **数据库**: MySQL (SQLAlchemy ORM)
- **认证**: JWT (python-jose)
- **密码加密**: Bcrypt (passlib)
- **数据验证**: Pydantic
