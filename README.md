# SoulStation - 心理咨询服务平台

> 心灵驿站，守护您的心理健康

## 项目简介

这是一个基于 **Vue 3 + FastAPI** 的心理咨询服务平台，提供智能心理问答、心理测试、在线咨询预约等功能。

## 核心功能

- 🤖 **智能心理问答** - 基于 RAG 检索增强生成的 AI 心理咨询
- 🎤 **语音转文字** - 集成豆包语音识别，支持语音输入
- 📝 **心理测试** - 9套专业心理测试量表（159题）
- 👨‍⚕️ **在线咨询** - 专业咨询师预约与实时对话
- 📚 **心理知识** - 心理健康文章与科普
- 🔐 **安全认证** - JWT Token + 邮箱验证

## 技术栈

### 前端
- **框架**: Vue 3.4+ + Vite 5.0+
- **UI库**: Element Plus 2.4+ + @element-plus/icons-vue
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **HTTP**: Axios 1.6+
- **图表**: ECharts 5.4+ + vue-echarts 6.6+
- **工具**: Day.js 1.11+
- **样式**: Sass 1.70+
- **代码检查**: ESLint 8.56+

### 后端
- **框架**: FastAPI 0.109 + Uvicorn 0.27
- **数据库**: MySQL 8.0 + SQLAlchemy 2.0 + PyMySQL 1.1 + Alembic 1.13
- **缓存**: Redis 5.0（可选，支持降级到内存存储）
- **认证**: JWT (python-jose[cryptography]) + Passlib + Bcrypt
- **邮件**: FastAPI Mail 1.4
- **AI服务**:
  - 豆包录音文件识别模型 (volc.seedasr.auc)
  - OpenAI API (用于 RAG 问答)
  - LangChain 0.1 + ChromaDB 0.4 + sentence-transformers
- **工具**: httpx, aiofiles, python-docx, python-dotenv, pydantic-settings
- **部署**: Docker Compose (MySQL + 后端)

### 基础设施
- **容器化**: Docker Compose（MySQL 8.0 容器）
- **数据库迁移**: Alembic 1.13
- **向量数据库**: ChromaDB（用于 RAG 知识检索）

## 项目结构

```
SoulStation/
├── frontend/                   # 前端 Vue 项目
│   ├── src/
│   │   ├── api/               # API 接口封装
│   │   ├── assets/            # 静态资源
│   │   │   ├── images/        # 图片
│   │   │   ├── icons/         # 图标
│   │   │   └── styles/        # 样式文件
│   │   ├── components/        # 组件
│   │   │   ├── auth/          # 登录注册组件
│   │   │   ├── chat/          # 智能问答组件 (RAG)
│   │   │   ├── test/          # 心理测试组件
│   │   │   ├── profile/       # 个人中心组件
│   │   │   ├── consultation/  # 咨询预约组件
│   │   │   ├── dialogue/      # 咨询对话组件
│   │   │   ├── admin/         # 后台管理组件
│   │   │   ├── counselor/     # 咨询师相关组件
│   │   │   ├── public/        # 公共信息组件
│   │   │   ├── common/        # 通用组件
│   │   │   └── right-sidebar/ # 右侧边栏组件
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── utils/             # 工具函数
│   │   └── views/             # 页面视图
│   │       ├── auth/          # 登录注册页
│   │       ├── chat/          # 智能问答页
│   │       ├── test/          # 心理测试页
│   │       ├── profile/       # 个人中心页
│   │       ├── consultation/  # 咨询预约页
│   │       ├── dialogue/      # 咨询对话页
│   │       ├── counselor/     # 咨询师相关页
│   │       ├── knowledge/     # 知识库页
│   │       ├── notification/  # 通知页
│   │       ├── admin/         # 后台管理页
│   │       └── public/        # 公共信息页
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/                    # 后端 FastAPI 项目
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth/          # 登录注册
│   │   │   ├── chat/          # 智能问答 (RAG)
│   │   │   ├── test/          # 心理测试
│   │   │   ├── consultation/  # 咨询预约
│   │   │   ├── counselor/     # 咨询师
│   │   │   ├── knowledge/     # 知识库
│   │   │   ├── user/          # 用户
│   │   │   ├── notification/  # 通知
│   │   │   ├── admin/         # 后台管理
│   │   │   ├── dialogue/      # 咨询对话
│   │   │   ├── profile/       # 个人中心
│   │   │   └── public/        # 公共信息
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── security.py    # JWT 安全
│   │   │   ├── database.py    # 数据库连接
│   │   │   └── init_db.py     # 数据库初始化脚本
│   │   ├── models/            # SQLAlchemy 模型
│   │   │   ├── admin.py
│   │   │   ├── chat.py
│   │   │   ├── counselor.py
│   │   │   ├── knowledge.py
│   │   │   ├── notification.py
│   │   │   ├── test.py
│   │   │   └── user.py
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── consultation.py
│   │   │   ├── counselor.py
│   │   │   ├── knowledge.py
│   │   │   ├── notification.py
│   │   │   ├── test.py
│   │   │   └── user.py
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── auth/          # 认证子模块
│   │   │   ├── email/         # 邮件子模块
│   │   │   ├── rag/           # RAG 知识检索子模块
│   │   │   ├── storage/       # 文件存储子模块
│   │   │   ├── admin_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── counselor_service.py
│   │   │   ├── crisis_service.py
│   │   │   ├── knowledge_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── speech_service.py
│   │   │   ├── test_service.py
│   │   │   ├── user_service.py
│   │   │   ├── verification_service.py
│   │   │   └── verification_redis_service.py
│   │   └── main.py            # FastAPI 应用入口
│   ├── seeds/                 # 测试数据种子
│   ├── sql/                   # SQL 脚本
│   │   ├── init.sql
│   │   ├── seed_data.sql
│   │   ├── migrate.sql
│   │   └── insert_data.sql
│   ├── uploads/               # 上传文件目录
│   ├── send_appointment_reminders.py  # 预约提醒定时任务
│   ├── reset_user_password.py
│   ├── start.sh
│   ├── requirements.txt       # Python 依赖
│   ├── docker-compose.yml     # Docker Compose (MySQL + Redis)
│   ├── .env                   # 环境变量
│   └── README.md
│
├── database/                   # 数据库相关
│   ├── Psychology-10K-ZH.json # 心理学知识库 (10K+ 条)
│   ├── docs/                  # 数据库文档
│   │   ├── ER图.md
│   │   └── 表结构.md
│   ├── migrations/            # Alembic 迁移脚本
│   ├── seeds/                 # 种子数据
│   └── backups/               # 备份文件
│
├── docs/                       # 项目文档（平铺文件，无子目录）
│   ├── ...（设计文档、API 说明等）
│   ├── 项目结构分析报告.md
│   └── 项目周报.md
│
└── README.md                   # 项目说明（本文件）
```

## 数据库表

### 用户相关
- `users` - 用户表（普通用户/咨询师）
- `admins` - 管理员表

### 心理测试相关
- `psychological_tests` - 心理测试表
- `test_questions` - 测试题目表
- `test_results` - 测试结果表
- `test_progress` - 答题进度表

### 聊天相关
- `chat_dialogues` - 对话记录表
- `chat_messages` - 聊天消息表
- `chat_tags` - 对话标签表
- `chat_dialogue_tags` - 对话标签关联表

### 咨询师相关
- `counselors` - 咨询师表
- `appointments` - 预约订单表
- `consultation_reviews` - 咨询评价表
- `consultation_messages` - 咨询对话消息表

### 知识库相关
- `knowledge_articles` - 知识文章表
- `knowledge_comments` - 知识评论表
- `knowledge_favorites` - 知识收藏表
- `knowledge_likes` - 知识点赞表

### 通知相关
- `notifications` - 用户通知表

## 开发规范

### 接口命名规范
- 后端路由前缀: `/api`
- 各模块路由:
  - `/api/auth` - 登录注册
  - `/api/chat` - 智能问答 (RAG + 语音识别)
  - `/api/test` - 心理测试
  - `/api/consultation` - 咨询预约
  - `/api/counselor` - 咨询师管理（含入驻、资质审核、预约管理）
  - `/api/knowledge` - 知识库
  - `/api/user` - 用户管理
  - `/api/notification` - 消息通知
  - `/api/admin` - 后台管理

### 代码规范
- 前端组件命名: PascalCase
- 后端路由命名: snake_case
- 统一代码风格

## 模块说明

### 登录注册模块 (auth)
- 邮箱验证码发送
- 用户注册/登录
- 忘记密码
- JWT Token 认证

### 智能问答模块 (chat)
- **RAG 检索增强问答** - 基于知识库的智能回复
- **语音转文字** - 集成豆包语音识别API
- 对话记录管理
- 对话标签管理
- 流式/非流式响应支持

### 心理测试模块 (test)
- **9套专业心理测试**（共159题）
  - 焦虑自评量表 (SAS-20)
  - 抑郁自评量表 (SDS-20)
  - 大五人格简版量表 (BIG5-20)
  - 工作生活压力量表 (STRESS-20)
  - 自尊量表 (SES-10)
  - 社交焦虑量表 (LSAS-20)
  - 情绪稳定性量表 (ES-15)
  - 职业倦怠量表 (MBI-15)
  - 匹茨堡睡眠质量指数 (PSQI-19)
- 问卷查询与筛选
- 答题进度保存
- 结果计算与展示
- 测试统计分析

### 咨询预约模块 (consultation)
- 咨询师信息展示
- 预约订单管理
- 预约提醒邮件
- 咨询评价

### 咨询师管理 (counselor)
- 咨询师资质审核
- 咨询师档案管理
- 可预约时间管理
- 咨询统计

### 知识库模块 (knowledge)
- 心理知识文章展示
- 文章评论与点赞
- 文章收藏与分享
- 知识搜索与分类

### 咨询对话模块 (dialogue)
- 实时对话
- 消息轮询
- 对话历史记录
- 咨询结束处理

### 公共信息模块 (public)
- 公开信息展示接口
- 公共页面数据

### 消息通知模块 (notification)
- 站内消息推送
- 通知列表与已读管理
- 预约提醒通知
- 系统公告

### 后台管理模块 (admin)
- 咨询师资质审核
- 心理知识管理
- 用户/订单管控
- 数据统计分析
- 系统配置管理

### 用户管理模块 (user)
- 用户信息管理
- 隐私设置
- 数据统计汇总
- 个人中心

## 快速开始

### 前置要求
- Node.js 16+
- Python 3.8+
- MySQL 5.7+ / MariaDB 10.3+
- Redis（可选，用于缓存）

### 1. 克隆项目
```bash
git clone <repository-url>
cd SoulStation
```

### 2. 数据库配置

#### 创建数据库
```bash
mysql -u root -p -e "CREATE DATABASE soulstation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

#### 配置环境变量

项目根目录 `backend/.env` 已预置默认配置，根据需要修改：
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/soulstation
SECRET_KEY=your-secret-key-here
# ... 其他配置
```

#### 初始化数据库
```bash
# 进入 backend 目录执行
cd backend
python -m app.core.init_db
```

这将自动创建所有表并初始化测试数据（9套心理测试，159道题目）。

### 3. 后端启动
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 5. 访问应用
- 前端地址: http://localhost:5173
- API文档: http://localhost:8000/docs
- 后台管理: http://localhost:5173/admin

### 默认账号

#### 🔑 管理员账号
```
邮箱/用户名: admin@soulstation.com 
密码: admin123
角色: 超级管理员
登录入口: http://localhost:5173/login
```
- 登录后自动跳转到管理后台
- 拥有所有管理权限
- **可以使用邮箱 `admin@soulstation.com` 或用户名 `admin` 登录**

#### 👥 普通用户账号

**测试用户1:**
```
邮箱: test@example.com
密码: 123456
昵称: 测试用户
```

**测试用户2:**
```
邮箱: user1@example.com
密码: 123456
昵称: 张三
```

**测试用户3:**
```
邮箱: user2@example.com
密码: 123456
昵称: 李四
```

**测试用户4:**
```
邮箱: user3@example.com
密码: 123456
昵称: 王五
```

**测试用户5 (焦虑测试):**
```
邮箱: anxiety@test.com
密码: 123456
昵称: 小明同学
```

**测试用户6 (抑郁测试):**
```
邮箱: depression@test.com
密码: 123456
昵称: 小红同学
```

#### 👨‍⚕️ 咨询师账号

每个咨询师都有独立的登录账号，登录后会根据角色自动跳转到咨询师工作台。

**咨询师1 - 王静怡 (焦虑与抑郁/青少年心理)**
```
邮箱: counselor1@soulstation.com
密码: 123456
专长: 焦虑与抑郁、青少年心理、情绪管理
职称: 国家二级心理咨询师
从业年限: 8年
```

**咨询师2 - 李明远 (婚姻家庭/职场压力)**
```
邮箱: counselor2@soulstation.com
密码: 123456
专长: 婚姻家庭、职场压力、个人成长
职称: 资深心理治疗师
从业年限: 12年
```

**咨询师3 - 张雅婷 (儿童心理/亲子关系)**
```
邮箱: counselor3@soulstation.com
密码: 123456
专长: 儿童心理、学习障碍、亲子关系
职称: 儿童心理专家
从业年限: 10年
```

**咨询师4 - 赵晓敏 (情绪管理/创伤疗愈)**
```
邮箱: counselor4@soulstation.com
密码: 123456
专长: 抑郁与焦虑、情绪障碍、创伤疗愈
职称: 情绪管理专家
从业年限: 6年
```

**咨询师5 - 陈建国 (成瘾行为/强迫症)**
```
邮箱: counselor5@soulstation.com
密码: 123456
专长: 成瘾行为、强迫症、睡眠障碍
职称: 成瘾心理专家
从业年限: 15年
```

**咨询师6 - 刘思雨 (婚恋情感/亲密关系)**
```
邮箱: counselor6@soulstation.com
密码: 123456
专长: 婚恋情感、失恋疗愈、亲密关系
职称: 婚恋情感专家
从业年限: 7年
```

⚠️ **重要提示**:
1. 所有测试账号的默认密码均为 `123456`（管理员为 `admin123`）
2. 首次登录后建议修改默认密码
3. 所有角色使用统一的登录入口：`http://localhost:5173/login`
4. 系统会根据用户角色自动跳转到对应页面（管理员→后台，咨询师→工作台，用户→首页）

## 高级配置

### 语音识别功能

项目已集成豆包语音识别API，支持语音转文字功能。

**配置步骤**：

1. 获取豆包API密钥
   - 访问[火山引擎控制台](https://console.volcengine.com/)
   - 开通"语音技术-音频自训练"服务
   - 获取 API Key

2. 配置后端环境变量（已在上面步骤中说明）

3. 配置公网URL（开发环境）
   - 语音识别需要公网可访问的音频URL
   - 开发环境使用内网穿透工具（ngrok、CloudFlare Tunnel等）配置公网URL

**使用说明**：
- 进入聊天页面点击麦克风按钮
- 允许浏览器访问麦克风
- 开始录音（最长60秒）
- 自动识别并填充到输入框

本模块的完整实现细节请参考后端 `app/services/speech_service.py`。

### 定时任务

项目包含预约提醒邮件定时任务：

```bash
# Linux/Mac (crontab)
*/10 * * * * cd /path/to/SoulStation/backend && python send_appointment_reminders.py

# Windows (任务计划程序)
# 创建基本任务，每10分钟运行一次
python C:\path\to\SoulStation\backend\send_appointment_reminders.py
```

## 常见问题

### 1. 数据库连接失败？
- 检查MySQL服务是否启动
- 确认 `.env` 文件中数据库配置正确
- 确保数据库已创建

### 2. 语音识别不工作？
- 确保配置了 `DOUBAO_API_KEY`
- 开发环境需要配置 `PUBLIC_URL`（使用内网穿透）
- 参考后端 `app/services/speech_service.py` 中的实现

### 3. 邮件发送失败？
- 检查 `.env` 中的邮件配置
- 某些邮箱需要开启"应用专用密码"
- 确认网络连接正常

### 4. 前端API请求失败？
- 确保后端服务正在运行（http://localhost:8000）
- 检查 `frontend/.env` 中的 `VITE_API_BASE_URL` 配置
- 查看浏览器控制台错误信息


## 技术支持

如有问题或建议，请：
- 提交 Issue
- 查看项目文档
- 联系开发团队

## 许可证

MIT License
